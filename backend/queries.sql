-- CMON 20250303 CSCI 331 queries.sql
-- storage for queries if teammates need cut/paste option
-- sample queries TODO replace with actual

-- get all users
SELECT * FROM users;

-- get all usernames
SELECT username FROM users;

-- insert new user
INSERT INTO users (username, email) VALUES (?, ?);

-- find a user by email
SELECT * FROM users WHERE email = ?;