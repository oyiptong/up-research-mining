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

                "CREATE TABLE submissions (" +
                    "id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY, " +
                    "user_id INTEGER UNSIGNED NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, " +
                    "timestamp_received TIMESTAMP NOT NULL, INDEX timestamp_received_idx USING BTREE (timestamp_received), " +
                    "timestamp_installed TIMESTAMP NOT NULL, INDEX timestamp_installed_idx USING BTREE (timestamp_installed), " +
                    "timestamp_payload TIMESTAMP NOT NULL, INDEX timestamp_payload_idx USING BTREE (timestamp_payload), " +
                    "timestamp_upload TIMESTAMP NOT NULL, INDEX timestamp_upload_idx USING BTREE (timestamp_upload), " +
                    "source VARCHAR(255) NOT NULL, INDEX source_idx USING BTREE (source), " +
                    "locale VARCHAR(255) NOT NULL, INDEX locale_idx USING BTREE (locale), " +
                    "addon_version VARCHAR(255) NOT NULL, INDEX addon_version_idx USING BTREE (addon_version), " +
                    "tld_counter TEXT NOT NULL, " +
                    "prefs TEXT NOT NULL" +
                ") ENGINE=InnoDB;",

                "CREATE TABLE submission_interests (" +
                    "user_id INTEGER UNSIGNED NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, " + # denormalize user_id
                    "submission_id INTEGER UNSIGNED NOT NULL, FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE, " +
                    "type_id INTEGER UNSIGNED NOT NULL, FOREIGN KEY (type_id) REFERENCES types(id) ON DELETE CASCADE, " +
                    "namespace_id INTEGER UNSIGNED NOT NULL, FOREIGN KEY (namespace_id) REFERENCES namespaces(id) ON DELETE CASCADE, " +
                    "category_id INTEGER UNSIGNED NOT NULL, FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE, " +
                    "day INTEGER UNSIGNED NOT NULL, INDEX day_idx USING BTREE (day), " +
                    "hostCount TEXT NOT NULL, " +
                    "PRIMARY KEY (user_id, type_id, namespace_id, category_id, day)" +
                ") ENGINE=InnoDB;"
            ],

            "teardown": [
                "DROP TABLE IF EXISTS submission_interests CASCADE;",
                "DROP TABLE IF EXISTS submissions CASCADE;",
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
