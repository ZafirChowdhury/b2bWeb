from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import timedelta
from base64 import b64encode

import database
import helper
import key

MAX_IAMGE_SIZE = 512 * 1024

app = Flask(__name__)

# Session Setup
app.secret_key = key.get_flask_secret_key()
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        # If user is not logedin redirrect to login
        if not session.get("user_id", None):
            return redirect(url_for("login"))
        
        listings = database.get("SELECT * FROM listings WHERE sold = %s AND user_id != %s ORDER BY listing_id DESC LIMIT 20", 
                                (False, session.get("user_id")))

        return render_template("home.html", listings=listings)
        
    if request.method == "POST":
        query = request.form.get("query", None)

        if not query:
            return redirect(url_for("apology", em="Missign Query"))

        if len(query) < 3:
            return redirect(url_for("apology", em="Search query must have at leat 3 chracters"))

        listings = database.get("SELECT * FROM listings WHERE title LIKE %s AND user_id != %s", ("%" + str(query) +"%", session.get("user_id")))

        if len(listings) == 0:
            listings = None

        return render_template("/listings.html", listings=listings, page_title="Search")


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
            return redirect(url_for("apology", em="Please fill all the requred fields."))
        
        if password != password_again:
            return redirect(url_for("apology", em="Confermation password dose not match."))

        # Check Username or email is already exist
        user_list = database.get("SELECT * FROM users WHERE user_name = %s or email = %s", (user_name, email))
        if len(user_list) >= 1:
            return redirect(url_for("apology", em="Username allready taken or email allready in use."))

        # Hasing the passowrd and saving the user to the database
        database.save("INSERT INTO users (user_name, email, password_hash) VALUES (%s, %s, %s)", (user_name, email, str(generate_password_hash(password))))

        return redirect("login")
        
# Update
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "GET":
        return render_template("/login.html")
    
    if request.method == "POST":
        user_name = request.form.get("user_name", None)
        password = request.form.get("password", None)

        if not user_name or not password:
            return redirect(url_for("apology", em="Please fill all the requred fields"))

        # Check if the user exists or not
        user_list =  database.get("SELECT * FROM users WHERE user_name = %s or email = %s", (user_name, user_name))
        if len(user_list) == 0:
            return redirect(url_for("apology", em="Username or Email dose not exist"))
        
        # Checking Password
        user = user_list[0]
        if check_password_hash(user.get("password_hash"), password):
            session["user_id"] = user.get("user_id")
            session["is_admin"] = user.get("is_admin")
            return redirect(url_for("index"))
        else:
            return redirect(url_for("apology", em="Wrong Password"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("login")
    
# em = Error Massage
@app.route("/apology")
def apology():
    return f"<h1>{request.args.get("em", "No Error")}</h1>"


@app.route("/new_listing", methods=["GET", "POST"])
def new_listing():
    if not session.get("user_id", None):
        return redirect(url_for("login"))

    if request.method == "GET":
        tag_list = database.get("SELECT * FROM tags", ()) # [{tag : "tag1"}, {tag : "tag2"}]
        return render_template("new_listing.html", tag_list=tag_list)
    
    if request.method == "POST":
        title = request.form.get("title", None)
        description = request.form.get("description", None)
        price = request.form.get("price", None)
        image = request.files.get("image", None)
        auction_end_time = request.form.get("auction_end_time", None)
        tag = request.form.get("tag", None)

        if not title or not description or not price or not tag:
            return redirect(url_for("apology", em="Please fill all the requred fiedls."))
        
        # Checking and converting price
        price = helper.check_is_float_and_convert(price)
        if not price:
            return redirect(url_for("apology", em="Wrong Price Format"))

        if image:
            if image.mimetype not in ["image/jpeg", "image/png"]:
                return redirect(url_for("apology", em="Invalid image format, only png and jpeg are allowed"))
            
            if len(image.read()) > MAX_IAMGE_SIZE:
                return redirect(url_for("apology", em="Image size exedes 512KB."))
            
            image.seek(0)
            image_url = helper.upload_image_to_imgbb(b64encode(image.read()))
        else:
            image_url = ""

        if auction_end_time:
            auction_end_time = helper.convert_html_date_time_to_python_datetime(auction_end_time)
            database.save("INSERT INTO listings (user_id, title, description, price, image_url, auction_end_time, tag) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                          (session.get("user_id", 0), title, description, price, image_url, auction_end_time, tag))

        else:
            database.save("INSERT INTO listings (user_id, title, description, price, image_url, tag) VALUES (%s, %s, %s, %s, %s, %s)", 
                          (session.get("user_id", 0),title, description, price, image_url, tag))
        
        # Getting the id of listing
        listing_id = database.get("SELECT * FROM listings ORDER BY listing_id DESC LIMIT 1", ())[0].get("listing_id")

        return redirect(url_for("view_listing", listing_id=listing_id))


@app.route("/view_listing/<int:listing_id>", methods=["GET", "POST"])
def view_listing(listing_id):
    if not session.get("user_id", None):
            return redirect(url_for("login"))
    
    if request.method == "GET":
        listings = database.get("SELECT * FROM listings WHERE listing_id = %s", (listing_id, ))
        
        if len(listings) == 0:
            return redirect(url_for("apology", em="Listing dose not exist"))
        
        return render_template("/view_listing.html", listing=listings[0])
        
    # Bidding System
    if request.method == "POST":
        return f"TOOD : Bidding System POST : You are trying to bid on {listing_id}" 


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("user_id", None):
            return redirect(url_for("login"))
    
    if request.method == "GET":
        user = database.get("SELECT * FROM users WHERE user_id = %s", (session.get("user_id"), ))[0]
        return render_template("/profile.html", user=user)

    if request.method == "FPOST":
        return "TODO : Profile POST"


@app.route("/my_listings", methods=["GET"])
def my_listings():
    if not session.get("user_id", None):
            return redirect(url_for("login"))

    listings = database.get("SELECT * FROM listings WHERE user_id = %s ORDER BY listing_id DESC", (session.get("user_id"), ))
    return render_template("/listings.html", listings=listings, page_title="My Listings")


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("user_id", None):
            return redirect(url_for("login"))
    
    if not session.get("is_admin"):
        return redirect(url_for("apology"), em="Acess denied")

    if request.method == "GET":
        return "TODO : Admin GET"
    
    if request.method == "POST":
        return "TODO : Admin POST"
    

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if not session.get("user_id", None):
        return redirect("login")

    if request.method == "GET":
        return render_template("/edit_profile.html")

    if request.method == "POST":
        return "TODO : EDIT PROFILE POST"


@app.route("/tag/<tag>", methods=["GET"])
def tag(tag):
    if not session.get("user_id", None):
            return redirect(url_for("login"))

    if not tag:
        return redirect(url_for("apology", em="Tag dose not exist"))

    listings = database.get("SELECT * FROM listings WHERE tag = %s ORDER BY listing_id DESC", (tag , ))
    return render_template("/listings.html", listings=listings, page_title="My Listings")
