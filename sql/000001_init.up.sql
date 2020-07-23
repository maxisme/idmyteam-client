CREATE TABLE IF NOT EXISTS `Members`
(
    `id`       int(11) unsigned NOT NULL AUTO_INCREMENT,
    `name`     varchar(50)      NOT NULL,
    `password` varchar(64)      NOT NULL,
    `perm`     varchar(20)      NOT NULL,
    `training` tinyint(1)       NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `name` (`name`)
) DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `Activity`
(
    `id`        int(11) unsigned              NOT NULL AUTO_INCREMENT,
    `member_id` int(11) unsigned              NOT NULL,
    `type`      enum ('TRAINED','RECOGNISED') NOT NULL,
    `time`      timestamp                     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `score`     float                                  DEFAULT NULL,
    `speed`     varchar(100)                           DEFAULT NULL,
    `num`       int(11)                                DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `member_id` (`member_id`),
    CONSTRAINT `Activity_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `Members` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `Logs`
(
    `id`      int(11) unsigned NOT NULL AUTO_INCREMENT,
    `time`    timestamp        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `message` text CHARACTER SET utf8 COLLATE utf8_bin,
    `read`    tinyint(1)       NOT NULL DEFAULT 0,
    `level`   int(2)           NOT NULL,
    PRIMARY KEY (`id`)
) DEFAULT CHARSET = utf8;

CREATE TABLE IF NOT EXISTS `Stats`
(
    `stat`  varchar(100) DEFAULT NULL,
    `info`  text,
    `value` text
) DEFAULT CHARSET = utf8;

INSERT INTO `Members` (`id`, `name`, `password`, `perm`, `training`)
VALUES (1, 'root', '$2b$12$nB2HppD58eqeF3sME3n5juCi1MHv4bY5VCbK8ar7qLsiDc8oISLJS', 3, 0); /* username: root password: root */
