from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    Response
)
import mysql.connector

# =========================
# FLASK APP
# =========================

app = Flask(__name__)

app.secret_key = "student_management_2026_secure_project_key"

# =========================
# MYSQL CONNECTION
# =========================

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootanjali123",   # Your MySQL password
    database="student_management"
)

cursor = conn.cursor(
    dictionary=True
)

# =========================
# LOGIN PAGE
# =========================

@app.route('/')
def home():

    return render_template(
        'login.html'
    )

# =========================
# LOGIN VALIDATION
# =========================

@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    cursor.execute(
        """
        SELECT *
        FROM admin
        WHERE username=%s
        AND password=%s
        """,
        (username, password)
    )

    user = cursor.fetchone()

    if user:
        session['user'] = username
        return redirect('/dashboard')

    else:

        return """
        <h2 style='color:red;text-align:center;'>
        Invalid Username or Password
        </h2>
        """

# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    cursor.execute("""
    SELECT COUNT(*) AS total_students
    FROM students
    """)
    total_students = cursor.fetchone()['total_students']

    cursor.execute("""
    SELECT COUNT(*) AS male_students
    FROM students
    WHERE gender='Male'
    """)
    male_students = cursor.fetchone()['male_students']

    cursor.execute("""
    SELECT COUNT(*) AS female_students
    FROM students
    WHERE gender='Female'
    """)
    female_students = cursor.fetchone()['female_students']

    cursor.execute("""
    SELECT COUNT(DISTINCT department) AS departments
    FROM students
    """)
    departments = cursor.fetchone()['departments']

    return render_template(
        'dashboard.html',
        total_students=total_students,
        male_students=male_students,
        female_students=female_students,
        departments=departments
    )
# =========================
# ADD STUDENT PAGE
# =========================

@app.route('/add_student')
def add_student():

    if 'user' not in session:
        return redirect('/')

    return render_template(
        'add_student.html'
    )

# =========================
# SAVE STUDENT
# =========================

@app.route('/save_student', methods=['POST'])
def save_student():

    student_id = request.form['student_id']
    student_name = request.form['student_name']
    gender = request.form['gender']
    course = request.form['course']
    department = request.form['department']
    mobile = request.form['mobile']
    email = request.form['email']
    address = request.form['address']

    cursor.execute(
        """
        INSERT INTO students
        (
            student_id,
            student_name,
            gender,
            course,
            department,
            mobile,
            email,
            address
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            student_id,
            student_name,
            gender,
            course,
            department,
            mobile,
            email,
            address
        )
    )

    conn.commit()

    return redirect('/student_list')

# =========================
# STUDENT LIST
# =========================

@app.route('/student_list')
def student_list():

    if 'user' not in session:
        return redirect('/')

    cursor.execute("""
    SELECT *
    FROM students
    ORDER BY id DESC
    """)

    students = cursor.fetchall()

    return render_template(
        'student_list.html',
        students=students
    )
# =========================
# RUN APP
# =========================
# =========================
# REPORTS PAGE
# =========================

@app.route('/reports')
def reports():

    if 'user' not in session:
        return redirect('/')

    # Total Students

    cursor.execute("""
    SELECT COUNT(*) AS total_students
    FROM students
    """)

    total_students = cursor.fetchone()['total_students']

    # Male Students

    cursor.execute("""
    SELECT COUNT(*) AS male_students
    FROM students
    WHERE gender='Male'
    """)

    male_students = cursor.fetchone()['male_students']

    # Female Students

    cursor.execute("""
    SELECT COUNT(*) AS female_students
    FROM students
    WHERE gender='Female'
    """)

    female_students = cursor.fetchone()['female_students']

    # Department Statistics

    cursor.execute("""
    SELECT
    department,
    COUNT(*) AS total
    FROM students
    GROUP BY department
    """)

    dept_stats = cursor.fetchall()

    # Student Records

    cursor.execute("""
    SELECT *
    FROM students
    ORDER BY id DESC
    """)

    students = cursor.fetchall()

    return render_template(
        "reports.html",
        total_students=total_students,
        male_students=male_students,
        female_students=female_students,
        dept_stats=dept_stats,
        students=students
    )
@app.route('/edit_student/<int:id>')
def edit_student(id):

    if 'user' not in session:
        return redirect('/')

    cursor.execute(
        "SELECT * FROM students WHERE id=%s",
        (id,)
    )

    student = cursor.fetchone()

    return render_template(
        'edit_student.html',
        student=student
    )
@app.route('/update_student/<int:id>', methods=['POST'])
def update_student(id):

    if 'user' not in session:
        return redirect('/')

    student_id = request.form['student_id']
    student_name = request.form['student_name']
    gender = request.form['gender']
    course = request.form['course']
    department = request.form['department']
    mobile = request.form['mobile']
    email = request.form['email']
    address = request.form['address']

    cursor.execute("""
    UPDATE students
    SET
    student_id=%s,
    student_name=%s,
    gender=%s,
    course=%s,
    department=%s,
    mobile=%s,
    email=%s,
    address=%s
    WHERE id=%s
    """,
    (
    student_id,
    student_name,
    gender,
    course,
    department,
    mobile,
    email,
    address,
    id
    ))

    conn.commit()

    return redirect('/student_list')
@app.route('/delete_student/<int:id>')
def delete_student(id):

    cursor.execute(
    "DELETE FROM students WHERE id=%s",
    (id,)
    )

    conn.commit()

    return redirect('/student_list')
@app.route('/search_student')
def search_student():

    keyword = request.args.get('keyword')

    cursor.execute("""
    SELECT *
    FROM students
    WHERE
    student_name LIKE %s
    OR department LIKE %s
    OR course LIKE %s
    """,
    (
    f"%{keyword}%",
    f"%{keyword}%",
    f"%{keyword}%"
    ))

    students = cursor.fetchall()

    return render_template(
        "student_list.html",
        students=students
    )
@app.route('/export_csv')
def export_csv():

    cursor.execute("""
    SELECT *
    FROM students
    """)

    students = cursor.fetchall()

    def generate():

        data = []

        data.append([
        'Student ID',
        'Name',
        'Gender',
        'Course',
        'Department',
        'Mobile',
        'Email',
        'Address'
        ])

        for row in students:

            data.append([
            row['student_id'],
            row['student_name'],
            row['gender'],
            row['course'],
            row['department'],
            row['mobile'],
            row['email'],
            row['address']
            ])

        for item in data:

            yield ','.join(
                map(str,item)
            ) + '\n'

    return Response(
        generate(),
        mimetype='text/csv',
        headers={
        'Content-Disposition':
        'attachment; filename=students.csv'
        }
    )
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':

    app.run(
        debug=True
    )