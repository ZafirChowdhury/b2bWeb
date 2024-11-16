from flask import Flask, request, render_template

from database import save

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>TODO</h1>"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("/register.html")
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_again = request.form.get("password_again")

        return f"<h1>{username} {email} {password} {password_again}</h1>"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("/login.html")
    
