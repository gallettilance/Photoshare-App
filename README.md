<<<<<<< HEAD
-- Baichuan Zhou (baichuan@bu.edu)
-- Please note I didn't put any check/assertion here.
-- We talked about this in the lab: MySQL DOES NOT support 'check' 
-- I only put some very basic constraints. You should put more based on your assumption
-- THERE IS NO NEED TO FOLLOW THIS SCHEMA AS LONG AS YOUR DESIGN MAKES SENSE!

DROP DATABASE PHOTOSHARESOLUTION;
CREATE DATABASE PHOTOSHARESOLUTION;
USE PHOTOSHARESOLUTION;

-- CREATE USER TABLE
CREATE TABLE USER (
UID INT NOT NULL AUTO_INCREMENT,
GENDER VARCHAR(6),
EMAIL VARCHAR(40) UNIQUE,
PASSWORD VARCHAR(40) NOT NULL,
DOB DATE,
HOMETOWN VARCHAR(40),
FNAME VARCHAR(40) NOT NULL,
LNAME VARCHAR(40) NOT NULL,
PRIMARY KEY (UID)
);

-- CREATE FRIENDSHIP TABLE
CREATE TABLE FRIENDSHIP(
UID1 INT NOT NULL,
UID2 INT NOT NULL,
PRIMARY KEY(UID1, UID2), 
FOREIGN KEY (UID1) REFERENCES USER(UID) ON DELETE CASCADE,
FOREIGN KEY (UID2) REFERENCES USER(UID) ON DELETE CASCADE
);


-- CREATE Album TABLE (include album entity and 'own' relationship) 
CREATE TABLE ALBUM(
AID INT NOT NULL AUTO_INCREMENT,
NAME VARCHAR(40) NOT NULL,
DOC TIMESTAMP NOT NULL,
UID INT NOT NULL,
PRIMARY KEY (AID),
FOREIGN KEY (UID) REFERENCES USER(UID) ON DELETE CASCADE
);

-- CREATE Photo TABLE (include photo entity and 'contains' relationship) 
CREATE TABLE PHOTO(
PID INT NOT NULL AUTO_INCREMENT,
CAPTION VARCHAR(200),
DATA BLOB NOT NULL,
AID INT NOT NULL,
PRIMARY KEY (PID),
FOREIGN KEY (AID) REFERENCES ALBUM(AID) ON DELETE CASCADE
);

-- CREATE Comment TABLE (include comment entity and 'comment' relationship)
CREATE TABLE COMMENT(
CID INT NOT NULL AUTO_INCREMENT,
CONTENT VARCHAR(200) NOT NULL,
DOC TIMESTAMP NOT NULL,
UID INT NOT NULL,
PID INT NOT NULL,
PRIMARY KEY (CID),
FOREIGN KEY (UID) REFERENCES USER(UID) ON DELETE CASCADE,
FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);

-- CREATE THE LIKETABLE. WE CAN'T name it LIKE
CREATE TABLE LIKETABLE(
UID INT NOT NULL,
PID INT NOT NULL,
DOC TIMESTAMP NOT NULL,
PRIMARY KEY (UID, PID),
FOREIGN KEY (UID) REFERENCES USER(UID) ON DELETE CASCADE,
FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);


-- CREATE Tag TABLE 
CREATE TABLE TAG(
HASHTAG VARCHAR(40) NOT NULL,
PRIMARY KEY (HASHTAG)
);

-- CREATE Associate Table
CREATE TABLE ASSOCIATE(
PID INT NOT NULL,
HASHTAG VARCHAR(40) NOT NULL,
PRIMARY KEY (PID, HASHTAG),
FOREIGN KEY (HASHTAG) REFERENCES TAG(HASHTAG) ON DELETE CASCADE,
FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);

=======
# CS660_Project1
update on Oct14 Sat: hi Lance! In the new version I pulled, I tried the following:
1. made a separate "visit" page, to direct visitors to the page where they can search for photos. The "visit" button looks fine on the safari -- a blue button next to the sign-up button, but in chrome, it appears in the left top corner, i am not sure why.

2. in create_profile page, I add "friends", "search", "you may also like" to the list

Note: these changes I made are pretty simple and coarse, and feel free to accept or not~ I am basically learning the basics of writing html and flask, and I believe you can design it in a better way!







Hi I compared the official sql with ours, and add the following changes accordingly:
1. add ON DELETE CASCADE to the "album"--because when a user is deleted, the albums created by him/her should disappear too
2. add ON DELETE CASCADE to the "friend_with" relation, since when any part of the friendship is deleted, then this relationship should be deleted too.
3. add ON DELETE CASCADE to the "likes" relationship, since if either the user or the photo is deleted, then this relationship does not exist. 
4. The note on the official sql file says we cannot name the above relationship as "like", but should name it as "LIKETABLE"--do you know why? 


For best template rendering please execute in Google Chrome


Hi I added the pdf version of our diagram above:)
Hi to view the diagram, please go to https://www.draw.io/#Hgalletti94%2FCS660_Project1%2Fmaster%2Fdatabase%2FCS660_ERmodel_Project1.xml
>>>>>>> f48a29beff7c5fe7e1af4bcb64a0008793e64bd3
