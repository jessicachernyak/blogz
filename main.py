from flask import Flask, flash, session, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def checkTitleError(post_title):
    if len(post_title)>0:
        return None
    return "Please name your blog post."

def checkBodyError(post_body):
    if len(post_body)>0:
        return None
    return "What would you like to say in your post?"

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def create_post():
    if request.method == 'POST':
        post_title = request.form['post-title']
        post_body = request.form['post-body']
        titleError = checkTitleError(post_title)
        bodyError = checkBodyError(post_body)

        if titleError or bodyError:
            return render_template('newpost.html', titleError=titleError, bodyError=bodyError, post_title=post_title, post_body=post_body)
        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(post_title, post_body, owner)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id=' + str(new_post.id))
    return render_template('newpost.html')

# def tryAgain():
#     if titleError or bodyError:
#         return render_template('newpost.html')
            
    
@app.route('/blog')
def blog():
    post_id = request.args.get('id')
    if post_id:
        post = Blog.query.get(post_id)
        return render_template('post.html', post=post)
    posts = Blog.query.all()
    user_id = request.args.get('user')
    if user_id:
        blog_posts = Blog.query.filter_by(owner_id=user_id)
        # print(blog_posts)
        return render_template('blog.html', posts=blog_posts)

    return render_template('blog.html', posts=posts)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")

    form = request.form
    username = form['username']
    password = form['password']
    vpass = form['vpass']

    username_error = lenUsername(username)
    password_error = lenPassword(password)
    verify_password_error = matchPassword(password, vpass)

    if username_error or password_error or verify_password_error:
        return render_template("signup.html", 
            username_error=username_error, 
            password_error=password_error, 
            verify_password_error=verify_password_error, 
            username=username)

    existing_user = User.query.filter_by(username=username).first()
    if not existing_user:
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
    else:
        return "<h1>Duplicate user</h1>"

    return redirect("/newpost")

def lenUsername(username):
    if len(username)>2 and len(username) < 25:
        return None
    return "Please type in a username of at least 3 characters."

def lenPassword(password):
    if len(password)>2 and len(password) < 120:
        return None
    return "Please type in a password of at least 3 characters."

def matchPassword(password, vpass):
    if len(vpass) < 1:
        return "You must verify your password."
    elif password == vpass:
        return None
    return "Your passwords do not match."

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # form = request.form
        # username = form['username']
        # password = form['password']
        # username_error = lenUsername(username)
        
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/')
        elif user and user.password != password:
            flash("Your password is invalid.")
        else:
            flash('The username does not exist!')

    return render_template('login.html')

# def userNonexistant():
#     if user:
#         return None
#     return 'The username does not exist!'


@app.route('/logout')
def logout():
    try:
        del session['username']
    except:
        pass
    finally:
        return redirect('/blog')
    
if __name__ == '__main__':
    app.run()
