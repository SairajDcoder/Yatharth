from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import MetaData

db_metadata = MetaData()
db = SQLAlchemy(metadata=db_metadata)
