import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB upload limit
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///allyalley.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    """Show current user's posts only"""
    posts = db.execute(
        "SELECT * FROM posts WHERE userid=? ORDER BY timestamp DESC", user_id)
    username = db.execute(
        "SELECT username FROM users WHERE id=?", user_id)[0]['username']

    if posts:
        for post in posts:
            user = db.execute(
                "SELECT username FROM users WHERE id=?", post["userid"])
            if user:
                post['user'] = user[0]['username']
            user_liked = db.execute(
                "SELECT * FROM likes WHERE postid=? AND userid=?", post['id'], user_id)
            if user_liked:  # this is used to print solid hearts or not
                post["user_liked"] = True
            else:
                post["user_liked"] = False
            likes = db.execute(
                "SELECT COUNT(*) FROM likes WHERE postid=?", post['id'])
            post['likes_count'] = likes[0]['COUNT(*)']
            # https://www.programiz.com/python-programming/datetime/strptime
            post['timestamp'] = datetime.datetime.strptime(
                post['timestamp'], '%Y-%m-%d %H:%M:%S')
            post['timestamp'] = post['timestamp'].strftime(
                '%B %d, %Y, %I:%M %p')

            if post['path'].endswith(('mp4', 'avi', 'mov')):
                post['is_video'] = True
            else:
                post['is_video'] = False

    return render_template("profile.html", posts=posts, username=username)


@app.route("/post/<int:post_id>")
@login_required
def current_post(post_id):
    """Show current post only"""
    post = db.execute(
        "SELECT * FROM posts WHERE id=?", post_id)[0]
    comments = db.execute(
        "SELECT * FROM comments WHERE postid=? ORDER BY timestamp DESC", post_id)
    if post:
        user = db.execute(
            "SELECT username FROM users WHERE id=?", post["userid"])
        if user:
            post['user'] = user[0]['username']
        user_liked = db.execute(
            "SELECT * FROM likes WHERE postid=? AND userid=?", post['id'], session["user_id"])
        if user_liked:  # this is used to print solid hearts or not
            post["user_liked"] = True
        else:
            post["user_liked"] = False
        likes = db.execute(
            "SELECT COUNT(*) FROM likes WHERE postid=?", post['id'])
        post['likes_count'] = likes[0]['COUNT(*)']
        # https://www.programiz.com/python-programming/datetime/strptime
        post['timestamp'] = datetime.datetime.strptime(
            post['timestamp'], '%Y-%m-%d %H:%M:%S')
        post['timestamp'] = post['timestamp'].strftime(
            '%B %d, %Y, %I:%M %p')

        if post['path'].endswith(('mp4', 'avi', 'mov')):
            post['is_video'] = True
        else:
            post['is_video'] = False
        for comment in comments:
            comment['timestamp'] = datetime.datetime.strptime(
                comment['timestamp'], '%Y-%m-%d %H:%M:%S')
            comment['timestamp'] = comment['timestamp'].strftime(
                '%B %d, %Y, %I:%M %p')
            # Retrieve the username associated with the userid of the comment
            comment['user'] = db.execute("SELECT username FROM users WHERE id=?", comment['userid'])[0]["username"]

        return render_template("post.html", post=post, comments=comments)
    else:
        return apology("No post!", 400)




@app.route("/")
@login_required
def index():
    """Show user feed"""
    posts = db.execute(
        "SELECT * FROM posts ORDER BY timestamp DESC")
    if posts:
        for post in posts:
            user = db.execute(
                "SELECT username FROM users WHERE id=?", post["userid"])
            if user:
                post['user'] = user[0]['username']
            user_liked = db.execute(
                "SELECT * FROM likes WHERE postid=? AND userid=?", post['id'], session["user_id"])
            if user_liked:  # this is used to print solid hearts or not
                post["user_liked"] = True
            else:
                post["user_liked"] = False
            likes = db.execute(
                "SELECT COUNT(*) FROM likes WHERE postid=?", post['id'])
            post['likes_count'] = likes[0]['COUNT(*)']
            # https://www.programiz.com/python-programming/datetime/strptime
            post['timestamp'] = datetime.datetime.strptime(
                post['timestamp'], '%Y-%m-%d %H:%M:%S')
            post['timestamp'] = post['timestamp'].strftime(
                '%B %d, %Y, %I:%M %p')

            if post['path'].endswith(('mp4', 'avi', 'mov')):
                post['is_video'] = True
            else:
                post['is_video'] = False

    return render_template("index.html", posts=posts)


@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    """Delete a post"""
    # Check if the post belongs to the current user
    post = db.execute("SELECT * FROM posts WHERE id=?", post_id)
    if post and post[0]['userid'] == session["user_id"]:
        # Delete the post from the database
        db.execute("DELETE FROM posts WHERE id=?", post_id)

        # Delete the associated file
        filepath = f"{post[0]['userid']}_{post_id}"
        file_extension = os.path.splitext(filepath)[1]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{
                                post[0]['userid']}_{post_id}{file_extension}")
        if os.path.exists(filepath):
            os.remove(filepath)

        # Redirect to the index page
        return redirect("/")
    else:
        # Post not found or user is not authorized
        return apology("Delete failed", 400)

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    """Delete a comment"""
    # Check if the comment belongs to the current user
    comment = db.execute("SELECT * FROM comments WHERE id=?", comment_id)
    if comment and comment[0]['userid'] == session["user_id"]:
        # Delete the comment from the database
        db.execute("DELETE FROM comments WHERE id=?", comment_id)
        # Redirect to the current post page
        return redirect(f"/post/{comment[0]['postid']}")
    else:
        # Comment not found or user is not authorized
        return apology("Delete failed", 400)


@app.route('/like/<int:post_id>', methods=['GET'])
def like_post(post_id):
    """Like a post"""
    user_id = session["user_id"]
    existing_like = db.execute(
        "SELECT * FROM likes WHERE postid=? AND userid=?", post_id, user_id)
    if existing_like:
        # Unlike the post (delete the like entry)
        db.execute("DELETE FROM likes WHERE postid=? AND userid=?",
                   post_id, user_id)
        total_likes = db.execute(
            "SELECT COUNT(*) AS total_likes FROM likes WHERE postid=?", post_id)[0]['total_likes']
        return jsonify({'success': True, 'total_likes': total_likes, 'user_liked': False})
    else:
        # Like the post (insert a new like entry)
        db.execute(
            "INSERT INTO likes (userid, postid) VALUES (?, ?)", user_id, post_id)
        total_likes = db.execute(
            "SELECT COUNT(*) AS total_likes FROM likes WHERE postid=?", post_id)[0]['total_likes']
        return jsonify({'success': True, 'total_likes': total_likes, 'user_liked': True})


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    """Upload file"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        title = request.form.get("title")
        body = request.form.get("body")
        filename = ""

        if 'file' not in request.files:
            return apology("No file part", 400)
        file = request.files['file']
        if not file.filename or not title or not body:
            return apology("Empty field(s)", 400)
        if file and allowed_file(file.filename):
            # Update the posts table
            db.execute("INSERT INTO posts (userid, title, body) VALUES(:id, :title, :body)",
                       id=session["user_id"], title=title, body=body)

            # Retrieve the id of the newly inserted post
            post_id = db.execute("SELECT last_insert_rowid()")[
                0]["last_insert_rowid()"]
            file_extension = os.path.splitext(file.filename)[1]
            # Generate filepath using post ID
            # Prefix filename with post_id, postfix with file extension
            filename = f"{session["user_id"]}_{post_id}{file_extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Update the path column of the corresponding post record
            db.execute("UPDATE posts SET path = :filepath WHERE id = :post_id",
                       filepath=filepath, post_id=post_id)
            flash("Post uploaded successfully.")
            # Redirect user to home page
            return redirect("/")
        else:
            return apology("File type not allowed", 400)

    return render_template("upload.html")

@app.route("/comment/<int:post_id>/<int:user_id>", methods=["POST"])
@login_required
def comment(post_id, user_id):
    """Comment on post"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        body = request.form.get("body")
        if user_id == session["user_id"]:
            if not body:
                return apology("Empty Comment", 400)
            # Update the posts table
            db.execute("INSERT INTO comments (userid, postid, comment) VALUES(:user_id, :post_id, :body)",
                        user_id=user_id, post_id=post_id, body=body)
            flash("Commented successfully.")
            # Redirect user to post
            return redirect(f"/post/{post_id}")
        else:
            return apology("You can't comment for other users!", 400)

    return redirect(f"/post/{post_id}")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get(
                "username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Validate submission
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username or not password or not confirmation:  # if empty fields
            return apology("Empty field(s)", 400)
        if password != confirmation:
            return apology("Passwords don't match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("Username is taken", 400)

        # Remember registrant
        hash = generate_password_hash(password)
        rows = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)

        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    return render_template("register.html")
