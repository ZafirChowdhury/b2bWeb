from flask import Flask, request, render_template, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import timedelta, datetime
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

        listings = database.get("SELECT * FROM listings WHERE title LIKE %s AND user_id != %s", 
                                ("%" + str(query) +"%", session.get("user_id")))

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
        user_list = database.get("SELECT * FROM users WHERE user_name = %s or email = %s", 
                                 (user_name, email))
        
        if len(user_list) >= 1:
            return redirect(url_for("apology", em="Username allready taken or email allready in use."))

        # Hasing the passowrd and saving the user to the database
        database.save("INSERT INTO users (user_name, email, password_hash) VALUES (%s, %s, %s)", 
                      (user_name, email, str(generate_password_hash(password))))

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

        # TODO : Move to a helper fuction
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


@app.route("/view_listing/<int:listing_id>", methods=["GET"])
def view_listing(listing_id):
    if not listing_id:
        return redirect(url_for("apology", em="Missing URL paramiters"))

    if not session.get("user_id", None):
            return redirect(url_for("login"))
    
    if request.method == "GET":
        listings = database.get("SELECT * FROM listings WHERE listing_id = %s", (listing_id, ))
        
        if len(listings) == 0:
            return redirect(url_for("apology", em="Listing dose not exist"))
        
        listing = listings[0]

        # Checking auction time
        auction_end_time = listing.get("auction_end_time")
        defult_no_end_time = datetime(2000, 1, 1, 0, 0, 0)
        current_time = datetime.now()

        # Update to sold, if time has ended
        if not auction_end_time == defult_no_end_time: # There is a user given time
            if auction_end_time < current_time: # Auction has ended
                # Getting user_id of the hiest bidder
                bids = database.get("SELECT user_id FROM bids WHERE listing_id = %s ORDER BY ammount ASC", 
                            (listing_id, ))

                if len(bids) == 0:
                    sold_to = session.get("user_id")
                    database.save("UPDATE listings SET sold_to = %s, sold = %s, ended_before_any_bids = %s WHERE listing_id = %s",
                            (sold_to, True, True,listing_id))
                else:
                    sold_to = bids[0].get("user_id")
                    database.save("UPDATE listings SET sold_to = %s, sold = %s WHERE listing_id = %s",
                            (sold_to, True, listing_id))

        return render_template("/view_listing.html", listing=listing)


@app.route("/bid/<int:listing_id>", methods=["POST"])
def bid(listing_id):
    if not listing_id:
        return redirect(url_for("apology", em="Missing URL paramiters"))

    if not session.get("user_id", None):
            return redirect(url_for("login"))
    
    bid_ammout = helper.check_is_float_and_convert(request.form.get("bid_amount"))

    if not bid_ammout:
        return redirect(url_for("apology", em="Please enter valid bid ammout"))
    
    listings = database.get("SELECT sold, user_id FROM listings WHERE listing_id = %s", (listing_id, ))

    # Listing dose not exist
    if len(listings) == 0:
        return redirect(url_for("apology", em="Listing dose not exist"))
    
    # Listing is sold 
    if listings[0].get("sold"):
        return redirect(url_for("apology", em="Listing is sold"))
    
    if listings[0].get("user_id") == session.get("user_id"):
        return redirect(url_for("apology", em="You cannont bid on your own listing"))

    database.save("INSERT INTO bids (user_id, listing_id, ammount) VALUES (%s, %s, %s)", 
                  (session.get("user_id"), listing_id, bid_ammout))
    
    database.save("UPDATE listings SET price = %s WHERE listing_id = %s", 
                  (bid_ammout, listing_id))

    return redirect(url_for("view_listing", listing_id=listing_id))


@app.route("/end_listing/<int:listing_id>", methods=["POST"])
def end_listing(listing_id):
    if not listing_id:
        return redirect(url_for("apology", em="Missing URL paramieters"))
    
    if not session.get("user_id"):
        return redirect(url_for("login"))

    listings = database.get("SELECT user_id FROM listings WHERE listing_id = %s", (listing_id, ))

    if len(listings) == 0:
        return redirect(url_for("apology", em="Listing dose not exist"))
    
    if listings[0].get("user_id") != session.get("user_id"):
        return redirect(url_for("apology", em="Only owners can end a listing"))
    
    # Getting user_id of the hiest bidder
    bids = database.get("SELECT user_id FROM bids WHERE listing_id = %s ORDER BY ammount ASC", 
                (listing_id, ))

    if len(bids) == 0:
        sold_to = session.get("user_id")
        database.save("UPDATE listings SET sold_to = %s, sold = %s, ended_before_any_bids = %s WHERE listing_id = %s",
                (sold_to, True, True,listing_id))
    else:
        sold_to = bids[0].get("user_id")
        database.save("UPDATE listings SET sold_to = %s, sold = %s WHERE listing_id = %s",
                (sold_to, True, listing_id))
    
    return redirect(url_for("view_listing", listing_id=listing_id))


@app.route("/profile/<int:user_id>", methods=["GET", "POST"])
def profile(user_id):
    if not session.get("user_id", None):
            return redirect(url_for("login"))
    
    if not user_id:
        return redirect(url_for("apology", rm="Missing URL paramiters"))
    
    if request.method == "GET":
        user = database.get("SELECT * FROM users WHERE user_id = %s", (user_id, ))[0]

        # TODO Profile reiews

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
    
# TODO
@app.route("/edit_profile/<int:user_id>", methods=["GET", "POST"])
def edit_profile(user_id):
    if not user_id:
        return redirect(url_for("apology", em="Missing URL paramiters"))

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


@app.route("/delete_listing/<int:listing_id>", methods=["POST"])
def delete_listing(listing_id):
    if not session.get("user_id", None):
            return redirect(url_for("login"))
    
    if not listing_id:
        return redirect(url_for("apology", em="Missing URL paramiters"))
    
    listings = database.get("SELECT user_id FROM listings WHERE listing_id = %s",
                            (listing_id, ))
    
    if len(listings) == 0:
        return redirect(url_for("apology", em="Listing dose not exist"))
    
    if not (listings[0].get("user_id") == session.get("user_id") or session.get("is_admin")):
        return redirect(url_for("apology", em="Only listing owener or a admin can delete a listing"))
    
    database.save("DELETE FROM listings WHERE listing_id = %s",
                  (listing_id, ))
    
    return redirect(url_for("index"))


@app.route("/submit_review/<int:user_id>", methods=["POST"])
def submit_reviews(user_id):
    if not user_id:
        return redirect(url_for("apology", em="Missing URL paramiters"))
    
    if not session.get("user_id", None):
        return redirect(url_for("login"))
    
    if session.get("user_id") == user_id:
        return redirect(url_for("apology", em="You cannot review your own profile"))
    
    review = request.form.get("review")

    if not review:
        return redirect(url_for("apology", em="Review content missing"))
    
    database.save("INSERT INTO profile_reviews (profile_id, reviewer_id, review) VALUES (%s, %s, %s)",
                  (user_id, session.get("user_id"), review))
    
    return redirect("pofiles", user_id=user_id)
