from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'student_mgmt_2026_secret'

client = MongoClient('mongodb+srv://dipeshyadav09086_db_user:<db_password>@cluster0.7vidk0m.mongodb.net/?appName=Cluster0')
db = client.student_management
students = db.students
admins = db.admins

if admins.count_documents({}) == 0:
    admins.insert_one({'username': 'admin', 'password': '12345'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if admins.find_one({'username': request.form['username'], 'password': request.form['password']}):
            session['logged_in'] = True
            session['username'] = request.form['username']
            return redirect(url_for('dashboard'))
        flash('Wrong credentials!')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    total = students.count_documents({})
    avg_marks = list(students.aggregate([{'$group': {'_id': None, 'avg': {'$avg': '$marks'}}}]))[0]['avg'] if total > 0 else 0
    recent = list(students.find().sort('created_at', -1).limit(5))
    for s in recent: s['_id'] = str(s['_id'])
    return render_template('dashboard.html', total=total, avg_marks=round(avg_marks, 1), recent=recent)

@app.route('/students', methods=['GET', 'POST'])
def students_view():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        students.insert_one({
            'name': request.form['name'],
            'roll_no': request.form['roll_no'],
            'age': int(request.form['age']),
            'marks': float(request.form['marks']),
            'class': request.form['class'],
            'created_at': datetime.now()
        })
        flash('Student added!')
        return redirect(url_for('students_view'))
    
    all_students = list(students.find().sort('created_at', -1))
    for s in all_students: s['_id'] = str(s['_id'])
    return render_template('students.html', students=all_students)

@app.route('/delete/<student_id>')
def delete(student_id):
    students.delete_one({'_id': ObjectId(student_id)})
    flash('Student deleted!')
    return redirect(url_for('students_view'))

@app.route('/search')
def search():
    q = request.args.get('q', '')
    results = list(students.find({'name': {'$regex': q, '$options': 'i'}}).limit(20))
    for s in results: s['_id'] = str(s['_id'])
    return jsonify(results)

@app.route('/stats')
def stats():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    total = students.count_documents({})
    avg = list(students.aggregate([{'$group': {'_id': None, 'avg': {'$avg': '$marks'}}}]))
    avg_marks = round(avg[0]['avg'], 1) if avg else 0
    return render_template('stats.html', total=total, avg_marks=avg_marks)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

