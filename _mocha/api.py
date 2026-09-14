from flask import Flask, request, jsonify
import logging
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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

def row_to_dict(row):
    """Turn one reflected ORM row into a plain dict of its columns."""
    if row is None:
        return None
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}

@app.route("/get_value")
def get_item():
    id = request.args.get("id", default="")
    if id is not None:
         with Session(engine) as session, session.begin():
            row = session.get(enterprise_table, id)         
            data = row_to_dict(row)
            return jsonify(data), 200

if __name__ == "__main__":
  app.run("0.0.0.0", 3000)
