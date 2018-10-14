from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body


def checkTitleError(post_title):
    if len(post_title)>0:
        return None
    return "Please name your blog post."

def checkBodyError(post_body):
    if len(post_body)>0:
        return None
    return "What would you like to say in your post?"

@app.route('/')
def index():
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def create_post():
    if request.method == 'POST':
        post_title = request.form['post-title']
        post_body = request.form['post-body']
        titleError = checkTitleError(post_title)
        bodyError = checkBodyError(post_body)

        if titleError or bodyError:
            return render_template('newpost.html', titleError=titleError, bodyError=bodyError, post_title=post_title, post_body=post_body)
        new_post = Blog(post_title, post_body)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id=' + str(new_post.id))
    return render_template('newpost.html')

def tryAgain():
    if titleError or bodyError:
        return render_template('newpost.html')
            
    
@app.route('/blog')
def blog_posts():
    post_id = request.args.get('id')
    if post_id:
        post = Blog.query.get(post_id)
        print(post)
        return render_template('post.html', post_title=post.title, post_body=post.body)
    posts = Blog.query.all()
    return render_template('blog.html', posts=posts)

    
if __name__ == '__main__':
    app.run()
