import logging
import MySQLdb
from upstudy.data.backends import SQLBackend
logger = logging.getLogger("upstudy")

class MySQLBackend(SQLBackend):
    SCHEMA = {
            "tables": [
                "CREATE TABLE categories (" +
                    "id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, " +
                    "name VARCHAR(64) NOT NULL UNIQUE KEY" +
                ") ENGINE=InnoDB;",

                "CREATE TABLE namespaces (" +
                    "id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, " +
                    "name VARCHAR(64) NOT NULL UNIQUE KEY" +
                ") ENGINE=InnoDB;",

                "CREATE TABLE types (" +
                    "id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, " +
                    "name VARCHAR(64) NOT NULL UNIQUE KEY" +
                ") ENGINE=InnoDB;",

                "CREATE TABLE users (" +
                    "id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, " +
                    "uuid VARCHAR(64) NOT NULL UNIQUE KEY" +
                ") ENGINE=InnoDB;",

                "CREATE TABLE survey_data (" +
                    "user_id INTEGER UNSIGNED NOT NULL, " +
                    "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE" +
                ") ENGINE=InnoDB;",

                "CREATE TABLE submission_data (" +
                    "user_id INTEGER UNSIGNED NOT NULL, " +
                    "type_id INTEGER UNSIGNED NOT NULL, " +
                    "namespace_id INTEGER UNSIGNED NOT NULL, " +
                    "category_id INTEGER UNSIGNED NOT NULL, " +
                    "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, " +
                    "FOREIGN KEY (type_id) REFERENCES types(id) ON DELETE CASCADE, " +
                    "FOREIGN KEY (namespace_id) REFERENCES namespaces(id) ON DELETE CASCADE, " +
                    "FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE" +
                ") ENGINE=InnoDB;"
            ],

            "teardown": [
                "DROP TABLE IF EXISTS submission_data CASCADE;",
                "DROP TABLE IF EXISTS survey_data CASCADE;",
                "DROP TABLE IF EXISTS categories CASCADE;",
                "DROP TABLE IF EXISTS namespaces CASCADE;",
                "DROP TABLE IF EXISTS types CASCADE;",
                "DROP TABLE IF EXISTS users CASCADE;",
            ],

            "indexes": [
            ],
    }

    SEED_DATA = {
            "categories": "INSERT IGNORE INTO categories (name) VALUES (%s);",
            "namespaces": "INSERT IGNORE INTO namespaces (name) VALUES (%s);",
            "types": "INSERT IGNORE INTO types (name) VALUES (%s);",
    }
    driver = MySQLdb
