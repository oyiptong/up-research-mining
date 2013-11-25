import upstudy.settings as settings
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import logging
logger = logging.getLogger("upstudy")

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False, unique=True)

    @classmethod
    def get_all(cls, session):
        if not hasattr(cls, "_all"):
            cls._all = session.query(cls).all()
        return cls._all

    def __repr__(self):
        return "<Category('{0}')>".format(self.name)

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), nullable=False, unique=True)

    def __repr__(self):
        return "<User('{0}')>".format(self.uuid)

    @classmethod
    def get_or_create(cls, session, uuid):
        """
        Get or Create a user with a given uuid
        """
        user = session.query(User).filter(User.uuid == uuid).first()
        if not user:
            user = cls(uuid=uuid)
            session.add(user)
        return user

class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
            Index("user_id_payload", "user_id", "payload_made_at"),
            {'mysql_engine':'InnoDB'}
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref=backref("submissions", order_by=id))
    received_at = Column(DateTime, nullable=False, index=True)
    installed_at = Column(DateTime, nullable=False, index=True)
    payload_made_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(DateTime, nullable=False, index=True)
    source = Column(String(255), nullable=False, index=True)
    locale = Column(String(255), nullable=False, index=True)
    addon_version = Column(String(255), nullable=False, index=True)
    tld_counter = Column(Text, nullable=False)
    prefs = Column(Text, nullable=False)

    def __repr__(self):
        return "<Submission('{0}:{1}')>".format(self.user.uuid, self.payload_made_at.strftime("%Y/%m/%d"))

class SubmissionInterest(Base):
    __tablename__ = "submission_interests"
    __table_args__ = {'mysql_engine':'InnoDB'}

    day = Column(Date, nullable=False, index=True, primary_key=True)
    type_namespace = Column(String(255), nullable=False, index=True, primary_key=True)
    host_count = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user = relationship("User", backref=backref("submission_interests", order_by=day))
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    submission = relationship("Submission", backref=backref("submission_interests", order_by=type_namespace))
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)
    category = relationship("Category", backref=backref("categories", order_by=type_namespace))

    def __repr__(self):
        return "<SubmissionInterest('{0}:{1}:{2}:{3}')>".format(self.user.uuid, self.type_namespace, self.category.name.split('.')[1], self.day)

def create_tables(engine):
    Base.metadata.create_all(engine)

def create_categories(session):
    from upstudy.data import LABELS
    
    for namespace, labels in LABELS.iteritems():
        for label in labels:
            # MySQL problem: indexes are case insensitive, cannot have case sensitive unique names
            cat_name = "{0}.{1}".format(namespace, label)
            category = Category(name=cat_name)
            session.merge(category)
    session.commit()
