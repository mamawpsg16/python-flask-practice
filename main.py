from flask import Flask, url_for, request, render_template, jsonify, make_response, abort, redirect, send_from_directory, session, flash
from markupsafe import escape
import os

app = Flask(__name__)

# Routing
@app.route('/')
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello, World'

# HTML Escaping
# @app.route("/<name>")
# def hello(name):
#     return f"Hello, {escape(name)}!"

# Variable Rules
@app.route('/user/<username>')
def show_user_profile(username):
    # show the user profile for that user
    return f'User {escape(username)}'

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return f'Post {post_id}'

@app.route('/path/<path:subpath>')
def show_subpath(subpath):
    # show the subpath after /path/
    return f'Subpath {escape(subpath)}'

# Unique URLs / Redirection Behavior
@app.route('/projects/')
def projects():
    return 'The project page'

@app.route('/about')
def about():
    return 'The about page'

# URL Building
# @app.route('/')
# def index():
#     return 'index'

# @app.route('/login')
# def login():
#     return 'login'

# @app.route('/user/<username>')
# def profile(username):
#     return f'{username}\'s profile'

# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('login'))
#     print(url_for('login', abc='/'))
#     print(url_for('profile', username='John Doe', haha="haha"))

# HTTP Methods
def do_the_login():
    return "Logging In..."

def show_the_login_form():
    return "Login Page"

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         return do_the_login()
#     else:
#         return show_the_login_form()
    
# ABOVE CAN BE SEPARATED LIKE BELOW
@app.get('/login')
def login_get():
    return show_the_login_form()

@app.post('/login')
def login_post():
    # print(request.json) # JSON 
    # print(request.form, "request.form")  # application/x-www-form-urlencode

    # multipart/form-data
    # Access form fields
    # name = request.form.get('name')
    # Access uploaded file
    # uploaded_file = request.files.get('file')

    # To access parameters submitted in the URL (?key=value) you can use the args attribute:
    searchword = request.args.get('id', '')

    print(searchword)
    return do_the_login()


# RENDERING TEMPLATES
@app.route('/greet/')
@app.route('/greet/<name>')
def greet(name=None):
    return render_template('index.html', person=name)

# Accessing Request Data

from flask import request

with app.test_request_context('/hello', method='POST'):
    # now you can do something with the request until the
    # end of the with block, such as basic assertions:
    assert request.path == '/hello'
    assert request.method == 'POST'

# File Uploads
from werkzeug.utils import secure_filename
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_PATH = os.path.join(BASE_DIR,"uploads")
    
@app.post('/upload')
def upload_file():
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_PATH):
        os.makedirs(UPLOAD_PATH)

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the file
    file_path = os.path.join(UPLOAD_PATH, secure_filename(file.filename))
    file.save(file_path)

    # Return a success message
    return jsonify({'message': 'File uploaded successfully'}), 200

@app.route('/uploads/<filename>')
def serve_file(filename):
    # Serve the file from the upload directory
    return send_from_directory('uploads', filename)

# Cookies
@app.route('/set_cookie')
def set_cookie():
    resp = make_response("Cookie Set")
    resp.set_cookie('my_cookie', 'cookie_value', max_age=3600)  # max_age is in seconds
    return resp

@app.route('/get_cookie')
def get_cookie():
    cookie_value = request.cookies.get('my_cookie', 'default_value')  # 'default_value' is returned if the cookie is not found
    return f"The value of the cookie is: {cookie_value}"

@app.route('/delete_cookie')
def delete_cookie():
    resp = make_response("Cookie Deleted")
    resp.set_cookie('my_cookie', '', expires=0)
    return resp

# Redirects and Errors

@app.route('/redirect_to_login')
def redirect_to_login():
    return redirect(url_for('login_get'))

from flask import render_template

@app.errorhandler(401)
def page_not_found(error):
    return render_template('unauthorized.html'), 401

@app.route('/error')
def error():
    abort(401)
    this_is_never_executed()


# APIs with JSON

def get_all_users():
    return [
        {
            "username": "Kevin",
            "theme": "Halloween",
            "image": "S.png",
        },
        {
            "username": "Rustian",
            "theme": "Christmas",
            "image": "Bajaj_Maxima_Cargo.jpeg",
        }
    ]

def get_current_user():
    return {
        "username": "Kevin",
        "theme": "Halloween",
        "image": "S.png",
    }

@app.route("/me")
def user():
    user = get_current_user()
    print(user["username"], "user")
    # Return a JSON response
    # return jsonify({
    #     "username": user["username"],
    #     "theme": user["theme"],
    #     "image": url_for("serve_file", filename=user["image"]),
    # })
    return {
        "username": user["username"],
        "theme": user["theme"],
        "image": url_for("serve_file", filename=user["image"]),
    }

@app.route("/users")
def users_api():
    users = get_all_users()
    return jsonify(users)


# Sessions
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/home')
def home():
    username = None
    if 'username' in session:
        username = session['username']
        flash(f'Welcome ^^', 'info')
    return render_template('home.html', username=username)

@app.route('/authenticate', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        session['username'] = request.form.get('username')
        return redirect(url_for('home'))
    
    return render_template('authenticate.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('home'))

# Message Flashing