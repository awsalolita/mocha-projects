import base64
import json
import logging
import time


from sqlalchemy import create_engine, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session

import boto3
from boto3.dynamodb.conditions import Key, Attr

def get_resource(region=None):
    return boto3.resource("dynamodb", region_name=region)

ddb_resource = get_resource('us-east-1')
TABLE = "cloudraiser-iot"

def ddbr_put_item(resource, table, item):
    """item uses plain Python types, e.g. {"id": "1", "n": 5}."""
    return resource.Table(table).put_item(Item=item)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_engine_postgres(user, password, host, database, port=5432):
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url, pool_pre_ping=True, future=True)


# Pick one. Edit the credentials.
engine = create_engine_postgres(
    user="awspg",
    password=".v8A_JQuspaxiV|:ViYBBa0<ChBM",
    host="database-2.cluster-c8t8o4e8myfc.us-east-1.rds.amazonaws.com",
    database="unicorn",
    port=5433
)


Base = automap_base()
Base.prepare(autoload_with=engine)

enterprise_table = Base.classes.enterprise



def _parse_body(event):
    body = event.get("body")
    if body is None:
        return None
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    try:
        return json.loads(body)
    except (ValueError, TypeError):
        return body

def row_to_dict(row):
    """Turn one reflected ORM row into a plain dict of its columns."""
    if row is None:
        return None
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


class AlchemyEncoder(json.JSONEncoder):
    """Use with json.dumps(row, cls=AlchemyEncoder) when you don't have to_dict."""

    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith("_") and x != "metadata"]:
                data = getattr(obj, field)
                try:
                    json.dumps(data)  # keep only JSON-safe values
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return super().default(obj)

def update_column_by_name(row_id, column, value):
    with Session(engine) as session, session.begin():
        one = session.get(enterprise_table, row_id)
        if one is not None:
            setattr(one, column, value)     # dynamic field update
            session.flush()
            return {"updated": row_id}

        # not found -> insert a new row with just id + that one dynamic column
        new_row = enterprise_table(id=row_id, **{column: value})
        session.add(new_row)
        session.flush()
        return {"inserted": new_row.id}

def calculate_score(systolic, diastolic):
    #MAP = (Systolic Blood Pressure + [2 × Diastolic Blood Pressure]) / 3
    return (systolic + (2 * diastolic)) /3

def lambda_handler(event, context):
    body = _parse_body(event)
    if "no" in body: 
        # {'no': '037', 'systolic': '119', 'diastolic': '97'}
        ttl = int(time.time()) + (3600 * 24 * 2)
        score = calculate_score(body.get("systolic"), body.get("diastolic"))
        data = {
            "No": body.get("no"),
            "Systolic": body.get("systolic"),
            "Diastolic": body.get("diastolic"),
            "Score": score,
            "ttl": ttl
        }

        result = ddbr_put_item(ddb_resource, TABLE, data)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "ok"}),
        }
    else:
        id = body.get("id")
        column = body.get("column")
        value = body.get("value")

        update_column_by_name(id, column, value)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "ok"}),
        }
