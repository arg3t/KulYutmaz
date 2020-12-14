-- MariaDB dump 10.17  Distrib 10.4.11-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: kulyutmaz_db
-- ------------------------------------------------------
-- Server version	10.4.11-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `domain_blacklist`
--

DROP TABLE IF EXISTS `domain_blacklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain_blacklist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `domain_blacklist`
--

LOCK TABLES `domain_blacklist` WRITE;
/*!40000 ALTER TABLE `domain_blacklist` DISABLE KEYS */;
INSERT INTO `domain_blacklist` VALUES (1,'malicious-domain.xyz'),(2,'mail.kulyutmaz.com'),(7,'mail.kulyutmaz.com'),(8,'unittest.malicious.com'),(9,'test.malicious.com'),(10,'mal.malicious.com');
/*!40000 ALTER TABLE `domain_blacklist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `domain_whitelist`
--

DROP TABLE IF EXISTS `domain_whitelist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `domain_whitelist` (
  `domain` varchar(69) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `domain_whitelist`
--

LOCK TABLES `domain_whitelist` WRITE;
/*!40000 ALTER TABLE `domain_whitelist` DISABLE KEYS */;
/*!40000 ALTER TABLE `domain_whitelist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `logs`
--

DROP TABLE IF EXISTS `logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `logs` (
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `sender_domain` tinytext COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `result` int(11) DEFAULT NULL,
  `account` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mail_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `logs`
--

LOCK TABLES `logs` WRITE;
/*!40000 ALTER TABLE `logs` DISABLE KEYS */;
INSERT INTO `logs` VALUES ('2020-01-16 16:30:20','yigitcolakoglu@hotmail.com',-1,'ycolakoglu.bilisim@gmail.com',400),('2020-01-16 16:30:24','no-reply@accounts.google.com',1,'ycolakoglu.bilisim@gmail.com',399),('2020-01-16 16:30:29','no-reply@accounts.google.com',1,'ycolakoglu.bilisim@gmail.com',398),('2020-01-16 16:30:36','no-reply@accounts.google.com',1,'ycolakoglu.bilisim@gmail.com',397),('2020-01-16 16:30:38','no-reply@accounts.google.com',1,'ycolakoglu.bilisim@gmail.com',396),('2020-01-16 16:30:40','no-reply@accounts.google.com',1,'ycolakoglu.bilisim@gmail.com',395),('2020-01-16 19:31:50','yigitcolakoglu@hotmail.com',1,'ycolakoglu.bilisim@gmail.com',402),('2020-01-16 19:31:50','yigitcolakoglu@hotmail.com',1,'ycolakoglu.bilisim@gmail.com',401),('2020-01-16 19:41:59','yigitcolakoglu@hotmail.com',1,'ycolakoglu.bilisim@gmail.com',403),('2020-01-16 19:44:19','yigitcolakoglu@hotmail.com',1,'ycolakoglu.bilisim@gmail.com',404),('2020-01-16 19:56:26','yigitcolakoglu@hotmail.com',1,'ycolakoglu.bilisim@gmail.com',406),('2020-01-16 19:56:27','yigitcolakoglu@hotmail.com',1,'ycolakoglu.bilisim@gmail.com',405),('2020-01-16 20:00:07','yigitcolakoglu@hotmail.com',1,'ycolakoglu.bilisim@gmail.com',407),('2020-01-16 20:00:28','yigitcolakoglu@hotmail.com',1,'ycolakoglu.bilisim@gmail.com',408),('2020-01-16 20:03:47','yigitcolakoglu@hotmail.com',1,'ycolakoglu.bilisim@gmail.com',409);
/*!40000 ALTER TABLE `logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mail_blacklist`
--

DROP TABLE IF EXISTS `mail_blacklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mail_blacklist` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mail` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mail_blacklist`
--

LOCK TABLES `mail_blacklist` WRITE;
/*!40000 ALTER TABLE `mail_blacklist` DISABLE KEYS */;
INSERT INTO `mail_blacklist` VALUES (1,'malicious-domain.xyz'),(2,'malicious-domain.xyz'),(3,'unittester@malicious.com'),(4,'test@malicious.com'),(5,'mal@malicious.com'),(6,'test@testmail.com'),(7,'yigitcolakoglu@hotmail.com');
/*!40000 ALTER TABLE `mail_blacklist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mail_whitelist`
--

DROP TABLE IF EXISTS `mail_whitelist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mail_whitelist` (
  `mail` varchar(69) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mail_whitelist`
--

LOCK TABLES `mail_whitelist` WRITE;
/*!40000 ALTER TABLE `mail_whitelist` DISABLE KEYS */;
/*!40000 ALTER TABLE `mail_whitelist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `whitelist_domain`
--

DROP TABLE IF EXISTS `whitelist_domain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `whitelist_domain` (
  `id` int(6) unsigned NOT NULL AUTO_INCREMENT,
  `domain` varchar(420) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `whitelist_domain`
--

LOCK TABLES `whitelist_domain` WRITE;
/*!40000 ALTER TABLE `whitelist_domain` DISABLE KEYS */;
/*!40000 ALTER TABLE `whitelist_domain` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `whitelist_mail`
--

DROP TABLE IF EXISTS `whitelist_mail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `whitelist_mail` (
  `id` int(6) unsigned NOT NULL AUTO_INCREMENT,
  `mail` varchar(420) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `whitelist_mail`
--

LOCK TABLES `whitelist_mail` WRITE;
/*!40000 ALTER TABLE `whitelist_mail` DISABLE KEYS */;
/*!40000 ALTER TABLE `whitelist_mail` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-01-16 23:05:54
