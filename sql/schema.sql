CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    user_name VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,

    location VARCHAR(255),
    phone_number VARCHAR(13),
    user_image_link VARCHAR(512),
    report INT NOT NULL DEFAULT 0,

    PRIMARY KEY (user_id)
);

CREATE TABLE profile_reviews (
    review_id INT NOT NULL AUTO_INCREMENT,
    profile_id INT,
    reviewer_id INT,

    review VARCHAR(2048),
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (review_id),
    FOREIGN KEY (profile_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (review_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE listings (
    listing_id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    sold_to INT,

    title VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    sold BOOLEAN NOT NULL DEFAULT FALSE,
    ended_before_any_bids BOOLEAN NOT NULL DEFAULT FALSE,
    description VARCHAR(6000) NOT NULL,
    tag VARCHAR(255) NOT NULL,

    image_url VARCHAR(512),
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    auction_end_time TIMESTAMP DEFAULT '2000-01-01 00:00:00',
    
    PRIMARY KEY (listing_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (sold_to) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE tags(
    tag VARCHAR(255) NOT NULL
);

CREATE TABLE bids (
    bid_id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    listing_id INT,

    ammount DECIMAL(10, 2) NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY(bid_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id) ON DELETE CASCADE
);
