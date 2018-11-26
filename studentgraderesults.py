#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""IS211 Assignment12 - Web Development with Flask - Tested in Python 3.6.3 :: Anaconda, Inc."""

from flask import Flask
from flask import session
from flask import redirect
from flask import request
from flask import render_template
import sqlite3
import re
import datetime

app = Flask(__name__)
status_message = ""


class Student:

    def __init__(self, id, first_name, last_name):
        self.id = int(id)
        self.first_name = first_name
        self.last_name = last_name

class Quiz:

    def __init__(self, id, subject, num_of_questions, date):
        self.id = int(id)
        self.subject = subject
        self.num_of_questions = int(num_of_questions)
        self.date = date

class Result:

    def __init__(self, quiz_id, grade, date=None, subject=None):
        self.quiz_id = quiz_id
        self.grade = grade
        self.date = date
        self.subject = subject

@app.route('/')
def index():
    return redirect("/dashboard")

@app.route('/login', methods=['GET', 'POST'])
def login():
    global status_message

    credentials_filled = 'username' in request.form and \
                         'password' in request.form

    if credentials_filled:
        correct_credentials = request.form['username'] == 'admin' and \
                              request.form['password'] == 'password'

    if credentials_filled and correct_credentials:
        session['username'] = request.form['username']
        return redirect('/dashboard')
    elif credentials_filled and not correct_credentials:
        status_message = "ERROR: No password matches that username."
    elif not credentials_filled:
        status_message = ""

    return render_template('login.html', status_message=status_message)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    if 'username' not in session:
        return redirect('/login')

    conn = sqlite3.connect("studentgrade.db")

    student_list = conn.execute("SELECT * FROM Students ORDER BY id ASC")
    quiz_list = conn.execute("SELECT * FROM Quizzes ORDER BY id ASC")

    student_roster = []
    for student in student_list.fetchall():
        student_roster.append(Student(student[0], student[1], student[2]))
    list_of_quizzes = []
    for quiz in quiz_list.fetchall():
        list_of_quizzes.append(Quiz(quiz[0], quiz[1], quiz[2], quiz[3]))

    conn.commit()
    conn.close()

    username = session['username']
    return render_template('dashboard.html', student_roster=student_roster,
                           list_of_quizzes=list_of_quizzes, username=username)

@app.route('/student/add', methods=['GET','POST'])
def add_student():

    if 'username' not in session:
        return redirect('/login')

    global status_message

    first_name = ""
    last_name = ""

    pattern = "^[a-zA-Z]+$"

    if not ('fname' in request.form and 'lname' in request.form):
        status_message = ""
        return render_template('addStudent.html',
                               status_message=status_message)
    elif 'fname' in request.form and 'lname' in request.form:
        if re.search(pattern, request.form['fname']) and \
                re.search(pattern, request.form['lname']):
            first_name = request.form['fname']
            last_name = request.form['lname']
        else:
            status_message="ERROR: You must enter proper first and last" \
                           "names. (Letters only)"
            return render_template('addStudent.html',
                                   status_message=status_message)
    status_message = ""

    conn = sqlite3.connect("studentgrade.db")
    add_statement = '''INSERT INTO Students (id, first_name, last_name) VALUES (NULL, "%s", "%s");''' % (first_name, last_name)
    conn.execute(add_statement)
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/student/delete', methods=['GET','POST'])
def delete_student():


    if 'username' not in session:
        return redirect('/login')

    delete_statement = """DELETE FROM Students WHERE id=%s""" % request.form['student_id']
    delete_assoc_results = """DELETE FROM Student_Results WHERE student_id=%s""" % request.form['student_id']

    conn = sqlite3.connect("studentgrade.db")
    conn.execute(delete_statement)
    conn.execute(delete_assoc_results)
    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route('/quiz/add', methods=['GET','POST'])
def add_quiz():

    if 'username' not in session:
        return redirect('/login')

    global status_message

    if 'username' not in session:
        return redirect('/login')

    number_only_pattern = "^[0-9]+$"

    all_fields_filled = 'subject' in request.form and \
                        'numOfQuestions' in request.form and \
                        'day' in request.form and \
                        'month' in request.form and \
                        'year' in request.form

    if not all_fields_filled:
        status_message = ""
        return render_template('addQuiz.html',
                               status_message=status_message)
    elif all_fields_filled:
        valid_subject = request.form['subject']

        if re.search(number_only_pattern, request.form['numOfQuestions']):
            valid_num_of_questions = request.form['numOfQuestions']
        else:
            status_message = "ERROR: Number of questions must be a number."
            return render_template('addQuiz.html',
                                   status_message=status_message)

        try:
            valid_date = datetime.date(int(request.form['year']),
                                       int(request.form['month']),
                                       int(request.form['day']))
        except ValueError:
            status_message = "ERROR: The date is not valid."
            return render_template('addQuiz.html',
                                   status_message=status_message)

    status_message = ""

    conn = sqlite3.connect("studentgrade.db")
    add_statement = '''INSERT INTO Quizzes (id, subject, num_of_questions, date) VALUES (NULL, "%s", "%s", "%s");'''\
                    % (valid_subject, valid_num_of_questions, valid_date)
    conn.execute(add_statement)
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/quiz/delete', methods=['GET','POST'])
def delete_quiz():

    if 'username' not in session:
        return redirect('/login')

    delete_statement = """DELETE FROM Quizzes WHERE id=%s;""" % request.form['quiz_id']
    delete_assoc_result_statement = """DELETE FROM Student_Results WHERE quiz_id=%s;""" \
                                    % request.form['quiz_id']

    conn = sqlite3.connect("studentgrade.db")
    conn.execute(delete_statement)
    conn.execute(delete_assoc_result_statement)
    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route('/quiz/<id>/results', methods=['GET','POST'])
def anonymous_view(id):
    
    anonymous_statement = """SELECT Student_Results.student_id, Quizzes.date,
                                Quizzes.subject, Student_Results.result,
                                Quizzes.num_of_questions, Quizzes.id
                             FROM Student_Results
                             LEFT JOIN Quizzes
                             ON Student_Results.quiz_id = Quizzes.id
                             WHERE quiz_id == %s
                             ORDER BY Student_Results.result DESC""" % id

    quiz_id_list_statement = """SELECT id FROM Quizzes"""

    conn = sqlite3.connect("studentgrade.db")

    grade_data_med = conn.execute(anonymous_statement)
    grade_data = grade_data_med.fetchall()

    quiz_id_list_med = conn.execute(quiz_id_list_statement)
    quiz_id_list = quiz_id_list_med.fetchall()

    conn.commit()
    conn.close()

    valid_quizzes = []
    for quiz_id in quiz_id_list:
        valid_quizzes.append(quiz_id[0])

    if len(grade_data) == 0:
        has_results = False
    else:
        has_results = True

    return render_template('AnonymousViewer.html', list_of_quizzes=grade_data,
                           has_results=has_results,
                           valid_quizzes=valid_quizzes)


@app.route('/student/<id>', methods=['GET','POST'])
def student_quiz_details(id):

    if 'username' not in session:
        return redirect('/login')

    student_name_statement = """SELECT first_name, last_name
                                FROM Students
                                WHERE id == %s;
                             """ % id

    joined_quiz_statement = """SELECT Student_Results.quiz_id,
                                  Quizzes.date, Quizzes.subject,
                                  Student_Results.result
                               FROM Student_Results
                               LEFT JOIN Quizzes
                               ON Student_Results.quiz_id = Quizzes.id
                               WHERE student_id == %s
                               ORDER BY Student_Results.quiz_id ASC;
                            """ % id

    conn = sqlite3.connect("studentgrade.db")

    student_whole_name = conn.execute(student_name_statement).fetchone()
    student_name = "%s %s" % (student_whole_name[0], student_whole_name[1])

    quiz_results = conn.execute(joined_quiz_statement)

    list_of_grades = []

    for quiz in quiz_results.fetchall():
        list_of_grades.append(Result(quiz[0], quiz[3], quiz[1], quiz[2]))
    conn.commit()
    conn.close()

    has_results = True
    if len(list_of_grades) == 0:
        has_results = False

    return render_template('StudentQuizDetail.html', id=id,
                           student_name=student_name,
                           list_of_grades=list_of_grades,
                           has_results=has_results)


@app.route('/results/add', methods=['GET','POST'])
def add_result():

    if 'username' not in session:
        return redirect('/login')

    if 'student' in request.form and 'quiz' in request.form and\
                    'grade' in request.form:
        all_values_filled = True
    else:
        all_values_filled = False

    conn = sqlite3.connect("studentgrade.db")
    student_list_statement = """SELECT first_name || " " || last_name, id FROM Students;"""
    quizzes_list_statement = """SELECT id || ". " || subject, id FROM Quizzes ORDER BY id ASC;"""
    student_list = conn.execute(student_list_statement)
    quizzes_list = conn.execute(quizzes_list_statement)

    if not all_values_filled:
        error_message = ""
        return render_template('addResult.html',
                               list_of_students=student_list.fetchall(),
                               list_of_quizzes=quizzes_list.fetchall(),
                               error_message=error_message)
    else:
        if request.form['student'] == "not_allowed":
            error_message = "ERROR: You must choose a student."
            return render_template('addResult.html',
                                   list_of_students=student_list.fetchall(),
                                   list_of_quizzes=quizzes_list.fetchall(),
                                   error_message=error_message)
        elif request.form['quiz'] == "not_allowed":
            error_message = "ERROR: You must choose a quiz."
            return render_template('addResult.html',
                                   list_of_students=student_list.fetchall(),
                                   list_of_quizzes=quizzes_list.fetchall(),
                                   error_message=error_message)
        try:
            grade = float(request.form['grade'])
        except ValueError:
            error_message = "ERROR: Please enter a valid number for the grade."
            return render_template('addResult.html',
                                   list_of_students=student_list.fetchall(),
                                   list_of_quizzes=quizzes_list.fetchall(),
                                   error_message=error_message)

    add_grade_statement = """INSERT INTO Student_Results (student_id, quiz_id, result) 
                             VALUES
                             (%s, %s, %s);""" % (request.form['student'],
                                                 request.form['quiz'],
                                                 str(grade))
    conn.execute(add_grade_statement)
    conn.commit()
    conn.close()

    return redirect('/dashboard')


@app.route('/results/delete', methods=['GET','POST'])
def delete_result(): 
    if 'username' not in session:
        return redirect('/login')

    delete_statement = """DELETE FROM Student_results
                          WHERE student_id=%s AND quiz_id=%s AND result=%s
                          LIMIT 1;""" % (request.form['student_id'],
                                         request.form['quiz_id'],
                                         request.form['grade'])

    conn = sqlite3.connect("studentgrade.db")
    conn.execute(delete_statement)
    conn.commit()
    conn.close()

    return redirect("/student/%s" % request.form['student_id'])

@app.route('/logout')
def logout():
    if 'username' not in session:
        return redirect('/login')

    session.pop('username', None)
    return redirect('/')

app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'

if __name__ == "__main__":
    app.run()
