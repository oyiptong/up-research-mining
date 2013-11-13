import psycopg2
import logging
logger = logging.getLogger("upstudy")

class PostgresBackend(object):

    SETUP_SQL = [
            "CREATE TABLE IF NOT EXISTS interests (id SERIAL PRIMARY KEY, namespace TEXT, name TEXT)",
            "CREATE UNIQUE INDEX ON interests (namespace, name)",
            "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, uuid TEXT, download_source TEXT, locale TEXT)",
            "CREATE UNIQUE INDEX ON users (uuid)",
            "CREATE TABLE IF NOT EXISTS documents (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), day INTEGER)",
            "CREATE TABLE IF NOT EXISTS interests_documents (id serial PRIMARY KEY, interest_id INTEGER REFERENCES interests(id), document_id INTEGER REFERENCES documents(id))",
    ]

    DROP_SQL = [
            "DROP TABLE IF EXISTS interests CASCADE",
            "DROP TABLE IF EXISTS users CASCADE",
            "DROP TABLE IF EXISTS documents CASCADE",
            "DROP TABLE IF EXISTS interests_documents CASCADE",
    ]

    def _execute(self, sql, params=[]):
        logger.debug("SQL: {0} {1}".format(sql, str(params)))
        self.cursor.execute(sql, params)

    def _initialize(self, clobber=False):
        statements = []
        if clobber:
            statements.extend(PostgresBackend.DROP_SQL)
        statements.extend(PostgresBackend.SETUP_SQL)

        for sql in statements:
            self._execute(sql)
        self.connection.commit()

    def __init__(self, settings):
        self.settings = settings
        self.connection = psycopg2.connect(**self.settings)
        self.cursor = self.connection.cursor()

    def _setup(self):
        self.__create_interests()

    def __create_interests(self):
        from upstudy.data.labels import LABELS
        for namespace, labels in LABELS.iteritems():
            for label in labels:
                self._execute("INSERT INTO interests (namespace, name) VALUES (%s, %s)", [namespace, label])
        self.connection.commit()
