CREATE DATABASE up_research CHARACTER SET utf8;
CREATE USER 'up'@'localhost' IDENTIFIED BY 'upandaway';
GRANT ALL PRIVILEGES ON *.* TO 'up'@'localhost';
