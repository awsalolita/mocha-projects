from flask import Flask, request, jsonify

import json

import logging
from sqlalchemy import create_engine, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def create_engine_postgres(user, password, host, database, port=5432):
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url, pool_pre_ping=True, future=True)


# Pick one. Edit the credentials.
engine = create_engine_postgres(
    user="awspg",
    password="Ph25:YUdP<q[f6xbWLfa3W]KTD-N",
    host="database-1.cluster-cy56w4uway77.us-east-1.rds.amazonaws.com",
    database="operation",
    port=5433
)

def row_to_dict(row):
    """Turn one reflected ORM row into a plain dict of its columns."""
    if row is None:
        return None
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


# =============================================================================
# 2. REFLECT TABLES (automap)
# =============================================================================
# automap reads the live schema and builds ORM classes for you.
# Table names become attributes on Base.classes.<table_name>.
# Requires a primary key on each table you want mapped.

Base = automap_base()
Base.prepare(autoload_with=engine)

# Grab the mapped classes you need (names = actual table names).
enterprise_table = Base.classes.enterprise

@app.route("/get_value")
def get():
    id = request.args.get("id", default="")
    with Session(engine) as session, session.begin():
        row = session.get(enterprise_table, id)

        return jsonify(
            row_to_dict(row)
        ), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
  app.run("0.0.0.0", 3000)
