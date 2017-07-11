from datetime import datetime
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine, DateTime
from scrapy_article.settings import DB_URI

Base = declarative_base()
engine = create_engine(DB_URI, poolclass=NullPool)
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()


class RawArticle(Base):
    __tablename__ = 'v2_rawpromotion'
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'
    }

    # 表的结构:
    id = Column(Integer, unique=True, primary_key=True, autoincrement=True)
    raw_url = Column(String(400))
    title = Column(String(80), nullable=False)
    desc = Column(String(255))
    source = Column(String(32))
    image = Column(String(255))
    s3_key = Column(String(255), index=True, unique=True)
    status = Column(Integer, default=0, nullable=False)  # "0:已爬, 1:已优化"
    created_at = Column(DateTime, default=datetime.now)
    article_time = Column(DateTime, default=datetime.now)
    platform = Column(String(32), default='wechat')
    section = Column(String(32), default='activity')

    def to_dict(self):
        return {c.name: getattr(self, c.name, None)
                for c in self.__table__.columns}

    @classmethod
    def get_raw_url(cls):
        try:
            query = session.query(cls).all()
        except Exception as e:
            # logger.exception(e)
            session.rollback()
            return []
        return [account.raw_url for account in query]

Base.metadata.create_all()