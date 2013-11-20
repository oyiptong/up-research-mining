__import__('pkg_resources').declare_namespace(__name__)

import logging
logger = logging.getLogger("upstudy")

class SQLBackend(object):
    def _execute(self, sql, params=[]):
        logger.debug("SQL: {0} {1}".format(sql, str(params)))
        self.cursor.execute(sql, params)
        results = self.cursor.fetchall()

    def _initialize(self, clobber=False):
        statements = []
        if clobber:
            logger.info("tearing down {0} tables".format(len(self.SCHEMA["teardown"])));
            for sql in self.SCHEMA["teardown"]:
                self._execute(sql)
            self.connection.commit()

        logger.info("creating {0} tables".format(len(self.SCHEMA["tables"])));
        for sql in self.SCHEMA["tables"]:
            self._execute(sql)
        self.connection.commit()

        logger.info("creating {0} indexes".format(len(self.SCHEMA["indexes"])));
        for sql in self.SCHEMA["indexes"]:
            self._execute(sql)
        self.connection.commit()

    def __init__(self, settings):
        self.settings = settings
        self.connection = self.driver.connect(**self.settings)
        self.cursor = self.connection.cursor()

    def _setup(self):
        self.__create_interests()

    def __create_interests(self):
        logger.info("loading initial data: categories, namespaces and types");
        from upstudy.data.labels import LABELS, NAMESPACES, TYPES
        for namespace, labels in LABELS.iteritems():
            for label in labels:
                self._execute(self.SEED_DATA["categories"], [label])
        for ns in NAMESPACES:
                self._execute(self.SEED_DATA["namespaces"], [ns])
        for type in TYPES:
                self._execute(self.SEED_DATA["types"], [type])
        self.connection.commit()
