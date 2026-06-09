-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: monstera
-- ------------------------------------------------------
-- Server version	9.7.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;
--

--
-- Table structure for table `environment_logs`
--

DROP TABLE IF EXISTS `environment_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `environment_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plant_id` int NOT NULL,
  `measured_at` datetime NOT NULL,
  `temperature_c` decimal(5,2) DEFAULT NULL,
  `humidity_percent` decimal(5,2) DEFAULT NULL,
  `light_hours` decimal(5,2) DEFAULT NULL,
  `fertilizer_used` tinyint(1) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`id`),
  KEY `plant_id` (`plant_id`),
  CONSTRAINT `environment_logs_ibfk_1` FOREIGN KEY (`plant_id`) REFERENCES `plants` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `environment_logs`
--

LOCK TABLES `environment_logs` WRITE;
/*!40000 ALTER TABLE `environment_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `environment_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leaves`
--

DROP TABLE IF EXISTS `leaves`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leaves` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plant_id` int NOT NULL,
  `leaf_order` int NOT NULL,
  `matured_at` date DEFAULT NULL,
  `length_cm` decimal(6,2) DEFAULT NULL,
  `width_cm` decimal(6,2) DEFAULT NULL,
  `outer_fenestration_count` int DEFAULT '0',
  `inner_fenestration_count` int DEFAULT '0',
  `notes` text,
  `matured_at_estimated` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `plant_id` (`plant_id`),
  CONSTRAINT `leaves_ibfk_1` FOREIGN KEY (`plant_id`) REFERENCES `plants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leaves`
--

LOCK TABLES `leaves` WRITE;
/*!40000 ALTER TABLE `leaves` DISABLE KEYS */;
INSERT INTO `leaves` VALUES (1,3,1,'2025-07-04',10.00,7.00,0,0,NULL,1),(2,3,2,'2025-08-15',12.00,9.00,0,0,NULL,1),(3,3,3,'2025-09-26',14.00,12.00,0,0,NULL,1),(4,3,4,'2025-11-07',15.00,14.00,1,0,NULL,1),(5,3,5,'2025-12-20',17.00,15.00,0,0,NULL,1),(6,3,6,'2026-01-31',22.00,19.00,1,0,NULL,1),(7,3,7,'2026-03-14',26.00,27.00,4,0,NULL,1),(8,3,8,'2026-04-25',30.00,35.00,7,0,NULL,0),(9,1,1,'2025-06-13',15.00,12.00,0,0,NULL,1),(10,1,2,'2025-08-15',14.00,12.00,0,0,NULL,1),(11,1,3,'2025-10-17',15.00,14.00,0,0,NULL,1),(12,1,4,'2025-12-20',21.00,17.00,2,0,NULL,1),(13,1,5,'2026-02-21',21.00,23.00,3,0,NULL,1),(14,1,6,'2026-04-25',31.00,33.00,6,0,NULL,0),(15,2,1,'2025-06-22',9.00,7.00,0,0,NULL,1),(16,2,2,'2025-08-15',11.00,8.00,0,0,NULL,1),(17,2,3,'2025-10-08',12.00,10.00,0,0,NULL,1),(18,2,4,'2025-11-30',12.00,12.00,0,0,NULL,1),(19,2,5,'2026-01-23',15.00,15.00,0,0,NULL,1),(20,2,6,'2026-03-17',19.00,20.00,0,0,NULL,1),(21,2,7,'2026-05-10',20.00,20.00,0,0,NULL,0),(22,4,1,'2025-06-09',13.00,10.00,0,0,NULL,1),(23,4,2,'2025-08-15',13.00,11.00,0,0,NULL,1),(24,4,3,'2025-10-21',17.00,16.00,1,0,NULL,1),(25,4,4,'2025-12-27',16.00,15.00,1,0,NULL,1),(26,4,5,'2026-03-04',21.00,20.00,2,0,NULL,1),(27,4,6,'2026-05-10',24.00,25.00,3,0,NULL,0),(28,5,1,'2025-08-15',16.00,13.00,0,0,NULL,1),(29,5,2,'2025-10-09',16.00,14.00,1,0,NULL,1),(30,5,3,'2025-12-02',19.00,18.00,3,0,NULL,1),(31,5,4,'2026-01-26',23.00,21.00,5,0,NULL,1),(32,5,5,'2026-03-21',26.00,23.00,7,4,NULL,1),(33,5,6,'2026-05-15',31.00,28.00,10,1,NULL,0);
/*!40000 ALTER TABLE `leaves` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plants`
--

DROP TABLE IF EXISTS `plants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cultivar` varchar(100) NOT NULL,
  `acquired_at` date DEFAULT NULL,
  `growing_medium` varchar(100) DEFAULT NULL,
  `light_type` varchar(100) DEFAULT NULL,
  `notes` text,
  `initial_leaf_order` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plants`
--

LOCK TABLES `plants` WRITE;
/*!40000 ALTER TABLE `plants` DISABLE KEYS */;
INSERT INTO `plants` VALUES (1,'Thai Constelation','2025-08-15','Deep Water Culture','Grow Light','Low variegated',2),(2,'Thai Constelation','2025-08-15','Chunky mix','West window','Medium white spots',2),(3,'Yellow Marilyn','2025-08-15','Deep Water Culture','Grow Light',NULL,2),(4,'Yellow Marilyn','2025-08-15','Chunky mix','West window',NULL,2),(5,'Mint','2025-08-15','Chunky mix','Grow Light',NULL,1),(6,'White Monster','2026-01-20','Deep Water Culture','West window',NULL,2);
/*!40000 ALTER TABLE `plants` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-08 20:27:25
