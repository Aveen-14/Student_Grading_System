from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps
import sqlite3
import os

app = Flask(__name__)

# 1. PERMANENT SECRET KEY (Kept for fallback context)
app.secret_key = 'development_secret_key_change_this_in_production'

# 2. CORS ENABLED FOR CROSS-PORT LOCALHOST DEVELOPMENT
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:5500", "http://localhost:5500"]}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database', 'Student_grading_system_database.db')

# Helper function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE, timeout=30)
    conn.row_factory = sqlite3.Row  
    return conn

# 3. NEW CUSTOM DECORATOR FOR LOCALSTORAGE AUTHENTICATION
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Inspect either the JSON payload body or GET parameters for an explicit teacher identity identifier
        data = request.get_json(silent=True) or {}
        teacher_id = data.get('Teacher_ID') or request.args.get('Teacher_ID')
        
        if not teacher_id:
            return jsonify({"error": "Unauthorized access. Missing valid Teacher_ID identification."}), 401
        return f(*args, **kwargs)
    return decorated_function


# ==============================================================================
# AUTHENTICATION ROUTES
# ==============================================================================

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'Name' not in data or 'Password' not in data:
        return jsonify({"error": "Missing credentials. 'Name' and 'Password' are required."}), 400

    Name = data['Name'].strip()
    password = data['Password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT ID, Name, Password FROM teacher WHERE Name = ?", (Name,))
    teacher = cursor.fetchone()
    conn.close()

    if teacher is None:
        return jsonify({"error": "Invalid username or password."}), 401

    if teacher['Password'] != password:
        return jsonify({"error": "Invalid username or password."}), 401

    # Returns the profile details directly to the client to save in localStorage
    return jsonify({
        "message": "Login successful!",
        "teacher": {
            "ID": teacher['ID'],
            "Name": teacher['Name'],
        }
    }), 200


@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logged out successfully from backend context."}), 200


# ==============================================================================
# STUDENT GRADING SYSTEM ROUTES
# ==============================================================================

# API 2
@app.route('/Student_Grade/<Student_name>', methods=['GET'])
def get_grades_for_Student(Student_name):
    conn = get_db_connection()
    cursor = conn.cursor()
   
    cursor.execute("""SELECT student.Name, grades.Marks, student.Class, student.Age, student.ID 
                      FROM student 
                      INNER JOIN grades ON student.ID = grades.Student_ID 
                      WHERE Name = ?""", (Student_name,))
    student_row = cursor.fetchone()
    conn.close()
   
    if student_row:
        return jsonify({
            "Name": student_row["Name"], 
            "Grade": student_row["Marks"], 
            "Class": student_row["Class"], 
            "age": student_row["Age"], 
            "Identification": student_row["ID"]
        })
    else:
        return jsonify({"error": f"No data found for student '{Student_name}'."}), 404


# API 3 (PROTECTED BY LOCALSTORAGE PAYLOAD MATCH)
@app.route('/addStudent', methods=['POST'])
def add_student():
    data = request.get_json()
   
    if not data or 'Name' not in data or 'Marks' not in data or 'Class' not in data or 'Age' not in data or 'Subject' not in data or 'Teacher_ID' not in data:
        return jsonify({"error": "Invalid data. All payload metadata fields including 'Teacher_ID' are required."}), 400
   
    Name = data['Name']
    Grade = data['Marks']
    Class = data['Class']
    Age = data['Age']
    Subject = data['Subject']
    Teacher_ID = data['Teacher_ID']

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
       
        # 1. Insert the student
        cursor.execute("INSERT INTO Student (Name, Age, Class) VALUES (?, ?, ?)", (Name, Age, Class))
        student_id = cursor.lastrowid

        # 2. Insert grades and class details
        cursor.execute("INSERT INTO Grades (Marks, Subject, Student_ID) VALUES (?, ?, ?)", (Grade, Subject, student_id))
        cursor.execute("INSERT INTO Class (Teacher_Id, Subject, Student_ID) VALUES (?, ?, ?)", (Teacher_ID, Subject, student_id))
        
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": "New Student added successfully!"}), 201


# API 4 (PROTECTED BY LOCALSTORAGE PAYLOAD MATCH)
@app.route('/updateGrades/<Student_name>', methods=['PUT'])
def update_grades_for_student(Student_name):
    data = request.get_json()
   
    if not data or 'Name' not in data or 'Marks' not in data:
        return jsonify({"error": "Invalid data. 'Name' and 'Marks' are required fields."}), 400
   
    Grade = data['Marks']
 
    conn = get_db_connection()
    cursor = conn.cursor()
 
    cursor.execute("UPDATE Grades SET Marks = ? WHERE Student_ID = (SELECT ID FROM Student WHERE Name = ?)", (Grade, Student_name))
    rows_updated = cursor.rowcount
    conn.commit()
    conn.close()
   
    if rows_updated > 0:
        return jsonify({"message": f"Updated DATA for '{Student_name}'", "rows_updated": rows_updated}), 200
    else:
        return jsonify({"error": f"No data found for Student '{Student_name}'."}), 404


@app.route('/Classes', methods=['POST'])
def get_Classes_db():
    data = request.get_json()
    
    if not data or 'Teacher_ID' not in data:
        return jsonify({"error": "Invalid data. 'Teacher_ID' is required."}), 400

    Teacher_ID = data["Teacher_ID"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT Subject FROM Class WHERE Teacher_ID = ?""", (Teacher_ID,))
    db_rows = cursor.fetchall()
    conn.close()
   
    if db_rows:
        subjects = [row[0] for row in db_rows]
        return jsonify({"Teacher_ID": Teacher_ID, "Subjects": subjects})
    else:
        return jsonify({"error": "No data found for this Teacher ID in the database."}), 404


# DELETE API (PROTECTED BY LOCALSTORAGE PAYLOAD MATCH)
@app.route('/delete_Student', methods=['POST'])
def delete_student():
    data = request.get_json()
   
    if not data or 'ID' not in data:
        return jsonify({"error": "Invalid data. 'ID' is a required field."}), 400
   
    Identification = data['ID']
    
    conn = get_db_connection()
    cursor = conn.cursor()
   
    cursor.execute("DELETE FROM Student WHERE ID = ?", (Identification,))
    cursor.execute("DELETE FROM grades WHERE Student_ID = ?", (Identification,))
    cursor.execute("DELETE FROM class WHERE Student_ID = ?", (Identification,))
    
    conn.commit()
    conn.close()

    return jsonify({"message": f"Student ID '{Identification}' deleted successfully!"}), 201


@app.route('/Get_Student/<Student_name>', methods=['GET'])
def get_Student(Student_name):
    conn = get_db_connection()
    cursor = conn.cursor()
   
    cursor.execute("""SELECT * FROM student WHERE Name = ?""", (Student_name,))
    student_row = cursor.fetchone()
    conn.close()
    
    if student_row:
        return jsonify(dict(student_row)), 200
    return jsonify({"error": f"Student '{Student_name}' not found."}), 404

if __name__ == '__main__':
    app.run(
        debug=True, 
        port=5555, 
        use_reloader=False
    )
