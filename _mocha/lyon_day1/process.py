import json
import logging
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

import boto3
from boto3.dynamodb.conditions import Key, Attr

def get_client(region=None):
    return boto3.client("dynamodb", region_name=region)

def get_resource(region=None):
    return boto3.resource("dynamodb", region_name=region)

def ddbr_scan(resource, table, filter_attr=None, filter_value=None):
    table_obj = resource.Table(table)
    if filter_attr is not None:
        return table_obj.scan(
            FilterExpression=Attr(filter_attr).eq(filter_value)
        ).get("Items", [])
    return table_obj.scan().get("Items", [])

def ddbr_delete_item(resource, table, key):
    return resource.Table(table).delete_item(Key=key)

ddb_resource = get_resource("us-east-1")
TABLE = "FeedbackTable"



def create_engine_postgres(user, password, host, database, port=5432):
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url, pool_pre_ping=True, future=True)


# Pick one. Edit the credentials.
engine = create_engine_postgres(
    user="pgaws",
    password="ilfQvZX:Ycsm9twqBdLQZOq9!ylg",
    host="database-1.cuvcge0kg0gv.us-east-1.rds.amazonaws.com",
    database="process",
    port=5433
)


# =============================================================================
# 2. REFLECT TABLES (automap)
# =============================================================================
# automap reads the live schema and builds ORM classes for you.
# Table names become attributes on Base.classes.<table_name>.
# Requires a primary key on each table you want mapped.

Base = automap_base()
Base.prepare(autoload_with=engine)

# Grab the mapped classes you need (names = actual table names).
process_table = Base.classes.dataprocessingapp

def process():
    MAX_RUN = 5
    items = ddbr_scan(ddb_resource, TABLE)

    for item in items:
        if MAX_RUN == 0:
            break

        MAX_RUN -= 1
        with Session(engine) as session, session.begin():
            id = item.get("id").replace("req_", "")
            row = process_table(id=int(id), message=item.get("message"), process=False)
            session.add(row)
            session.flush()
            Key = {
                "id": item.get("id"),
                "message": item.get("message")
            }
            ddbr_delete_item(ddb_resource, TABLE, Key)
        

def main():
    process()

main()
sys.exit(0)
