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


APP_ID = "tj0hfyn"
ENV_ID = "76k3y2i"
BASELINE_ID = "laluata"
WET_ID = "0cfkwgg"

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

def get_active_timing_rule():
    url = "https://d2wh7kt8zhycpc.cloudfront.net/api/config/rules/version"
    headers = {
        "X-Dev-Groups": "director",
        "X-Dev-Sub": "scoring-director"
    }

    x = requests.get(url=url, headers=headers)

    return x.json().get("version")


def get_active_config_rule(app_id, env_id, conf_profile_id) -> dict:
    appconfig = boto3.client('appconfigdata')

    token = appconfig .start_configuration_session(
        ApplicationIdentifier=app_id,
        EnvironmentIdentifier=env_id, 
        ConfigurationProfileIdentifier=conf_profile_id
    )

    config_stream = appconfig.get_latest_configuration(ConfigurationToken=token.get('InitialConfigurationToken'))
    config = json.loads(config_stream.get('Configuration').read())
    return config


def lambda_handler(event, context):
    try:
        body = _parse_body(event)
        print(body)

        rule_version = get_active_timing_rule()
        app_config = ""
        if rule_version == "wet-track-2026":
            app_config = get_active_config_rule(APP_ID, ENV_ID, WET_ID)
        else:
            app_config = get_active_config_rule(APP_ID, ENV_ID, BASELINE_ID)

        transponder_id = body.get("transponder_id")
        heat_id = body.get("heat_id")
        lap_time_ms = random.randrange(app_config.get("min_lap_ms"), app_config.get("max_lap_ms"))

        with Session(engine) as session, session.begin():
            count = session.query(laps.lap_id).count()

            row = laps(lap_id=int(count+1), heat_id=heat_id, transponder_id=transponder_id, lap_number=int(count+1), lap_time_ms=lap_time_ms, crossed_at=str(datetime.now()), rules_version=rule_version)
            session.add(row)
            session.flush()   

            data = {
                "lap_number": row.lap_number,
                "lap_time_ms": row.lap_time_ms,
                "rules_version": row.rules_version
            }

            return {
                "statusCode": 202,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(data),
            }
    except Exception as e:
        return {
            "statusCode": 422,
            "headers": {"Content-Type": "application/json"},
            "body": str(e),
        }
