from flask import Flask, request, redirect, render_template, session, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:nynja@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "y337kGcys&zP3B"

# -------------------------------------------------------------------------------

class Entry(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    date = db.Column(db.String(120))
    time = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, date, time):
        self.title = title
        self.body = body    
        self.owner = owner
        self.date = date
        self.time = time

# -------------------------------------------------------------------------------

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    entries = db.relationship('Entry', backref='owner')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

# -------------------------------------------------------------------------------

@app.route('/', methods=['POST', 'GET'])
def index():

    entry_owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        entry_title = request.form['title']
        entry_body = request.form['body']
        if datetime.today().hour > 12:
            tag = 'PM'
        else:
            tag = 'AM'
        entry_date = str(datetime.today().year) + "/" + str(datetime.today().month) + "/" + str(datetime.today().day)
        entry_time = str(datetime.today().hour % 12) + ":" + str(datetime.today().minute) + ":" + str(datetime.today().second) + ' ' + tag
        if not entry_title or not entry_body:
            flash("Your post must include both a title and body", 'error')
            return redirect('/')
        else:
            new_entry = Entry(entry_title, entry_body, entry_owner, entry_date, entry_time)
            db.session.add(new_entry)
            db.session.commit()

    entries = Entry.query.filter_by().all()
    personal_entries = Entry.query.filter_by(owner=entry_owner).all()
    return render_template('home.html', title="Blogz", entries=entries)

# -------------------------------------------------------------------------------

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in!", 'success')
            print(session)
            return redirect('/')
        else:
            flash("User password incorrect, or user does not exist", 'error')

    return render_template('login.html', title="Login!")

# -------------------------------------------------------------------------------

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        email_error = ''
        password_error = ''
        verify_error = ''
        

        upper_alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        special = "!@#$%^&*?"

        # email
        at_count = 0
        e_space_count = 0
        dot_count = 0

        # password
        upper_count = 0
        p_space_count = 0
        digit_count = 0
        special_count = 0
        char_count = 0


        for char in str(email):
            if char == '@':
                at_count += 1
            elif char == ' ':
                e_space_count += 1
            elif char == '.':
                dot_count += 1

        if not (at_count == 1) or not (e_space_count == 0) or not (dot_count >= 1):
            #email_error += "invalid email address"
            flash("Invalid Email address", 'error')

        for char in str(password):
            char_count += 1

            if char in upper_alpha:
                upper_count += 1
            elif char in digits:
                digit_count += 1
            elif char == ' ':
                p_space_count += 1
            elif char in special:
                special_count += 1

        if not upper_count >= 1:
            password_error += "Password must contain an upper-case character"
        elif not digit_count >= 1:
            password_error += "Password must contain a digit"
        elif not special_count >= 1:
            password_error += "Password must contain a special character"
        elif not p_space_count == 0:
            password_error += "Password must not contain whitespace"
        elif (len(password) < 3) or (len(password) > 20):
            password_error += "Password must be between 3 and 20 characters"

        if verify != password:
            verify_error += 'Your passwords did not match'

        registered_user = User.query.filter_by(email=email).first()
        if not email_error and not password_error and not verify_error and not registered_user:
            new_user = User(username, email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            return render_template('register.html', email_error=email_error, password_error=password_error, verify_error=verify_error)

    return render_template('register.html')

# -------------------------------------------------------------------------------

@app.route('/logout')
def logout():
    del session['email']
    flash("Logged out!", 'success')
    return redirect('/login')

# -------------------------------------------------------------------------------

@app.route('/user-page', methods=['POST','GET'])
def user_page():

    
    user_id = int(request.args.get('user'))
    author = User.query.filter_by(id=user_id).first()
    entries = Entry.query.filter_by(owner_id=user_id).all()
    return render_template('user-page.html', entries=entries, author=author)

# -------------------------------------------------------------------------------

@app.route('/post-page', methods=['POST','GET'])
def single_page():

    
    entry_id = request.args.get('entryID')
    print(entry_id)
    print(entry_id)
    print(entry_id)
    print(entry_id)
    author = request.args.get('user')
    print(author)
    print(author)
    print(author)
    print(author)
    print(author)
    entry = Entry.query.filter_by(id=entry_id).first()
    print(entry)
    print(entry)
    print(entry)
    print(entry)
    print(entry)
    return render_template('post-page.html', entry=entry, author=author)

# -------------------------------------------------------------------------------

@app.route('/post-entry', methods=['POST', 'GET'])
def post_entry():

    entry_owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        entry_title = request.form['title']
        entry_body = request.form['body']
        if not entry_title or not entry_body:
            flash("Your post must include both a title and body", 'error')
            return redirect('/')
        else:
            new_entry = Entry(entry_title, entry_body, entry_owner)
            db.session.add(new_entry)
            db.session.commit()


    return render_template('post-entry.html')

# -------------------------------------------------------------------------------

@app.before_request
def require_login():
    print(session)
    allowed_routes = ['register', 'login', 'home']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------
# -------------------------------------------------------------------------------

if __name__ == "__main__":
    app.run()