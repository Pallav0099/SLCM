from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "secret_key123"
app.permanent_session_lifetime = timedelta(days=1)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='pallav',
            password='damnboi',
            database='students_db'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        sid = request.form['sid']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        dob = request.form['dob']
        phone_number = request.form['phone_number']
        gender = request.form['gender']
        enrollment_date = request.form['enrollment_date']
        address = request.form['address']
        branch = request.form['branch']
        section = request.form['section']
        semester = request.form['semester']

        if not sid.isalnum():
            flash('Student ID must be alphanumeric.', 'danger')
            return render_template('register.html')
        if not phone_number.isdigit() or len(phone_number) != 10:
            flash('Invalid phone number. Must be 10 digits.', 'danger')
            return render_template('register.html')
        if gender not in ['Male', 'Female', 'Other']:
            flash('Invalid gender selection.', 'danger')
            return render_template('register.html')
        if not semester.isdigit():
            flash('Semester Value MUST be an integer.', 'danger')
            return render_template('register.html')

        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed!', 'danger')
            return render_template('register.html')

        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO students 
                (sid, password, email, name, dob, phone_number, gender, enrollment_date, address, branch, section, semester) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (sid, password, email, name, dob, phone_number, gender, enrollment_date, address, branch, section, semester)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            print(f"Database Insert Error: {err}")
            flash('Registration failed due to a database error.', 'danger')
            return render_template('register.html')
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        sid = request.form['sid']
        password = request.form['password']
        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed!', 'danger')
            return render_template('login_page.html')

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM students WHERE sid = %s AND password = %s", (sid, password))
            student = cursor.fetchone()

            if student:
                session.permanent = True
                session['user'] = sid
                session['sid'] = student['sid']
                session['name'] = student['name']
                session['email'] = student['email']
                session['dob'] = student.get('dob')
                session['gender'] = student.get('gender')
                session['enrollment_date'] = student.get('enrollment_date')
                session['phone_number'] = student.get('phone_number')
                session['address'] = student.get('address')
                session['branch'] = student.get('branch')
                session['section'] = student.get('section')
                session['semester'] = student.get('semester')
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Login failed. Incorrect registration number or password.', 'danger')
                return render_template('login_page.html')
        except mysql.connector.Error as err:
            print(f"Database Query Error: {err}")
            flash('Login failed due to a database error.', 'danger')
            return render_template('login_page.html')
        finally:
            cursor.close()
            conn.close()

    return render_template('login_page.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/campusplacement.html')
def campusplacement():
    return render_template('campusplacement.html')

@app.route('/clubs.html')
def clubs():
    return render_template('clubs.html')

@app.route('/oniros.html')
def oniros():
    return render_template('oniros.html')

@app.route('/logout')
def logout():
    session.pop("user", None)
    flash(f"Logout successful!")
    return redirect(url_for('login'))

@app.route('/student', methods=['GET', 'POST'])
def student():
    if 'user' in session:
        sid = session['sid'] #square bracket because I'm assuming sid will exist in every register attempt.
        name = session.get('name', 'N/A')
        email = session.get('email', 'N/A')
        dob = session.get('dob', 'N/A') #small bracket because I'm assuming it may or may not be there.
        gender = session.get('gender', 'N/A')
        enrollment_date = session.get('enrollment_date', 'N/A')
        phone_number = session.get('phone_number', 'N/A')
        address = session.get('address', 'N/A')
        branch = session.get('branch', 'N/A')
        section = session.get('section', 'N/A')
        semester = session.get('semester', 'N/A')


        return render_template(
            'student.html',
            sid=sid,
            name=name,
            email=email,
            dob=dob,
            gender=gender,
            enrollment_date=enrollment_date,
            phone_number=phone_number,
            address=address,
            branch=branch,
            section=section,
            semester=semester
        )
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login'))

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user' in session:
        sid = session['sid']
        password = phone_number = address = semester = None  # Initialize the variables
        if request.method == 'POST':
            password = request.form.get('password', '')
            phone_number = request.form.get('phone_number', '')
            address = request.form.get('address', '')
            semester = request.form.get('semester', '')
            sid = session.get('sid')

        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed!', 'danger')
            return redirect(url_for('dashboard'))

        cursor = conn.cursor()
        
        # Initialize fields to hold the values for update, only if they're not empty
        update_fields = []
        update_values = []
        
        if password:
            update_fields.append("password = %s")
            update_values.append(password)
        if phone_number:
            update_fields.append("phone_number = %s")
            update_values.append(phone_number)
        if address:
            update_fields.append("address = %s")
            update_values.append(address)
        if semester:
            update_fields.append("semester = %s")
            update_values.append(semester)

        if update_fields:
            query = f"""
                UPDATE students
                SET {', '.join(update_fields)}
                WHERE sid = %s
            """
            update_values.append(sid)
            
            try:
                cursor.execute(query, tuple(update_values))
                conn.commit()
                flash('Profile updated successfully!', 'success')
            except mysql.connector.Error as err:
                print(f"Database Update Error: {err}")
                flash('Profile update failed due to a database error.', 'danger')
        else:
            flash('No fields were updated.', 'warning')
            return render_template('update_profile.html')
        return redirect(url_for('dashboard'))

@app.route('/pick_elective_courses', methods=['GET', 'POST'])
def pick_elective_courses():
    if 'sid' in session:
        sid = session.get('sid')

        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed!', 'danger')
            return redirect(url_for('dashboard'))

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM student_elective_courses WHERE sid = %s", (sid,))
        result = cursor.fetchall()

        if result:
            flash('You have already selected your elective courses. Changes are not allowed.', 'danger')
            return redirect(url_for('courses'))

        if request.method == 'POST':
            flexi_core_2 = request.form.get('flexi_core_2', '')
            program_elective_1 = request.form.get('program_elective_1', '')

            if not flexi_core_2 or not program_elective_1:
                flash('Both elective courses must be selected.', 'warning')
                return render_template('pick_elective_courses.html')

            flexi_core_2_data = flexi_core_2.split(',')
            program_elective_1_data = program_elective_1.split(',')

            try:
                query = """
                    INSERT INTO student_elective_courses (sid, category, course_id, course_name)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (sid, flexi_core_2_data[0], flexi_core_2_data[1], flexi_core_2_data[2]))
                cursor.execute(query, (sid, program_elective_1_data[0], program_elective_1_data[1], program_elective_1_data[2]))
                conn.commit()
                flash('Elective courses selected successfully!', 'success')
            except mysql.connector.Error as err:
                print(f"Database Insert Error: {err}")
                flash('Failed to select elective courses due to a database error.', 'danger')
                conn.rollback()

        return redirect(url_for('courses'))

    flash('Unauthorized access. Please log in.', 'danger')
    return redirect(url_for('login'))


@app.route('/courses', methods=['GET', 'POST'])
def courses():
    if 'user' in session:
        branch = session.get('branch', 'N/A')
        semester = session.get('semester', 'N/A')
        sid = session.get('sid', None)

        if branch == 'N/A' or semester == 'N/A' or not sid:
            flash('Profile details are missing. Please update your profile.', 'danger')
            return redirect(url_for('dashboard'))

        conn = get_db_connection()
        if conn is None:
            flash('Database connection failed!', 'danger')
            return redirect(url_for('dashboard'))

        cursor = conn.cursor(dictionary=True)
        try:
            # Query for mandatory courses
            core_courses_query = "SELECT cid, course_name, credits FROM courses WHERE branch = %s AND semester = %s"
            cursor.execute(core_courses_query, (branch, semester))
            courses = cursor.fetchall()

            # Query for elective courses
            elective_courses_query = "SELECT course_id, course_name, credits, category FROM student_elective_courses WHERE sid = %s"
            cursor.execute(elective_courses_query, (sid,))
            student_elective_courses = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Database Query Error: {err}")
            flash('Unable to fetch courses due to a database error.', 'danger')
            return redirect(url_for('dashboard'))
        finally:
            cursor.close()
            conn.close()

        return render_template('courses.html', courses=courses, student_elective_courses=student_elective_courses)
    else:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
