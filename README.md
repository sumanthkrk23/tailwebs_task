# Teacher Portal

A robust teacher portal built with **Python (Flask)**, **MySQL**, **JWT authentication**, **vanilla JavaScript**, and **Tailwind CSS**.

## Features
- Secure teacher login with JWT authentication
- Each teacher manages their own student list
- Add, edit, and delete students (name, subject, marks)
- Prevent duplicate student+subject entries (marks are summed)
- Responsive UI with Tailwind CSS
- Teacher profile picture upload and display
- Forgot password (change with old password)
- Teacher registration page

## Tech Stack
- **Backend:** Python (Flask), flask_mysqldb, bcrypt, PyJWT
- **Frontend:** HTML, Tailwind CSS, vanilla JavaScript
- **Database:** MySQL

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. MySQL Database Setup
- Create the database and tables:
```sql
CREATE DATABASE IF NOT EXISTS teacher_portal;
USE teacher_portal;

CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    profile_pic VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    mark INT NOT NULL,
    teacher_id INT,
    UNIQUE KEY unique_student_subject_teacher (name, subject, teacher_id)
);
```
- Update your MySQL credentials in `app.py` if needed.

### 4. Run the App
```bash
python app.py
```
- The app will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Usage
- **Register:** Go to `/register` to create a new teacher account.
- **Login:** Go to `/login` to log in as a teacher.
- **Dashboard:** Manage your students, upload a profile picture, and edit your info.
- **Forgot Password:** Use the "Forgot Password?" link on the login page.

## File Structure
```
├── app.py
├── requirements.txt
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   └── register.html
├── static/
│   └── js/
│       └── main.js
├── uploads/           # Profile pictures
└── README.md
```

## Security Notes
- Passwords are hashed with bcrypt.
- JWT is used for authentication.
- Each teacher can only access their own students.

## Customization
- You can further style the UI with Tailwind CSS.
- Add more teacher profile fields or features as needed.