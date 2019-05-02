SET FOREIGN_KEY_CHECKS=0;DROP TABLE IF EXISTS `Activity`;
CREATE TABLE `Activity` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `member_id` int(11) unsigned NOT NULL,
  `type` enum('TRAINED','RECOGNISED') NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `score` float DEFAULT NULL COMMENT 'if recognised the score is how likely it was to be that person. if trained it is ...',
  `speed` varchar(100) DEFAULT NULL COMMENT 'in seconds',
  `num` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `member_id` (`member_id`),
  CONSTRAINT `Activity_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `Members` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
DROP TABLE IF EXISTS `Logs`;
CREATE TABLE `Logs` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `message` text CHARACTER SET utf8 COLLATE utf8_bin,
  `read` tinyint(1) NOT NULL DEFAULT '0',
  `level` int(2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
DROP TABLE IF EXISTS `Members`;
CREATE TABLE `Members` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `password` varchar(64) NOT NULL,
  `perm` varchar(20) NOT NULL DEFAULT 'low',
  `training` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
DROP TABLE IF EXISTS `Stats`;
CREATE TABLE `Stats` (
  `stat` varchar(100) DEFAULT NULL,
  `info` text,
  `value` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
SET FOREIGN_KEY_CHECKS=1;
