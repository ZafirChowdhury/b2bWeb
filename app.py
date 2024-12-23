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
    return render_template("apology.html", em=request.args.get("em", "No Error"))


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
            database.save("INSERT INTO listings (user_id, title, description, price, image_url, auction_end_time, tag, auction_end_time_flag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                          (session.get("user_id", 0), title, description, price, image_url, auction_end_time, tag, True))

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

        # Update to ended, if time has ended
        if not auction_end_time == defult_no_end_time: # There is a user given time
            if auction_end_time < current_time: # Auction has ended
                query = '''
                    UPDATE listings
                    SET ended = %s
                    WHERE listing_id = %s
                '''
                database.save(query, (listing_id, True))
                    
        # Bids
        query = '''
            SELECT bids.user_id, users.user_name, bids.date, bids.ammount 
            FROM bids
            INNER JOIN users
            ON  bids.user_id = users.user_id
            WHERE listing_id = %s
        '''
        bids = database.get(query, (listing_id, ))

        user_bids = database.get("SELECT * FROM bids WHERE listing_id = %s AND user_id = %s", (listing_id, session.get("user_id")))
        return render_template("/view_listing.html", listing=listing, bids=bids, user_bids=user_bids)


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
    
    # Change the ended flag in listings
    query = '''
            UPDATE listings
            SET ended = %s
            WHERE listing_id = %s
            '''
    database.save(query, (listing_id, True))
    
    return redirect(url_for("view_listing", listing_id=listing_id))


@app.route("/profile/<int:user_id>", methods=["GET", "POST"])
def profile(user_id):
    if not session.get("user_id", None):
            return redirect(url_for("login"))
    
    if not user_id:
        return redirect(url_for("apology", rm="Missing URL paramiters"))
    
    if request.method == "GET":
        user = database.get("SELECT * FROM users WHERE user_id = %s", (user_id, ))[0]

        # Profile Reviews
        reviews = database.get("SELECT user_name, review, date_posted, reviewer_id FROM profile_reviews INNER JOIN users ON profile_reviews.reviewer_id = users.user_id WHERE profile_id = %s ORDER BY date_posted DESC",
                               (user_id, ))

        return render_template("/profile.html", user=user, reviews=reviews)

    if request.method == "POST":
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
    

@app.route("/edit_profile/<int:user_id>", methods=["GET", "POST"])
def edit_profile(user_id):
    if not user_id:
        return redirect(url_for("apology", em="Missing URL paramiters"))

    if not session.get("user_id", None):
        return redirect("login")
    
    if not (session.get("is_admin") or session.get("user_id")) == user_id:
        return redirect(url_for("apology", em="You dont have acess."))

    if request.method == "GET":
        user = database.get("SELECT user_id, email, location, phone_number FROM users WHERE user_id = %s", (session.get("user_id"), ))[0]
        return render_template("/edit_profile.html", user=user)

    if request.method == "POST":
        email = request.form.get("email")
        phone = request.form.get("phone_number")
        location = request.form.get("location")
        profile_image = request.files.get("image")

        if email:
            user_list = database.get("SELECT * FROM users WHERE email = %s", (email, ))
            if len(user_list) > 1:
                return redirect(url_for("apology", em="Email is allready in use"))

            database.save("UPDATE users SET email = %s WHERE user_id = %s", (email, user_id))
        
        if phone:
            database.save("UPDATE users SET phone_number = %s WHERE user_id = %s", (phone, user_id))

        if location:
            database.save("UPDATE users SET location = %s WHERE user_id = %s", (location, user_id))

        if profile_image:
            if profile_image.mimetype not in ["image/jpeg", "image/png"]:
                return redirect(url_for("apology", em="Invalid image format, only png and jpeg are allowed"))
            
            if len(profile_image.read()) > MAX_IAMGE_SIZE:
                return redirect(url_for("apology", em="Image size exedes 512KB."))
            
            profile_image.seek(0)
            image_url = helper.upload_image_to_imgbb(b64encode(profile_image.read()))

            database.save("UPDATE users SET user_image_link = %s WHERE user_id = %s", (image_url, user_id))

        return redirect(url_for("profile", user_id=user_id))


@app.route("/delete_profile/<int:user_id>")
def delete_profile(user_id):
    if not session.get("user_id", None):
        return redirect(url_for("login"))
    
    if not (session.get("user_id") == user_id or session.get("is_admin")):
        return redirect(url_for("apology", em="Only user if self or a admin can delete a user"))
    
    database.save("DELETE FROM users WHERE user_id = %s", (user_id, ))

    return redirect(url_for("/"))


@app.route("/tag/<tag>", methods=["GET"])
def tag(tag):
    if not session.get("user_id", None):
            return redirect(url_for("login"))

    if not tag:
        return redirect(url_for("apology", em="Tag dose not exist"))

    listings = database.get("SELECT * FROM listings WHERE tag = %s ORDER BY listing_id DESC", (tag, ))
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
    
    return redirect(url_for("profile", user_id=user_id))


@app.route("/report_user/<int:user_id>", methods=["POST"])
def report_user(user_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    if session.get("user_id") == user_id:
        return redirect(url_for("apology", em="You cannot report yourself"))
    
    number_of_repoerts = database.get("SELECT reports FROM users WHERE user_id = %s",
                           (user_id, ))[0].get("reports")
    
    number_of_repoerts = number_of_repoerts + 1

    database.save("UPDATE users SET reports = %s WHERE user_id = %s",
                  (number_of_repoerts, user_id))

    return redirect(url_for("profile", user_id=user_id))


@app.route("/chat/<int:listing_id>/<int:buyer_id>", methods=["POST", "GET"])
def chat(listing_id, buyer_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    listings = database.get("SELECT * FROM listings WHERE listing_id = %s", (listing_id, ))
    if len(listings) == 0:
        return redirect(url_for("apology", em="Listing dose not exist"))
    
    listing = listings[0]

    # Checking user acess
    if not (listing.get("user_id") == session.get("user_id") or buyer_id == session.get("user_id")):
        return redirect(url_for("apology", em="Invalid acess"))

    # If chat dose not exist create chat and then show
    chats = database.get("SELECT * FROM chats WHERE listing_id = %s AND buyer_id = %s", (listing_id, buyer_id))
    if len(chats) == 0: 
        database.save("INSERT INTO chats (listing_id, buyer_id, seller_id) VALUES (%s, %s, %s)", (listing_id, buyer_id, listing.get("user_id")))

    # Getting chat data and messages
    chat = database.get("SELECT * FROM chats WHERE listing_id = %s AND buyer_id = %s", (listing_id, buyer_id))[0]
    messages = database.get("SELECT * FROM chat_message WHERE chat_id = %s", (chat.get("chat_id"), ))
    buyer = database.get("SELECT * FROM users WHERE user_id = %s", (buyer_id, ))[0]
    bid = database.get("SELECT * FROM bids WHERE listing_id = %s AND user_id = %s ORDER BY ammount DESC LIMIT 1", (listing_id, buyer_id)) # highest bid of the bidder for this listing
    if len(bid) == 0:
        bid = None
    else:
        bid = bid[0]

    return render_template("chat.html", chat=chat, messages=messages, bid=bid, buyer=buyer)


@app.route("/message/<int:sender_id>/<int:chat_id>/<int:buyer_id>/<int:listing_id>", methods=["POST"])
def message(sender_id, chat_id, buyer_id, listing_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    if sender_id != session.get("user_id"):
        return redirect(url_for("apology", em="Invalid acess"))
    
    text = request.form.get("message_text")

    if not text:
        return redirect(url_for("apology", em="Message content missings"))
    
    database.save("INSERT INTO chat_message (chat_id, sender_id, message_text) VALUES (%s, %s, %s)", (chat_id, sender_id, text))

    return redirect(url_for("chat", listing_id=listing_id, buyer_id=buyer_id))


@app.route("/accept_bid/<int:chat_id>", methods=["POST"])
def accept_bid(chat_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    # Check if listing owner is accepting the bid
    chat = database.get("SELECT * FROM chats WHERE chat_id = %s", (chat_id, ))[0]
    if not (session.get("user_id") == chat.get("seller_id")):
        return redirect(url_for("apology", em="Only owners can accept bids"))
    
    database.save("UPDATE chats SET bid_accepted = %s WHERE chat_id = %s", (True, chat_id))

    return redirect(url_for("chat", listing_id=chat.get("listing_id"), buyer_id=chat.get("buyer_id")))


@app.route("/pay/<int:flag>/<int:chat_id>", methods=["POST"])
def pay(flag, chat_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    if flag not in [1, 2]:
        return redirect(url_for("apology", em="Invalid Request"))
    
    chat = database.get("SELECT * FROM chats WHERE chat_id = %s", (chat_id, ))[0]
    
    if not (session.get("user_id") == chat.get("buyer_id")):
        return redirect(url_for("apology", em="Access Denied"))
    
    # 1 -> Payment made
    # Update sold status
    if flag == 1:
        # Change sold status, sold_to
        database.save("UPDATE listings SET sold = %s, sold_to = %s", (True, chat.get("buyer_id")))

    database.save("UPDATE chats SET payment_made = %s WHERE chat_id = %s", (flag, chat.get("chat_id")))

    return redirect(url_for("view_listing", listing_id=chat.get("listing_id")))


@app.route("/purchased_products", methods=["GET"])
def purchased_products():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    listings = database.get("SELECT * FROM listings WHERE sold_to = %s", (session.get("user_id"), ))

    return render_template("listings.html", listings=listings)
    

@app.route("/edit_listing/<int:listing_id>", methods=["GET", "POST"])
def edit_listing(listing_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    # Check if listing exist
    listings = database.get("SELECT * FROM listings WHERE listing_id = %s LIMIT 1", (listing_id, ))
    if len(listings) == 0:
        return redirect(url_for("apology", em="Listing dose not exist"))
    
    # Check if owner is trying to edit it
    listing = listings[0]
    if not (listing.get("user_id") == session.get("user_id")):
        return redirect(url_for("apology", em="Only owners can edit a listing"))
    
    # Check if any bid is made
    bids = database.get("SELECT * FROM bids WHERE listing_id = %s", (listing_id, ))
    if len(bids) > 0:
        return redirect(url_for("apology", em="You cannot edit a listing with bids"))
    
    if request.method == "GET":
        tags = database.get("SELECT * FROM tags", ())
        return render_template("edit_listing.html", listing=listing, tags=tags)
    
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        price = request.form.get("price")
        auction_end_time = request.form.get("auction_end_time")
        tag = request.form.get("tag")
        image = request.files.get("image")

        if title:
            database.save("UPDATE listings SET title = %s WHERE listing_id = %s", (title, listing_id))

        if description:
            database.save("UPDATE listings SET description = %s WHERE listing_id = %s", (description, listing_id))

        price = helper.check_is_float_and_convert(price)
        if price:
            database.save("UPDATE listings SET price = %s WHERE listing_id = %s", (price, listing_id))

        if auction_end_time:
            auction_end_time = helper.convert_html_date_time_to_python_datetime(auction_end_time)
            database.save("UPDATE listings SET auction_end_time = %s WHERE listing_id = %s", (auction_end_time, listing_id))

        if tag:
            database.save("UPDATE listings SET tag = %s WHERE listing_id = %s", (tag, listing_id))

        if image:
            if image.mimetype not in ["image/jpeg", "image/png"]:
                return redirect(url_for("apology", em="Invalid image format, only png and jpeg are allowed"))
            
            if len(image.read()) > MAX_IAMGE_SIZE:
                return redirect(url_for("apology", em="Image size exedes 512KB."))
            
            image.seek(0)
            image_url = helper.upload_image_to_imgbb(b64encode(image.read()))

            database.save("UPDATE listings SET image_url = %s WHERE listing_id = %s", (image_url, listing_id))

        return redirect(url_for("view_listing", listing_id=listing_id))
    

@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if not session.get("user_id"):
        return redirect(url_for("login"))   
    
    if request.method == "GET":
        return render_template("change_password.html")
    
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not current_password or not new_password or not confirm_password:
            return redirect(url_for("apology", em="Fill all the requred fields"))
        
        if new_password != confirm_password:
            return redirect(url_for("Confermation password dose not match"))
        
        password_hash = database.get("SELECT password_hash FROM users WHERE user_id = %s", (session.get("user_id"), ))[0].get("password_hash")

        if not check_password_hash(password_hash, current_password):
            return redirect(url_for("apology", em="Wrong Password"))
        
        database.save("UPDATE users SET password_hash = %s WHERE user_id = %s", (generate_password_hash(new_password), session.get("user_id")))

        return redirect(url_for("profile", user_id=session.get("user_id")))
