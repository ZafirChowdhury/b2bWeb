from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import save

app = Flask(__name__)

# Session Setup
app.secret_key = "SSS"
app.config["SESSION_TYPE"] = "filesystem"

@app.route("/")
def index():
    return "<h1>TODO</h1>"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("/register.html")
    
    if request.method == "POST":
        username = request.form.get("username", None)
        email = request.form.get("email", None)
        password = request.form.get("password", None)
        password_again = request.form.get("password_again", None)

        if not username or not email or not password or not password_again:
            session["error_massage"] = "Please fill all the requred fields."
            return redirect("/apology")

        # Check Username or email is already exist
        # check if password and password_again are the same
        
        query = "INSERT INTO users (user_name, email, password_hash) VALUES (%s, %s, %s)"
        data = (username, email, password)
        save(query, data)

        return "<h1>User registered successfully</h1>"
        

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("/login.html")
    

@app.route("/apology")
def apology():
    error_massage = session.get("error_massage", "Unknone Error")
    
    if error_massage:
        del session["error_massage"]

    return f"<h1> {error_massage} </h1>"
