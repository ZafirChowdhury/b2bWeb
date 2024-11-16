CREATE TABLE users (
    user_id INT NOT NULL AUTO_INCREMENT,
    user_name VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    PRIMARY KEY (user_id)
);


-- RESET DATABAE
drop schema test;
create schema test;
