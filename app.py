from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>TODO</h1>"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("/register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("/login.html")
    
