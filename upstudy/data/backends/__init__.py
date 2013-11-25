__import__('pkg_resources').declare_namespace(__name__)

import logging
logger = logging.getLogger("upstudy")
from upstudy import settings
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.exc import ProgrammingError, IntegrityError

class SQLBackend(object):

    def __init__(self, config):
        self.engine = None
        self._connection = None
        self._session = None
        self.config = config

        if not hasattr(SQLBackend, "_instance"):
            SQLBackend._instance = self

    def connect(self, user=None, password=None, host=None, database=None, type=None, driver=None):
        if self.engine:
            self._session = None
            self._connection.close()
            self._connection = None
            self.engine.dispose()
            self.engine = None

        user = user or self.config.get("user")
        password = password or self.config.get("user")
        database = database or self.config.get("database")
        host = host or self.config.get("host")
        type = type or self.config.get("type")
        driver = driver or self.config.get("driver")
        pool_size = self.config.get("pool_size", 5)
        params = {
                "user": user,
                "password": password,
                "database": database,
                "host": host,
                "type": type,
                "driver": driver,
        }

        connect_url = ""
        if user:
            if not password:
                connect_url = "{type}+{driver}://{user}@{host}/{database}"
            else:
                connect_url = "{type}+{driver}://{user}:{password}@{host}/{database}"
        else:
            connect_url = "{type}+{driver}://{host}/{database}"
        self.engine = create_engine(connect_url.format(**params), encoding='utf8', pool_size=pool_size)

        if self.config.get("use_threadlocal", False):
            self.engine.pool._use_threadlocal = True

        self._connection = self.engine.connect()
        self._connection.execute("COMMIT")
        Session = sessionmaker(bind=self.engine)
        self._session = Session()

    def __initialize__(self):
        database_name = self.config.get("database", "up_research")
        logger.info("creating database {0}".format(database_name));
        if self.config["type"] == "mysql":
            self.connect()
            self._connection.execute("CREATE DATABASE IF NOT EXISTS {0} CHARACTER SET utf8;".format(database_name))
        elif self.config["type"] == "postgresql":
            self.connect(database="postgres")
            try:
                self._connection.execute("CREATE DATABASE {0};".format(database_name))
            except ProgrammingError, e:
                logging.warning(e)
            self.connect()

    def __drop__(self):
        database_name = self.config.get("database", "up_research")
        logger.info("dropping database {0}".format(database_name));
        database = self.config.get("database")
        if self.config["type"] == "postgresql":
            database = "postgres"
        self.connect(database=database)
        self._connection.execute("DROP DATABASE {0};".format(database_name))

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
