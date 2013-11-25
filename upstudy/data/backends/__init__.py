__import__('pkg_resources').declare_namespace(__name__)

import logging
logger = logging.getLogger("upstudy")
from upstudy import settings
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.exc import ProgrammingError, IntegrityError

class SQLBackend(object):

    def refresh(self, user=None, password=None, host=None, database=None, type=None, driver=None):
        user = user or self.config.get("user")
        password = password or self.config.get("user")
        database = database or self.config.get("database")
        host = host or self.config.get("host")
        type = type or self.config.get("type")
        driver = driver or self.config.get("driver")
        params = {
                "user": user,
                "password": password,
                "database": database,
                "host": host,
                "type": type,
                "driver": driver,
        }

        if user:
            if not password:
                self.engine = create_engine("{type}+{driver}://{user}@{host}/{database}".format(**params), encoding='utf8')
            else:
                self.engine = create_engine("{type}+{driver}://{user}:{password}@{host}/{database}".format(**params), encoding='utf8')
        else:
            self.engine = create_engine("{type}+{driver}://{host}/{database}".format(**params), encoding='utf8')

        if self.config.get("use_threadlocal", False):
            self.engine.pool._use_threadlocal = True
        self._connection = self.engine.connect()
        self._connection.execute("COMMIT")
        Session = sessionmaker(bind=self.engine)
        self._session = Session()

    def __init__(self, config):
        self.config = config
        #self.refresh()

        if not hasattr(SQLBackend, "_instance"):
            SQLBackend._instance = self

    def __initialize__(self):
        logger.info("creating database");
        if self.config["type"] == "mysql":
            self.refresh()
            self._connection.execute("CREATE DATABASE IF NOT EXISTS up_research CHARACTER SET utf8;")
        elif self.config["type"] == "postgresql":
            self.refresh(database="postgres")
            try:
                self._connection.execute("CREATE DATABASE up_research;")
            except ProgrammingError, e:
                logging.warning(e)
            self.refresh()

    def __drop__(self):
        logger.info("dropping database");
        database = self.config.get("database")
        if self.config["type"] == "postgresql":
            database = "postgres"
        self.refresh(database=database)
        self._connection.execute("DROP DATABASE up_research;")

    def __create_tables__(self):
        from upstudy.data.models import create_tables
        create_tables(self.engine)

    def __load_categories__(self):
        logger.info("loading initial data");
        from upstudy.data.models import create_categories
        try:
            create_categories(self._session)
        except IntegrityError, e:
            logger.warning(e)

    @property
    def session(self):
        return self._session

    @classmethod
    def instance(cls):
        if hasattr(SQLBackend, "_instance"):
            return SQLBackend._instance
        else:
            return SQLBackend(settings.database)
