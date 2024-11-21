CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    user_name VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,

    location VARCHAR(255),
    phone_number VARCHAR(13),
    user_image_link VARCHAR(512),

    PRIMARY KEY (user_id)
);

CREATE TABLE listings (
    listing_id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    sold BOOLEAN NOT NULL DEFAULT FALSE,
    description VARCHAR(6000) NOT NULL,

    image_url VARCHAR(512),
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    auction_end_time TIMESTAMP,
    
    PRIMARY KEY (listing_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE comments (
    comment_id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    listing_id INT,
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (comment_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id) ON DELETE CASCADE
);

CREATE TABLE profile_reviews (
    review_id INT NOT NULL AUTO_INCREMENT,
    made_by_user_id INT,
    for_user_id INT,
    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (review_id),
    FOREIGN KEY (made_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (for_user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE test (
    test_id INT,
    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- RESET DATABAE
drop schema test;
create schema test;
