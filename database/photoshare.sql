-- MySQL dump 10.13  Distrib 5.7.19, for Linux (x86_64)
--
-- Host: localhost    Database: photoshare
-- ------------------------------------------------------
-- Server version	5.7.19-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ALBUMS`
--

DROP TABLE IF EXISTS `ALBUMS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ALBUMS` (
  `album_id` int(11) NOT NULL AUTO_INCREMENT,
  `album_name` varchar(40) NOT NULL,
  `DOC` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`album_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `ALBUMS_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `USERS` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ALBUMS`
--

LOCK TABLES `ALBUMS` WRITE;
/*!40000 ALTER TABLE `ALBUMS` DISABLE KEYS */;
/*!40000 ALTER TABLE `ALBUMS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ASSOCIATE`
--

DROP TABLE IF EXISTS `ASSOCIATE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ASSOCIATE` (
  `photo_id` int(11) NOT NULL,
  `HASHTAG` varchar(40) NOT NULL,
  PRIMARY KEY (`photo_id`,`HASHTAG`),
  KEY `HASHTAG` (`HASHTAG`),
  CONSTRAINT `ASSOCIATE_ibfk_1` FOREIGN KEY (`HASHTAG`) REFERENCES `TAG` (`HASHTAG`) ON DELETE CASCADE,
  CONSTRAINT `ASSOCIATE_ibfk_2` FOREIGN KEY (`photo_id`) REFERENCES `PHOTOS` (`photo_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ASSOCIATE`
--

LOCK TABLES `ASSOCIATE` WRITE;
/*!40000 ALTER TABLE `ASSOCIATE` DISABLE KEYS */;
/*!40000 ALTER TABLE `ASSOCIATE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `COMMENTS`
--

DROP TABLE IF EXISTS `COMMENTS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `COMMENTS` (
  `comment_id` int(11) NOT NULL AUTO_INCREMENT,
  `CONTENT` varchar(2000) NOT NULL,
  `DOC` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `user_id` int(11) NOT NULL,
  `photo_id` int(11) NOT NULL,
  PRIMARY KEY (`comment_id`),
  KEY `user_id` (`user_id`),
  KEY `photo_id` (`photo_id`),
  CONSTRAINT `COMMENTS_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `USERS` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `COMMENTS_ibfk_2` FOREIGN KEY (`photo_id`) REFERENCES `PHOTOS` (`photo_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `COMMENTS`
--

LOCK TABLES `COMMENTS` WRITE;
/*!40000 ALTER TABLE `COMMENTS` DISABLE KEYS */;
/*!40000 ALTER TABLE `COMMENTS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FRIENDSHIP`
--

DROP TABLE IF EXISTS `FRIENDSHIP`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `FRIENDSHIP` (
  `user_id1` int(11) NOT NULL,
  `user_id2` int(11) NOT NULL,
  PRIMARY KEY (`user_id1`,`user_id2`),
  KEY `user_id2` (`user_id2`),
  CONSTRAINT `FRIENDSHIP_ibfk_1` FOREIGN KEY (`user_id1`) REFERENCES `USERS` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `FRIENDSHIP_ibfk_2` FOREIGN KEY (`user_id2`) REFERENCES `USERS` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FRIENDSHIP`
--

LOCK TABLES `FRIENDSHIP` WRITE;
/*!40000 ALTER TABLE `FRIENDSHIP` DISABLE KEYS */;
/*!40000 ALTER TABLE `FRIENDSHIP` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LIKETABLE`
--

DROP TABLE IF EXISTS `LIKETABLE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `LIKETABLE` (
  `user_id` int(11) NOT NULL,
  `photo_id` int(11) NOT NULL,
  `DOC` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`photo_id`),
  KEY `photo_id` (`photo_id`),
  CONSTRAINT `LIKETABLE_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `USERS` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `LIKETABLE_ibfk_2` FOREIGN KEY (`photo_id`) REFERENCES `PHOTOS` (`photo_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LIKETABLE`
--

LOCK TABLES `LIKETABLE` WRITE;
/*!40000 ALTER TABLE `LIKETABLE` DISABLE KEYS */;
/*!40000 ALTER TABLE `LIKETABLE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PHOTOS`
--

DROP TABLE IF EXISTS `PHOTOS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PHOTOS` (
  `photo_id` int(11) NOT NULL AUTO_INCREMENT,
  `CAPTION` varchar(200) DEFAULT NULL,
  `DATA` longblob NOT NULL,
  `album_id` int(11) NOT NULL,
  PRIMARY KEY (`photo_id`),
  KEY `album_id` (`album_id`),
  CONSTRAINT `PHOTOS_ibfk_1` FOREIGN KEY (`album_id`) REFERENCES `ALBUMS` (`album_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PHOTOS`
--

LOCK TABLES `PHOTOS` WRITE;
/*!40000 ALTER TABLE `PHOTOS` DISABLE KEYS */;
/*!40000 ALTER TABLE `PHOTOS` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TAG`
--

DROP TABLE IF EXISTS `TAG`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `TAG` (
  `HASHTAG` varchar(40) NOT NULL,
  PRIMARY KEY (`HASHTAG`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TAG`
--

LOCK TABLES `TAG` WRITE;
/*!40000 ALTER TABLE `TAG` DISABLE KEYS */;
/*!40000 ALTER TABLE `TAG` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `USERS`
--

DROP TABLE IF EXISTS `USERS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `USERS` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `GENDER` varchar(6) DEFAULT NULL,
  `EMAIL` varchar(40) DEFAULT NULL,
  `PASSWORD` varchar(40) NOT NULL,
  `DOB` date DEFAULT NULL,
  `HOMETOWN` varchar(40) DEFAULT NULL,
  `first_name` varchar(40) NOT NULL,
  `last_name` varchar(40) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `EMAIL` (`EMAIL`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `USERS`
--

LOCK TABLES `USERS` WRITE;
/*!40000 ALTER TABLE `USERS` DISABLE KEYS */;
/*!40000 ALTER TABLE `USERS` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-10-20  9:46:00
