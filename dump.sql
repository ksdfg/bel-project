-- MySQL dump 10.13  Distrib 8.0.16, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: beldb
-- ------------------------------------------------------
-- Server version	8.0.16

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
 SET NAMES utf8mb4 ;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `complaint`
--

DROP TABLE IF EXISTS `complaint`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `complaint` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Machine` int(11) NOT NULL,
  `Status` enum('Open','Closed') NOT NULL,
  `Description` varchar(250) NOT NULL,
  `MadeOn` datetime NOT NULL,
  `AttendedOn` datetime NOT NULL,
  `Engineer` int(11) DEFAULT NULL,
  `ClosedOn` datetime DEFAULT NULL,
  `Remarks` varchar(250) DEFAULT NULL,
  `Priority` enum('High','Medium','Low') NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_complaint_eng` (`Engineer`),
  KEY `fk_complaint_machine` (`Machine`),
  CONSTRAINT `fk_complaint_eng` FOREIGN KEY (`Engineer`) REFERENCES `engineer` (`ID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_complaint_machine` FOREIGN KEY (`Machine`) REFERENCES `machine` (`SlNo`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaint`
--

LOCK TABLES `complaint` WRITE;
/*!40000 ALTER TABLE `complaint` DISABLE KEYS */;
INSERT INTO `complaint` (`ID`, `Machine`, `Status`, `Description`, `MadeOn`, `AttendedOn`, `Engineer`, `ClosedOn`, `Remarks`, `Priority`) VALUES (1,101,'Closed','Equipment not working','2019-11-03 06:37:20','2019-11-02 09:37:27',1,'2019-11-03 06:38:11','Replaced XDAQ card','Low'),(2,102,'Open','Nothing happens','2019-10-30 06:42:15','2019-10-30 10:42:28',5,NULL,NULL,'High');
/*!40000 ALTER TABLE `complaint` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `complaint_material`
--

DROP TABLE IF EXISTS `complaint_material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `complaint_material` (
  `Complaint` int(11) NOT NULL,
  `PartNo` bigint(12) NOT NULL,
  `Qty` float NOT NULL,
  `Status` enum('Pending','Delivered') NOT NULL,
  PRIMARY KEY (`Complaint`,`PartNo`),
  KEY `fk_complaint_material_part` (`PartNo`),
  CONSTRAINT `fk_complaint_material_comp` FOREIGN KEY (`Complaint`) REFERENCES `complaint` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_complaint_material_part` FOREIGN KEY (`PartNo`) REFERENCES `material` (`PartNo`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `complaint_material`
--

LOCK TABLES `complaint_material` WRITE;
/*!40000 ALTER TABLE `complaint_material` DISABLE KEYS */;
INSERT INTO `complaint_material` (`Complaint`, `PartNo`, `Qty`, `Status`) VALUES (1,123456789123,1,'Delivered'),(2,198765432109,1,'Pending');
/*!40000 ALTER TABLE `complaint_material` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `customer` (
  `ID` int(11) NOT NULL,
  `Name` varchar(50) NOT NULL,
  `ContactPerson` varchar(30) DEFAULT NULL,
  `ContactNo` bigint(10) DEFAULT NULL,
  `email` varchar(30) NOT NULL,
  `Address` varchar(200) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` (`ID`, `Name`, `ContactPerson`, `ContactNo`, `email`, `Address`) VALUES (101,'J&K Police',NULL,NULL,'jkpolice@police.gov.in','Jammu and Kashmir'),(102,'Gujrat Police',NULL,NULL,'gujpolice@police.gov.in','Ahmadabad');
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eng_material`
--

DROP TABLE IF EXISTS `eng_material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `eng_material` (
  `Engineer` int(11) NOT NULL,
  `PartNo` bigint(12) NOT NULL,
  `Qty` float NOT NULL,
  PRIMARY KEY (`Engineer`,`PartNo`),
  KEY `fk_eng_material_part` (`PartNo`),
  CONSTRAINT `fk_eng_material_eng` FOREIGN KEY (`Engineer`) REFERENCES `engineer` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_eng_material_part` FOREIGN KEY (`PartNo`) REFERENCES `material` (`PartNo`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eng_material`
--

LOCK TABLES `eng_material` WRITE;
/*!40000 ALTER TABLE `eng_material` DISABLE KEYS */;
INSERT INTO `eng_material` (`Engineer`, `PartNo`, `Qty`) VALUES (5,123456789123,3);
/*!40000 ALTER TABLE `eng_material` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eng_scrap`
--

DROP TABLE IF EXISTS `eng_scrap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `eng_scrap` (
  `Engineer` int(11) NOT NULL,
  `PartNo` bigint(12) NOT NULL,
  `Qty` float DEFAULT NULL,
  PRIMARY KEY (`Engineer`,`PartNo`),
  KEY `fk_eng_scrap_part` (`PartNo`),
  CONSTRAINT `fk_eng_scrap_eng` FOREIGN KEY (`Engineer`) REFERENCES `engineer` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_eng_scrap_part` FOREIGN KEY (`PartNo`) REFERENCES `material` (`PartNo`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eng_scrap`
--

LOCK TABLES `eng_scrap` WRITE;
/*!40000 ALTER TABLE `eng_scrap` DISABLE KEYS */;
INSERT INTO `eng_scrap` (`Engineer`, `PartNo`, `Qty`) VALUES (1,123456789123,1);
/*!40000 ALTER TABLE `eng_scrap` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `engineer`
--

DROP TABLE IF EXISTS `engineer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `engineer` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(30) NOT NULL,
  `ContactNo` bigint(10) NOT NULL,
  `email` varchar(50) NOT NULL,
  `Region` varchar(2) NOT NULL,
  `Address` varchar(200) NOT NULL,
  `Username` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `fk_engineer_user` (`Username`),
  KEY `fk_engineer_reg` (`Region`),
  CONSTRAINT `fk_engineer_reg` FOREIGN KEY (`Region`) REFERENCES `reg_center` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_engineer_user` FOREIGN KEY (`Username`) REFERENCES `user` (`username`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `engineer`
--

LOCK TABLES `engineer` WRITE;
/*!40000 ALTER TABLE `engineer` DISABLE KEYS */;
INSERT INTO `engineer` (`ID`, `Name`, `ContactNo`, `email`, `Region`, `Address`, `Username`) VALUES (1,'Generic Name',9876543210,'generic@contractor.com','NR','Srinagar','geneng'),(2,'Akash',98123847560,'akash@contractor.com','NR','Agra','akasheng'),(5,'Mr. Patel',9584736201,'patel@contractor.com','WR','Surat','pateleng'),(6,'Mr. Iyengar',9678123465,'iyengar@contractor.com','SR','Mysore','iyeng');
/*!40000 ALTER TABLE `engineer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `machine`
--

DROP TABLE IF EXISTS `machine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `machine` (
  `SlNo` int(11) NOT NULL,
  `Model` varchar(10) NOT NULL,
  `CustID` int(11) DEFAULT NULL,
  `Status` varchar(20) NOT NULL,
  `InstallDate` date NOT NULL,
  `InstalledBy` int(11) DEFAULT NULL,
  `AllocatedTo` int(11) DEFAULT NULL,
  `WarrantyExp` date NOT NULL,
  `AMCStart` date NOT NULL,
  `AMCExp` date NOT NULL,
  `Location` varchar(200) NOT NULL,
  PRIMARY KEY (`SlNo`),
  KEY `fk_machine_cust` (`CustID`),
  KEY `fk_machine_installby` (`InstalledBy`),
  CONSTRAINT `fk_machine_cust` FOREIGN KEY (`CustID`) REFERENCES `customer` (`ID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_machine_installby` FOREIGN KEY (`InstalledBy`) REFERENCES `engineer` (`ID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `machine`
--

LOCK TABLES `machine` WRITE;
/*!40000 ALTER TABLE `machine` DISABLE KEYS */;
INSERT INTO `machine` (`SlNo`, `Model`, `CustID`, `Status`, `InstallDate`, `InstalledBy`, `AllocatedTo`, `WarrantyExp`, `AMCStart`, `AMCExp`, `Location`) VALUES (101,'xbis-1',101,'Active','2017-05-14',1,1,'2018-05-13','2018-05-14','2022-05-13','Gandoh Bhalessa, Jammu and Kashmir 182203'),(102,'xbis-2',102,'Down','2017-11-03',5,5,'2018-11-02','2018-11-03','2019-11-02','Surat, Gujrat, India');
/*!40000 ALTER TABLE `machine` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `material`
--

DROP TABLE IF EXISTS `material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `material` (
  `PartNo` bigint(12) NOT NULL,
  `Desc` varchar(50) NOT NULL,
  `Unit` enum('L','NO','M') NOT NULL,
  `Price` float(10,3) NOT NULL,
  PRIMARY KEY (`PartNo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `material`
--

LOCK TABLES `material` WRITE;
/*!40000 ALTER TABLE `material` DISABLE KEYS */;
INSERT INTO `material` (`PartNo`, `Desc`, `Unit`, `Price`) VALUES (123456789123,'XDAQ','NO',400.120),(198765432109,'ECU','NO',500.000);
/*!40000 ALTER TABLE `material` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pm`
--

DROP TABLE IF EXISTS `pm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `pm` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Machine` int(11) DEFAULT NULL,
  `Date` date NOT NULL,
  `Engineer` int(11) DEFAULT NULL,
  `Remarks` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_prev_maintainence_eng` (`Engineer`),
  KEY `fk_prev_maintainenece_machine` (`Machine`),
  CONSTRAINT `fk_prev_maintainence_eng` FOREIGN KEY (`Engineer`) REFERENCES `engineer` (`ID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_prev_maintainenece_machine` FOREIGN KEY (`Machine`) REFERENCES `machine` (`SlNo`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pm`
--

LOCK TABLES `pm` WRITE;
/*!40000 ALTER TABLE `pm` DISABLE KEYS */;
INSERT INTO `pm` (`ID`, `Machine`, `Date`, `Engineer`, `Remarks`) VALUES (44,101,'2017-08-14',1,NULL),(45,101,'2017-11-14',1,NULL),(46,101,'2018-02-14',1,NULL),(47,101,'2018-05-14',1,NULL),(48,101,'2018-08-14',1,NULL),(49,101,'2018-11-14',1,NULL),(50,101,'2019-02-14',1,NULL),(51,101,'2019-05-14',1,NULL),(52,101,'2019-08-14',1,NULL),(53,102,'2018-02-03',5,NULL),(54,102,'2018-05-03',5,NULL),(55,102,'2018-08-03',5,NULL),(56,102,'2018-11-03',5,NULL),(57,102,'2019-02-03',5,NULL),(58,102,'2019-05-03',5,NULL),(59,102,'2019-08-03',5,NULL);
/*!40000 ALTER TABLE `pm` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pm_material`
--

DROP TABLE IF EXISTS `pm_material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `pm_material` (
  `PM` int(11) NOT NULL,
  `PartNo` bigint(12) NOT NULL,
  `Qty` float NOT NULL,
  `status` varchar(10) NOT NULL,
  PRIMARY KEY (`PM`,`PartNo`),
  KEY `fk_pm_material_part` (`PartNo`),
  CONSTRAINT `fk_pm_material_part` FOREIGN KEY (`PartNo`) REFERENCES `material` (`PartNo`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_pm_material_used_pm` FOREIGN KEY (`PM`) REFERENCES `pm` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pm_material`
--

LOCK TABLES `pm_material` WRITE;
/*!40000 ALTER TABLE `pm_material` DISABLE KEYS */;
/*!40000 ALTER TABLE `pm_material` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reg_center`
--

DROP TABLE IF EXISTS `reg_center`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `reg_center` (
  `ID` varchar(2) NOT NULL,
  `Address` varchar(200) NOT NULL,
  `username` varchar(10) NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_reg_center_user` (`username`),
  CONSTRAINT `fk_reg_center_user` FOREIGN KEY (`username`) REFERENCES `user` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reg_center`
--

LOCK TABLES `reg_center` WRITE;
/*!40000 ALTER TABLE `reg_center` DISABLE KEYS */;
INSERT INTO `reg_center` (`ID`, `Address`, `username`) VALUES ('ER','Kolkata','er_admin'),('NR','Delhi','nr_admin'),('SR','Bengaluru','sr_admin'),('WR','Mumbai','wr_admin');
/*!40000 ALTER TABLE `reg_center` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reg_materials`
--

DROP TABLE IF EXISTS `reg_materials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `reg_materials` (
  `Region` varchar(2) NOT NULL,
  `PartNo` bigint(12) NOT NULL,
  `Qty` float NOT NULL,
  PRIMARY KEY (`Region`,`PartNo`),
  KEY `fk_reg_materials_part` (`PartNo`),
  CONSTRAINT `fk_reg_materials_part` FOREIGN KEY (`PartNo`) REFERENCES `material` (`PartNo`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_reg_materials_reg` FOREIGN KEY (`Region`) REFERENCES `reg_center` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reg_materials`
--

LOCK TABLES `reg_materials` WRITE;
/*!40000 ALTER TABLE `reg_materials` DISABLE KEYS */;
/*!40000 ALTER TABLE `reg_materials` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reg_scrap`
--

DROP TABLE IF EXISTS `reg_scrap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `reg_scrap` (
  `Region` varchar(2) NOT NULL,
  `PartNo` bigint(12) NOT NULL,
  `Qty` float NOT NULL,
  PRIMARY KEY (`Region`,`PartNo`),
  KEY `fk_reg_scrap_part` (`PartNo`),
  CONSTRAINT `fk_reg_scrap_part` FOREIGN KEY (`PartNo`) REFERENCES `material` (`PartNo`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_reg_scrap_reg` FOREIGN KEY (`Region`) REFERENCES `reg_center` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reg_scrap`
--

LOCK TABLES `reg_scrap` WRITE;
/*!40000 ALTER TABLE `reg_scrap` DISABLE KEYS */;
INSERT INTO `reg_scrap` (`Region`, `PartNo`, `Qty`) VALUES ('NR',123456789123,4);
/*!40000 ALTER TABLE `reg_scrap` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
 SET character_set_client = utf8mb4 ;
CREATE TABLE `user` (
  `username` varchar(10) NOT NULL,
  `password` varchar(30) NOT NULL,
  `role` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` (`username`, `password`, `role`) VALUES ('akasheng','singh','engineer'),('er_admin','east','reg_mgr'),('geneng','password','engineer'),('iyeng','sweets','engineer'),('ksdfg','123','bel_mgr'),('nr_admin','north','reg_mgr'),('pateleng','gujju','engineer'),('snd','ksh31jan','bel_mgr'),('sr_admin','south','reg_mgr'),('wr_admin','west','reg_mgr');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-11-04 22:47:29
