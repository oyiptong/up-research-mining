__import__('pkg_resources').declare_namespace(__name__)

import logging
logger = logging.getLogger("upstudy")
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

    def initialize(self):
        logger.info("creating database");
        self.connection.execute("CREATE DATABASE up_research CHARACTER SET utf8;")

    def drop(self):
        logger.info("dropping database");
        self.connection.execute("DROP DATABASE up_research;")

    def create_tables(self):
        from upstudy.data.models import create_tables
        create_tables(self.engine)

    def load_categories(self):
        logger.info("loading initial data");
        from upstudy.data.models import create_categories

        create_categories(self.session)
