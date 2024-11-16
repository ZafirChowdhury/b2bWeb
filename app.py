from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>TODO</h1>"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return "<h1>TODO : REGISTER GET METHOD</h1>"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return "<h1>TODO: LOGIN GET METHOD</h1>"
    
