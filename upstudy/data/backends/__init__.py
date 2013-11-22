__import__('pkg_resources').declare_namespace(__name__)

import logging
logger = logging.getLogger("upstudy")
from upstudy import settings
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

class SQLBackend(object):

    def refresh(self):
        self.engine = create_engine("{type}+{driver}://{user}:{password}@{host}/{database}".format(**self.config), encoding='utf8')
        self.connection = self.engine.connect()
        self.connection.execute("COMMIT")
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def __init__(self, config):
        self.config = config
        self.refresh()

        if not hasattr(SQLBackend, "_instance"):
            SQLBackend._instance = self

    def __initialize__(self):
        logger.info("creating database");
        self.connection.execute("CREATE DATABASE up_research CHARACTER SET utf8;")

    def __drop__(self):
        logger.info("dropping database");
        self.connection.execute("DROP DATABASE up_research;")

    def __create_tables__(self):
        from upstudy.data.models import create_tables
        create_tables(self.engine)

    def __load_categories__(self):
        logger.info("loading initial data");
        from upstudy.data.models import create_categories
        create_categories(self.session)

    @classmethod
    def instance(cls):
        if hasattr(SQLBackend, "_instance"):
            return SQLBackend._instance
        else:
            return SQLBackend(settings.database)
