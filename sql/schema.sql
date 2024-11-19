CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    user_name VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE listing (
    listing_id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(6000),
    
    PRIMARY KEY (listing_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE 
);


-- RESET DATABAE
drop schema test;
create schema test;
