from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import sqlite3
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'Student_grading_system_database.db')

# Helper function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # This allows fetching results as dictionaries
    return conn

#####API 1
# Route to get a random trivia question from the8 database
@app.route('/Student_Grades', methods=['GET'])
def get_Student_db():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
   
    # Fetch all trivia questions from the database
    cursor.execute("""SELECT student.Name, grades.Marks,student.Class,student.Age,student.ID  FROM student INNER JOIN grades ON student.ID = grades.Student_ID""")
    list = cursor.fetchall()
   
    # Close the database connection
    conn.close()
   
    if list:
        # Select a random trivia question from the list
        found = random.choice(list)
        return jsonify({"Name": found["Name"],"Grade" : found["Marks"], "Class" : found["Class"], "age" : found["Age"], "Identification" : found["ID"]})
    else:
        return jsonify({"error": "No data found in the database."}), 404
 
#API 2
# Route to get trivia for a specific superhero
@app.route('/Student_Grade/<Student_name>', methods=['GET'])
def get_grades_for_Student(Student_name):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
   
    # Fetch trivia for the specified superhero
    cursor.execute("""SELECT student.Name, grades.Marks,student.Class,student.Age,student.ID  FROM student INNER JOIN grades ON student.ID = grades.Student_ID WHERE Name = ?""", (Student_name,))
    list = cursor.fetchone()
   
    # Close the database connection
    conn.close()
   
    if list:
        return jsonify({"Name": list["Name"], "Grade": list["Marks"], "Class": list["Class"], "age" : list["Age"], "Identification" : list["ID"]})
    else:
        return jsonify({"error": f"No data found for student '{Student_name}'."}), 404
 
 
#API 3
# Route to add a new trivia entry to the database
@app.route('/addStudent', methods=['POST'])
def add_student():
    data = request.get_json()  # Get the JSON data from the request
   
    # Validate the JSON data
    if not data or 'Name' not in data or 'Marks' not in data or 'Class' not in data or 'Age' not in data or 'Subject' not in data:
        return jsonify({"error": "Invalid data. 'Name', 'Marks', 'Class', 'Age', and 'Subject' are required fields."}), 400
   
    Name = data['Name']
    Grade = data['Marks']
    Class = data['Class']
    Age = data['Age']
    Subject = data['Subject']
    Class_ID = data['Class_ID']
    Teacher_ID = data['Teacher_ID']
    Identification = data['ID']
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
   
    # Insert the new trivia into the database
   # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
   
    # 1. Insert the student (Fixed your parameter swapping bug here too!)
    cursor.execute("INSERT INTO Student (Name,ID, Age, Class) VALUES (?,?,?,?)", (Name, Age, Class,Identification))
    
    # 2. Get the Student_ID that the database just automatically generated
    student_id = cursor.lastrowid  # For SQLite / MySQL
    # Note: If using PostgreSQL, use cursor.fetchone()[0] after adding "RETURNING Student_ID" to your SQL string
   
    # 3. Insert the grades AND pass the new student_id into the Student_ID foreign key column
    cursor.execute("INSERT INTO Grades (Marks, Subject, Student_ID) VALUES (?,?,?)", (Grade, Subject, student_id))

    cursor.execute("INSERT INTO Class (Class_ID, Teacher_Id, Subject, Student_ID) VALUES (?,?,?,?)", (Class_ID, Teacher_ID, Subject, student_id))
    
    conn.commit()  # Save changes to both tables
    conn.close()

   
    return jsonify({"message": "New Student added successfully!"}), 201
 
 
#API - 4
# New route to update trivia for a specific superhero
@app.route('/updateGrades/<Student_name>', methods=['PUT'])
def update_grades_for_student(Student_name):
    data = request.get_json()
   
    # Validate the input data
    if not data or 'Name' not in data or 'Grades' not in data:
        return jsonify({"error": "Invalid data. 'Name' and 'Marks' are required fields."}), 400
   
    Name = data['Name']
    Grade = data['Marks']
 
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
 
    # Update trivia for the specified superhero
    cursor.execute("UPDATE Grades SET Name = ?, Grades = ? WHERE ID = ?", (Name, Grade, Student_name))
    rows_updated = cursor.rowcount  # Get the number of rows updated
    conn.commit()  # Save changes
    conn.close()
   
    if rows_updated > 0:
        return jsonify({"message": f"Updated DATA for '{Student_name}'", "rows_updated": rows_updated}), 200
    else:
        return jsonify({"error": f"No data found for Student '{Student_name}'."}), 404


@app.route('/Classes', methods=['POST'])
def get_Classes_db():
    data = request.get_json()
    
    # FIX 1: Correctly check if 'Teacher_ID' is NOT inside the data payload
    if not data or 'Teacher_ID' not in data:
        return jsonify({"error": "Invalid data. 'Teacher_ID' is required."}), 400

    Teacher_ID = data["Teacher_ID"]
    
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # FIX 2: Added trailing comma (Teacher_ID,) to make it a tuple so SQL executes safely
    cursor.execute("""SELECT Subject FROM Class WHERE Teacher_ID = ?""", (Teacher_ID,))
    db_rows = cursor.fetchall()
   
    # Close the database connection
    conn.close()
   
    if db_rows:
        # FIX 3: Safely extract values instead of indexing by ID number 
        # Converts list of row structures into a clean text list of subjects
        subjects = [row[0] for row in db_rows]
        
        return jsonify({
            "Teacher_ID": Teacher_ID,
            "Subjects": subjects
        })
    else:
        return jsonify({"error": "No data found for this Teacher ID in the database."}), 404


@app.route('/delete_Student', methods=['POST'])
def delete_student():
    data = request.get_json()  # Get the JSON data from the request
   
    # Validate the JSON data
    if not data or 'Name' not in data or 'ID' not in data or 'Marks' not in data or 'Class' not in data or 'Age' not in data or 'Subject' not in data or 'Class_ID' not in data or 'Teacher_ID' not in data:
        return jsonify({"error": "Invalid data. 'Name', 'Marks', 'Class', 'Age', and 'Subject' are required fields."}), 400
   
    Name = data['Name']
    Identification = data['ID']
    Class = data['Class']
    Age = data['Age']
    Subject = data['Subject']
    Grade = data['Marks']
    Class_ID = data['Class_ID']
    Teacher_ID = data['Teacher_ID']
    
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
   
    # Insert the new trivia into the database
   # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
   
    # 1. Insert the student (Fixed your parameter swapping bug here too!)
    cursor.execute("DELETE FROM Student WHERE ID = ? ", (Identification,))
    
    # 2. Get the Student_ID that the database just automatically generated
    student_id = cursor.lastrowid  # For SQLite / MySQL
    # Note: If using PostgreSQL, use cursor.fetchone()[0] after adding "RETURNING Student_ID" to your SQL string
   
    # 3. Insert the grades AND pass the new student_id into the Student_ID foreign key column
    cursor.execute("DELETE FROM grades WHERE Student_ID = ? ", (Identification,))

    cursor.execute("DELETE FROM class WHERE Student_ID = ? ", (Identification,))
    
    conn.commit()  # Save changes to both tables
    conn.close()

   
    return jsonify({"message": "Student deleted successfully!"}), 201


@app.route('/Get_Student/<Student_name>', methods=['GET'])
def get_Student(Student_name):
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
   
    # Fetch trivia for the specified superhero
    cursor.execute("""SELECT * FROM student WHERE Name = ?""", (Student_name,))
    list = cursor.fetchone()
   
    # Close the database connection
    conn.close()
   
    if list:
        return jsonify({"Identification" : list["ID"], "Name": list["Name"], "Class": list["Class"], "age" : list["Age"]})
    else:
        return jsonify({"error": f"No data found for student '{Student_name}'."}), 404
 



# Quiz mode endpoint
@app.route('/quiz', methods=['GET', 'POST'])
def quiz_mode():
    if request.method == 'GET':
        # TODO: Connect to the database and fetch a list of trivia questions
        # conn = (Connect to the database)
        # cursor = (Create a cursor from the connection)
        # cursor.execute("SELECT * FROM trivia")  # Query to fetch trivia questions
        # trivia_list = (Fetch all trivia questions)
        # conn.close()  # Close the database connection

        # TODO: Check if trivia_list contains questions
        # if trivia_list:
            # TODO: Select a random trivia question and return it as JSON (excluding the answer)
            # trivia = (Select a random trivia item from trivia_list)
            # return jsonify({"Superhero": (Superhero name), "Question": (Question text)})
        # else:
            # TODO: Return a 404 error if no trivia is found in the database
            # return jsonify({"error": "No trivia found in the database."}), 404
        print()

    elif request.method == 'POST':
        # TODO: Retrieve JSON data from the request
        # data = (Get JSON data from the request)
        # hero = (Extract 'hero' from data)
        # user_answer = (Extract 'answer' from data)

        # TODO: Validate that both 'hero' and 'answer' fields are present
        # if (Check if hero or user_answer is missing):
            # return jsonify({"error": "Hero and answer are required fields."}), 400

        # TODO: Connect to the database and fetch the correct answer for the given hero
        # conn = (Connect to the database)
        # cursor = (Create a cursor from the connection)
        # cursor.execute("SELECT * FROM trivia WHERE hero = ?", (hero,))
        # trivia = (Fetch one trivia item for the specified hero)
        # conn.close()  # Close the database connection

        # TODO: Check if trivia is found for the given hero
        # if trivia:
            # correct_answer = (Retrieve correct answer from trivia item)
            # TODO: Compare the user's answer to the correct answer (case insensitive)
            # if (User answer matches correct answer):
                # return jsonify({"result": "Correct!", "correct_answer": correct_answer})
            # else:
                # return jsonify({"result": "Incorrect", "correct_answer": correct_answer})
        # else:
            # TODO: Return a 404 error if no trivia is found for the specified hero
            # return jsonify({"error": f"No trivia found for superhero '{hero}'."}), 404
            print()



# Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555)
