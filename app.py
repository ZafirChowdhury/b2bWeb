from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import save, get

app = Flask(__name__)

# Session Setup
app.secret_key = "SSS"
app.config["SESSION_TYPE"] = "filesystem"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # If user is not logedin redirrect to login
        if not session.get("user_id", None):
            return redirect(url_for("login"))
        
        return f"<h1>{session.get("user_id", "NO USER IS LOGGED IN")}</h1>"
        
    if request.method == "POST":
        return "<h1>TODO</h1>"
    

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("/register.html")
    
    if request.method == "POST":
        user_name = request.form.get("user_name", None)
        email = request.form.get("email", None)
        password = request.form.get("password", None)
        password_again = request.form.get("password_again", None)

        if not user_name or not email or not password or not password_again:
            return redirect(url_for("apology", error_massage="Please fill all the requred fields."))
        
        if password != password_again:
            return redirect(url_for("apology", error_massage="Confermation password dose not match."))

        # Check Username or email is already exist
        user_list =  get("SELECT * FROM users WHERE user_name = %s or email = %s", (user_name, email))
        if len(user_list) >= 1:
            return redirect(url_for("apology", error_massage="Username allready taken or email allready in use."))

        # Hasing the passowrd and saving the user to the database
        save("INSERT INTO users (user_name, email, password_hash) VALUES (%s, %s, %s)", (user_name, email, str(generate_password_hash(password))))

        return redirect("login")
        

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "GET":
        return render_template("/login.html")
    
    if request.method == "POST":
        user_name = request.form.get("user_name", None)
        password = request.form.get("password", None)

        if not user_name or not password:
            return redirect(url_for("apology", error_massage="Please fill all the requred fields"))

        # Check if the user exists or not
        user_list =  get("SELECT * FROM users WHERE user_name = %s or email = %s", (user_name, user_name))
        if len(user_list) == 0:
            return redirect(url_for("apology", error_massage="Username or Email dose not exist"))
        
        # Checking password
        # (id, user_name, email, password_hash) 3 = password_hash
        user = user_list[0]
        if check_password_hash(user[3], password):
            session["user_id"] = user[0]
            return redirect(url_for("index"))
        else:
            return redirect(url_for("apology", error_massage="Wrong Password"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("login")
    

@app.route("/apology")
def apology():
    return f"<h1>{request.args.get("error_massage", "No Error")}</h1>"

# TODO
# Degine Listing View Scene
# Degine Make New Listing Page 
# Make Listing Schema
# Make View Listing Page
# Make New Listing Page
 