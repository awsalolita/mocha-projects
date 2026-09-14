import base64
import json
import logging
import requests
import boto3


from sqlalchemy import create_engine, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session
import random
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def create_engine_postgres(user, password, host, database, port=5432):
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url, pool_pre_ping=True, future=True)


# Pick one. Edit the credentials.
engine = create_engine_postgres(
    user="awspg",
    password="8<yHL1-O7_eCny-0Q3kM[-9H$7n:",
    host="database-1.cluster-cy5wmckawgmx.us-east-1.rds.amazonaws.com",
    database="gridline",
    port=5433
)


Base = automap_base()
Base.prepare(autoload_with=engine)

# Grab the mapped classes you need (names = actual table names).
tracks = Base.classes.tracks
drivers = Base.classes.drivers
heats = Base.classes.heats
laps = Base.classes.laps
heat_standings = Base.classes.heat_standings




def lambda_handler(event, context):
    print(event)
    heat_id = event.get("detail").get("heat_id")
    try:
        with Session(engine) as session, session.begin():
            heat = session.get(heats, heat_id)
            heat.status = "RUNNING"
            heat.started_at = str(datetime.now())
            
            session.flush()
            return {
                'statusCode': 200,
                'body': json.dumps('Status updated')
            }
    
    except:
        return {
            'statusCode': 422,
            'body': 'could not update status'
        }
