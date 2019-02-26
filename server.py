#   Python Belt Exam #2

from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re

app = Flask(__name__)
app.secret_key = 'secret'
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-z0-9.+_-]+@[a-zA-z0-9.+_-]+\.[a-zA-Z]+$')


# LOGIN & REGISTRATION HOMEPAGE
@app.route('/')
def index():
    return render_template('index.html')

# REGISTRATION VALIDATIONS
@app.route('/registration', methods=['post'])
def registration():

    # Session Information
    session['first_name'] = request.form['first_name']
    session['last_name'] = request.form['last_name']
    session['email'] = request.form['email']
    session['password'] = request.form['password']

    # print('*'*20,session['first_name'])
    # print('*'*20,session['last_name'])
    # print('*'*20,session['email'])
    # print('*'*20,session['password'])

    is_valid = True

    # Name length validation
    if len(request.form['first_name']) < 3:
        is_valid = False
        # print('*'*20, False, '*'*20)
        flash('Please enter a name that is at least two characters long')
        return redirect('/')

    if len(request.form['last_name']) < 3:
        is_valid = False
        # print('*'*20, False, '*'*20)
        flash('Please enter a name that is at least two characters long')
        return redirect('/')

    # Email format validation
    if not EMAIL_REGEX.match(request.form['email']):
        flash(f"{request.form['email']} is invalid")
        return redirect('/')

    # Existing email validation
    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'SELECT * FROM users WHERE email = %(email)s'
    data = {
        'email': request.form['email']
    }
    existing_email = belt_exam_2.query_db(query, data)

    # print('*'*20,existing_email)
    if len(existing_email) > 0:
        flash('Email already exist.')
        # print(('~'*20))
        return redirect('/')

    # Password length validation
    if len(request.form['password']) < 8:
        is_valid = False
        # print('*'*20, False, '*'*20)
        flash('Please enter a password name that is at least 8 characters long')
        return redirect('/')

    # Password match validation
    if request.form['password'] != request.form['password_conf']:
        is_valid = True
        flash('Make sure your passwords match')
        return redirect('/')

    # Registration Insertion
    if is_valid:
        belt_exam_2 = connectToMySQL('belt_exam_2')
        query = 'INSERT INTO users (first_name, last_name, email, password) VALUES (%(first_name)s,%(last_name)s,%(email)s,%(password)s);'
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'password': bcrypt.generate_password_hash(request.form['password'])
        }

        users = belt_exam_2.query_db(query, data)
        # print('*----*'*20,users)

        flash("You've successfully registered!")

        return redirect('/dashboard')


# LOGIN VALIDATIONS
@app.route('/login', methods=['post'])
def login():

    # Session Information
    session['email'] = request.form['email']

    # is_valid = True

    # Email format validation
    if not EMAIL_REGEX.match(request.form['email']):
        flash(f"{request.form['email']} is invalid")
        return redirect('/')

    # Existing email validation
    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'SELECT * FROM users WHERE email = %(email)s'
    data = {
        'email': request.form['email']
    }

    logins = belt_exam_2.query_db(query, data)
    # print(logins,'*/'*30)
    # print('*-*'*20,request.form['email'])

    if len(logins) == 0:
        flash("Failed login! Email not found.")
        return redirect('/')

    # Password validation
    if logins:
        if bcrypt.check_password_hash(logins[0]['password'], request.form['password']):
            flash("Logged in successfully!")
            return redirect('/dashboard')
        else:
            flash("Failed login! Password was incorrect.")
            return redirect('/')

# dashboard PAGE


@app.route('/dashboard')
def dashboard():

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'SELECT * FROM users WHERE email = %(email)s;'
    data = {'email': session['email']}
    users = belt_exam_2.query_db(query, data)
    session['id'] = users[0]['id']
    # print(session['id'],'*'*40)
    # print('---'*20, users[0]['id'])
    # print(users)

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'SELECT * FROM jobs WHERE job_taker IS NULL;'
    all_jobs = belt_exam_2.query_db(query)
    # print('*'*20, all_jobs['user_id'])
    # print(all_jobs)

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'SELECT * FROM jobs JOIN users ON jobs.user_id = users.id WHERE jobs.job_taker = %(user_id)s;'
    data = {
        'user_id' : session['id']
    }
    user_jobs = belt_exam_2.query_db(query,data)
   

    return render_template('dashboard.html', users=users, all_jobs=all_jobs, user_jobs=user_jobs)


# CREATE A JOB FORM

@app.route('/jobs/new')
def newjob():
    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'SELECT * FROM users WHERE email = %(email)s;'
    data = {'email': session['email']}
    users = belt_exam_2.query_db(query, data)
    session['id'] = users[0]['id']
    return render_template('create_job.html', users=users)

# CREATE A JOB SUBMISSION


@app.route('/create_job', methods = ['post'])
def create_job():
    # print('*'*20, request.form['job_title'])
    # print('*'*20, request.form['job_description'])
    # print('*'*20, request.form['address'])
    # print('*'*20, request.form['job_categories'])
    # print('*'*20, request.form['other'])
    # print('*'*20, session['id'])

    is_valid = True

    # Job_title length validation
    if len(request.form['job_title']) < 3:
        is_valid = False
        # print('*'*20, False, '*'*20)
        flash('A job must consist of at least 3 characters!')
        return redirect('/jobs/new')

    # location length validation
    if len(request.form['address']) < 3:
        is_valid = False
        # print('*'*20, False, '*'*20)
        flash('A location must be provided')
        return redirect('/jobs/new')

    # description length validation
    if len(request.form['job_description']) < 3:
        is_valid = False
        # print('*'*20, False, '*'*20)
        flash('A description must be provided')
        return redirect('/jobs/new')

    # Add a job

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'INSERT INTO jobs (job_title, job_description, address, user_id) VALUES (%(job_title)s,%(job_description)s, %(address)s, %(user_id)s)'
    data = {
        'job_title': request.form['job_title'],
        'job_description': request.form['job_description'],
        'address': request.form['address'],
        'user_id': session['id']
    }
    job = belt_exam_2.query_db(query, data)

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'INSERT INTO job_categories (job_categories,job_id) VALUES (%(job_categories)s,%(job_id)s)'
    data = {
        'job_categories': request.form['category_1'],
        'job_id': job
    }
    job_categories = belt_exam_2.query_db(query, data)

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'INSERT INTO job_categories (job_categories,job_id) VALUES (%(job_categories)s,%(job_id)s)'
    data = {
        'job_categories': request.form['category_2'],
        'job_id': job
    }
    job_categories = belt_exam_2.query_db(query, data)

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'INSERT INTO job_categories (job_categories,job_id) VALUES (%(job_categories)s,%(job_id)s)'
    data = {
        'job_categories': request.form['category_3'],
        'job_id': job
    }
    job_categories = belt_exam_2.query_db(query, data)

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'INSERT INTO job_categories (job_categories,job_id) VALUES (%(job_categories)s,%(job_id)s)'
    data = {
        'job_categories': request.form['category_4'],
        'job_id': job
    }
    job_categories = belt_exam_2.query_db(query, data)

    return redirect('/dashboard')

#View Job

@app.route('/job/<id>')
def job_id(id):

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'SELECT * FROM users WHERE email = %(email)s;'
    data = {'email': session['email']}
    users = belt_exam_2.query_db(query, data)
    session['id'] = users[0]['id']


    # Job_id 
    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'SELECT *, group_concat(job_categories,"") AS categories FROM jobs JOIN job_categories ON job_categories.job_id =jobs.id WHERE jobs.id = %(job_id)s GROUP BY %(job_id)s;'
    data = {
        'job_id': id
    }
    jobs = belt_exam_2.query_db(query,data)
    print(jobs)
    return render_template('job_id.html', users = users, jobs = jobs)

# UPDATES

@app.route('/update/<id>', methods=['post'])
def update(id):

    print('*-'*20,request.form['job_title'])

    #Validations
    is_valid = True

    # Job_title length validation
    if len(request.form['job_title']) < 3:
        is_valid = False
        print('*'*20, False, '*'*20)
        flash('A job must consist of at least 3 characters!')
        return redirect(f'/edit/{id}')

    # location length validation
    if len(request.form['address']) < 3:
        is_valid = False
        print('*'*20, False, '*'*20)
        flash('A location must be provided')
        return redirect(f'/edit/{id}')

    # description length validation
    if len(request.form['job_description']) < 3:
        is_valid = False
        print('*'*20, False, '*'*20)
        flash('A description must be provided')
        return redirect(f'/edit/{id}')

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'SELECT * FROM jobs JOIN users ON jobs.user_id = users.id WHERE users.id = %(user_id)s;'
    data = {
        'user_id' : session['id']
    }
    user_jobs = belt_exam_2.query_db(query,data)

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'UPDATE jobs SET job_title = %(job_title)s, job_description = %(job_description)s, address = %(address)s WHERE jobs.id = %(job_id)s'
    data = {
        'job_title': request.form['job_title'],
        'job_description': request.form['job_description'],
        'address': request.form['address'],
        'job_id' : id
        # 'other': request.form['other']
    }
    jobs = belt_exam_2.query_db(query, data)
    print(jobs)

    return redirect('/dashboard')


# Edit the job page
@app.route('/edit/<id>')
def edit(id):

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'SELECT * FROM jobs JOIN users ON jobs.user_id = users.id WHERE users.id = %(user_id)s AND jobs.id = %(job_id)s;'
    data = {
        'user_id' : session['id'],
        'job_id' : id
    }
    users = belt_exam_2.query_db(query,data)
    print(users)

    return render_template('edit_job.html', users = users)

    

@app.route('/pick_up_job/<id>')
def pick_up_job(id):

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'UPDATE jobs SET jobs.job_taker =%(user_id)s WHERE jobs.id = %(jobs_id)s;'
    data = {
        'jobs_id' : id,
        'user_id' : session['id']
    }
    user_jobs = belt_exam_2.query_db(query,data)

    return redirect('/dashboard')

@app.route('/giveup/<id>')
def giveup(id):

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'UPDATE jobs SET job_taker = NULL WHERE jobs.id = %(jobs_id)s;'
    data = {
        'jobs_id' : id
    }
    user_jobs = belt_exam_2.query_db(query,data)

    return redirect('/dashboard')

# DELETIONS

@app.route('/remove/<id>')
def remove(id):

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'DELETE from jobs WHERE jobs.id = %(jobs_id)s;'
    data = {
        'jobs_id' : id
    }
    user_jobs = belt_exam_2.query_db(query,data)

    return redirect('/dashboard')


@app.route('/done/<id>')
def done(id):

    belt_exam_2 = connectToMySQL('belt_exam_2')
    query = 'DELETE from jobs WHERE jobs.id = %(jobs_id)s;'
    data = {
        'jobs_id' : id
    }
    user_jobs = belt_exam_2.query_db(query,data)

    return redirect('/dashboard')




# RETURN TO HOME BUTTON

@app.route('/home')
def home():
    return redirect('/dashboard')

# CANCEL BUTTON


@app.route('/cancel', methods=['post'])
def cancel():
    return redirect('/dashboard')

# LOGOUT BUTTON


@app.route('/logoff')
def logoff():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
