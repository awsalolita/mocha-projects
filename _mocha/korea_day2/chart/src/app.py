from flask import Flask, request, jsonify

import logging
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session
import uuid
import requests

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def create_engine_mysql(user, password, host, database, port=3306):
    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url, pool_pre_ping=True, future=True)


# Pick one. Edit the credentials.
engine = create_engine_mysql(
    user="awsadmin",
    password="j]]R3RjxbHZ50LMuTarN*bz?a|SZ",
    host="database-1.ca1iuecyo0cq.us-east-1.rds.amazonaws.com",
    database="hallyudb",
    port=3307
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
clients = Base.classes.clients
projects = Base.classes.projects

def row_to_dict(row):
    """Turn one reflected ORM row into a plain dict of its columns."""
    if row is None:
        return None
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}

## middleware
@app.before_request
def require_api_key():
    if request.path.startswith("/api"):
        if request.path.startswith("/api/client"):
            return None
        if not request.headers.get("X-API-Key"):
            return jsonify({"error": "unauthorized"}), 401

@app.route("/")
def health():
  return jsonify({
        "status": "ok"
  }), 200

@app.route("/api/client", methods=["POST"])
def create_client():
    data = request.get_json()
    with Session(engine) as session, session.begin():
        api_key = str(uuid.uuid4())
        row = clients(name=data.get("name"), api_key=api_key)
        session.add(row)
        session.flush()    

        return jsonify({
            "id": row.id,
            "name": row.name,
            "api_key": row.api_key 
            
        }), 201

@app.route("/api/analytics/project", methods=["POST"])
def create_project():
    data = request.get_json()
    with Session(engine) as session, session.begin():
        row = projects(name=data.get("name"), description=data.get("description"), client_id=data.get("client_id"))
        session.add(row)
        session.flush()    

        return jsonify({
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "client_id": row.client_id,
            "created_at": row.created_at 
            
        }), 201


@app.route("/api/analytics/project/<id>", methods=["GET"])
def get_project(id):
    with Session(engine) as session, session.begin():
        row = session.get(projects, id)
        return jsonify({
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "client_id": row.client_id,
            "created_at": row.created_at,
            "file_count": 0,
            "job_count": 0
            
        }), 200

@app.route("/api/analytics/projects", methods=["GET"])
def list_projects():
    with Session(engine) as session, session.begin():
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=10, type=int)

        page = max(page, 1)
        limit = min(max(limit, 1), 100)

        stmt = select(projects)
        rows = [row_to_dict(r) for r in session.scalars(stmt).all()]

        total = len(rows)
        start = (page - 1) * limit
        end = start + limit
        items = rows[start:end]

        return jsonify(
            {
                "projects": items,
                "total": total,
                "page": page
            }
        ), 200

@app.route("/api/takedown-notice", methods=["POST"])
def takedown():
    data = request.get_json()
    body = {
        "team": "1LRRVZHV",
        "takedown": data.get("takedown")
    }

    headers = {
        "Content-Type": "application/json"
    }

    url = "http://95.182.115.9:8080/api/takedown"

    x = requests.post(url, json=body, headers=headers)

    return jsonify({
        "accepted": True
    }), 202

if __name__ == "__main__":
  app.run("0.0.0.0", 8080)
