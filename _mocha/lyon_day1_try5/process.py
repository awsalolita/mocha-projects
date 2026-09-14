import boto3
from boto3.dynamodb.conditions import Key, Attr

import json
import logging

from sqlalchemy import create_engine, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def get_resource(region=None):
    return boto3.resource("dynamodb", region_name=region)

ddb_resource = get_resource("us-east-1")
TABLE = "FeedbackTable"

def create_engine_postgres(user, password, host, database, port=5432):
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url, pool_pre_ping=True, future=True)


# Pick one. Edit the credentials.
engine = create_engine_postgres(
    user="awspg",
    password="NcErrGvc.*MwYqkSvskb?8p6FeN>",
    host="database-1.clm6gs4qcvah.us-east-1.rds.amazonaws.com",
    database="unicorn",
    port=5433
)


Base = automap_base()
Base.prepare(autoload_with=engine)

dataprocessingapp = Base.classes.dataprocessingapp


def row_to_dict(row):
    """Turn one reflected ORM row into a plain dict of its columns."""
    if row is None:
        return None
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}

def ddbr_scan(resource, table, filter_attr=None, filter_value=None):
    table_obj = resource.Table(table)
    if filter_attr is not None:
        return table_obj.scan(
            FilterExpression=Attr(filter_attr).eq(filter_value)
        ).get("Items", [])
    return table_obj.scan().get("Items", [])

def ddbr_delete_item(resource, table, key):
    return resource.Table(table).delete_item(Key=key)

def process():
    items = ddbr_scan(ddb_resource, TABLE)
    number = 0
    for item in items:
        if number == 5:
            break
        with Session(engine) as session, session.begin():
            id = int(item.get("id").replace("req_", ""))
            row = dataprocessingapp(id=id, message=item.get("message"), process=False)
            session.add(row)
            session.flush()                
        ddbr_delete_item(ddb_resource, TABLE, item)
        number +=1 

process()
