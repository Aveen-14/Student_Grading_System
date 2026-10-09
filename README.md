# Student Grading System Backend

A lightweight **Flask REST API** driving a Student Grading System, utilizing raw **SQLite3** queries and custom **payload-based authentication decorators** for access control.

---

## 📸 Interface Preview

> *Replace the image placeholder blocks below with screenshots of your actual frontend implementation.*

### 🔐 1. Authentication Dashboard
_Secure workspace gateway featuring a streamlined Teacher Login module._

```text
┌──────────────────────────────────────────────────────────┐
│                      Teacher Login                       │
│                                                          │
│  Teacher Name: [_________________]                       │
│  Password:     [*****************]                       │
│                                                          │
│                        [ Login ]                         │
└──────────────────────────────────────────────────────────┘
```
![Teacher Login Screen](https://placeholder.com)

### 📊 2. Main Grading Dashboard Overview
_The comprehensive data hub showcasing active student tracking, search configurations, operations metrics, and live rosters._

```text
┌──────────────────────────────────────────────────────────┐
│ Grading Dashboard                 Welcome, [Teacher]  |  │
├──────────────────────────────────────────────────────────┤
│  [Search Student Grade]         [Add New Student]       │
│  [Update Student Grade]         [Delete Student]         │
└──────────────────────────────────────────────────────────┘
```
![Grading Dashboard Screen](https://placeholder.com)

### ⚙️ 3. Dynamic Roster Operations
_The operational layout highlighting form submission interfaces for managing data entry records, student profiles, and grade metrics._

![Student Operations Interface](https://placeholder.com)

---

## 🚀 Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.x, Flask | RESTful API generation, custom decorator route protection, CORS management |
| **Database** | SQLite3 | Local server-less relational tables (`Student`, `Grades`, `Class`, `Teacher`) |
| **Security** | Flask-CORS, LocalStorage Payload Validation | Cross-Origin resource sharing rules and `Teacher_ID` permission validations |

---

## ✨ Features

* **Custom Payload-Based Authentication:** Uses a custom `@login_required` validation decorator checking `Teacher_ID` inside client request payloads rather than relying on server cookies.
* **Relational Transactions:** Safe, transactional multi-table database operations (`INSERT` / `DELETE`) using SQL commits and rollbacks.
* **Cross-Origin Development Friendly:** Preconfigured out-of-the-box for decoupled frontend tools (like Live Server running on port 5500).

---

## 🛠️ Project Structure

```text
student-grading-system/
├── database/
│   └── Student_grading_system_database.db  # Relational SQLite database file
├── app.py                                  # Core application entrypoint, routes, and logic
├── requirements.txt                        # Application runtime dependencies
└── README.md                               # Project documentation
```

---

## 📥 Installation & Setup

Follow these steps to run the Flask microservice locally.

### Prerequisites
* **Python 3.8+** installed globally.

### 1. Clone & Navigate
```bash
git clone https://github.com
cd student-grading-system
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Create environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install flask flask-cors
```

### 4. Database Setup
Ensure that your database folder matches the configured file path exactly:
* Place your SQLite file at: `database/Student_grading_system_database.db`.

### 5. Run the Server
```bash
python app.py
```
The application will boot up in **Debug Mode** targeting port **`5555`** (`http://127.0.0.1:5555`).

---

## 🔒 API Specifications & Endpoints

### Authentication Routes

| Method | Endpoint | Payload Requirements | Description |
| :--- | :--- | :--- | :--- |
| **POST** | `/login` | `{"Name": "...", "Password": "..."}` | Validates user against database credentials and returns profile information. |
| **POST** | `/logout` | None | Terminates backend session mapping. |

### Grading System Routes

| Method | Endpoint | Payload Requirements / URL Params | Description |
| :--- | :--- | :--- | :--- |
| **GET** | `/Student_Grade/<Student_name>` | URL parameter: `Student_name` | Performs join queries across tables to return standard academic transcripts. |
| **POST** | `/addStudent` | `{"Name", "Marks", "Class", "Age", "Subject", "Teacher_ID"}` | Protected route creating relational database records across tables. |
| **PUT** | `/updateGrades/<Student_name>`| `{"Name", "Marks"}` | Modifies grades records matched dynamically to a target student ID subquery. |
| **POST** | `/Classes` | `{"Teacher_ID"}` | Extracts all tracking course subjects associated with a specific instructor. |
| **POST** | `/delete_Student` | `{"ID"}` | Performs linked safe cascade-style deletion across Student, Grades, and Class tables. |
| **GET** | `/Get_Student/<Student_name>` | URL parameter: `Student_name` | Returns a key-value dictionary dump of raw data from the student schema table. |

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
