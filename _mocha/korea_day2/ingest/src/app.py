from flask import Flask, request, jsonify

import logging
import sys

from sqlalchemy import create_engine, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session
import boto3


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_client(region=None):
    return boto3.client("s3", region_name=region)

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
data_files = Base.classes.data_files


s3_client = get_client("us-east-1")
BUCKET_NAME = "hallyu-files-340985"


def s3c_put_object(client, bucket, key, body):
    """Put raw bytes/str body directly (single request, no multipart)."""
    return client.put_object(Bucket=bucket, Key=key, Body=body)

## middleware
@app.before_request
def require_api_key():
    if request.path.startswith("/ingest"):
        if request.path.startswith("/ingest/"):
            return None
        if not request.headers.get("X-API-Key"):
            return jsonify({"error": "unauthorized"}), 401

@app.route("/ingest/")
def health():
    return "Hello, world!"


@app.route("/ingest/upload", methods=["POST"])
def upload_file():
    with Session(engine) as session, session.begin():
        file = request.files["file"]
        project_id = request.form.to_dict().get("project_id")
        filename = file.filename
        s3c_put_object(s3_client, BUCKET_NAME, filename, file)
        resp =file.decode("utf-8")

        size = len(resp)
        row = data_files(project_id=project_id, filename=filename, s3_key=filename, size=size)
        session.add(row)
        session.flush()

        return jsonify(
            {
                "fileId": row.id,
                "filename": filename,
                "size": size
            }
        ), 201


if __name__ == "__main__":
  app.run("0.0.0.0", 8080)
