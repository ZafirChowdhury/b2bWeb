from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import save, get

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
        user_name = request.form.get("username", None)
        email = request.form.get("email", None)
        password = request.form.get("password", None)
        password_again = request.form.get("password_again", None)

        if not user_name or not email or not password or not password_again:
            session["error_massage"] = "Please fill all the requred fields."
            return redirect("/apology")
        
        if password != password_again:
            session["error_massage"] = "Confermation password dose not match."
            return redirect("/apology")

        # Check Username or email is already exist
        query = "SELECT * FROM users WHERE user_name = %s or email = %s"
        data = (user_name, email)
        user_list =  get(query, data)
        if len(user_list) >= 1:
            session["error_massage"] = "Username allready taken or email allready in use."
            return redirect("/apology")

        # Hash the passowrds - NEXT TODO
        query = "INSERT INTO users (user_name, email, password_hash) VALUES (%s, %s, %s)"
        data = (user_name, email, password)
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
