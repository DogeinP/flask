import config

from sqlalchemy import create_engine, text

database = create_engine(config.test_config['DB_URL'], encoding = 'utf-8',max_overflow=0)