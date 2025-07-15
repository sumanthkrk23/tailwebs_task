from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_mysqldb import MySQL
import MySQLdb.cursors
import jwt
import datetime
from functools import wraps
import os
import bcrypt

app = Flask(__name__)
app.secret_key = ''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root@123'
app.config['MYSQL_DB'] = 'teacher_portal'
app.config['UPLOAD_FOLDER'] = 'uploads'

mysql = MySQL(app)
JWT_SECRET = 'zsnbcuqtvcsd6ryryd5yc56cw2jhdtefg22b3d82'

# JWT Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = data['username']
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM teachers WHERE username = %s', (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode(), user['password'].encode()):
            token = jwt.encode({'username': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)}, JWT_SECRET, algorithm="HS256")
            return jsonify({'token': token})
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('INSERT INTO teachers (username, password) VALUES (%s, %s)', (username, hashed_password))
    mysql.connection.commit()
    return jsonify({'message': 'Teacher registered successfully'})

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    token = request.cookies.get('jwt') or request.headers.get('Authorization', '').replace('Bearer ', '') or request.args.get('token') or None
    if not token:
        return redirect(url_for('login'))
    try:
        jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Helper to get teacher_id from username
def get_teacher_id(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT id FROM teachers WHERE username = %s', (username,))
    user = cursor.fetchone()
    return user['id'] if user else None

@app.route('/students', methods=['GET'])
@token_required
def get_students(current_user):
    teacher_id = get_teacher_id(current_user)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM students WHERE teacher_id = %s', (teacher_id,))
    students = cursor.fetchall()
    return jsonify(students)

@app.route('/students', methods=['POST'])
@token_required
def add_student(current_user):
    data = request.json
    name = data['name']
    subject = data['subject']
    mark = data['mark']
    teacher_id = get_teacher_id(current_user)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM students WHERE name = %s AND subject = %s AND teacher_id = %s', (name, subject, teacher_id))
    student = cursor.fetchone()
    if student:
        cursor.execute('UPDATE students SET mark = mark + %s WHERE id = %s', (mark, student['id']))
    else:
        cursor.execute('INSERT INTO students (name, subject, mark, teacher_id) VALUES (%s, %s, %s, %s)', (name, subject, mark, teacher_id))
    mysql.connection.commit()
    return jsonify({'message': 'Student record updated/added'})

@app.route('/students/<int:id>', methods=['PUT'])
@token_required
def edit_student(current_user, id):
    data = request.json
    name = data['name']
    subject = data['subject']
    mark = data['mark']
    teacher_id = get_teacher_id(current_user)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Only update if the student belongs to the teacher
    cursor.execute('UPDATE students SET name = %s, subject = %s, mark = mark + %s WHERE id = %s AND teacher_id = %s', (name, subject, mark, id, teacher_id))
    mysql.connection.commit()
    return jsonify({'message': 'Student updated'})

@app.route('/students/<int:id>', methods=['DELETE'])
@token_required
def delete_student(current_user, id):
    teacher_id = get_teacher_id(current_user)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Only delete if the student belongs to the teacher
    cursor.execute('DELETE FROM students WHERE id = %s AND teacher_id = %s', (id, teacher_id))
    mysql.connection.commit()
    return jsonify({'message': 'Student deleted'})

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    username = data.get('username')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    if not all([username, old_password, new_password, confirm_password]):
        return jsonify({'message': 'All fields are required'}), 400
    if new_password != confirm_password:
        return jsonify({'message': 'New passwords do not match'}), 400
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM teachers WHERE username = %s', (username,))
    user = cursor.fetchone()
    if not user or not bcrypt.checkpw(old_password.encode(), user['password'].encode()):
        return jsonify({'message': 'Invalid username or old password'}), 401
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    cursor.execute('UPDATE teachers SET password = %s WHERE username = %s', (hashed_password, username))
    mysql.connection.commit()
    return jsonify({'message': 'Password updated successfully'})

@app.route('/upload-profile-pic', methods=['POST'])
@token_required
def upload_profile_pic(current_user):
    if 'profile_pic' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['profile_pic']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file:
        filename = f"{current_user}_profile_{datetime.datetime.utcnow().timestamp()}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE teachers SET profile_pic = %s WHERE username = %s', (filename, current_user))
        mysql.connection.commit()
        return jsonify({'message': 'Profile picture updated', 'profile_pic': filename})
    return jsonify({'message': 'File upload failed'}), 500

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT username, profile_pic FROM teachers WHERE username = %s', (current_user,))
    user = cursor.fetchone()
    if user:
        if user['profile_pic']:
            user['profile_pic_url'] = url_for('uploaded_file', filename=user['profile_pic'])
        else:
            user['profile_pic_url'] = None
        return jsonify(user)
    return jsonify({'message': 'User not found'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True) 