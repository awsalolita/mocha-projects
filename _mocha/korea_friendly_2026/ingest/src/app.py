from flask import Flask, request, jsonify

import logging
import sys

import json

from sqlalchemy import create_engine, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session
import uuid
import boto3
import base64

from werkzeug.utils import secure_filename


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def create_engine_mysql(user, password, host, database, port=3306):
    url = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return create_engine(url, pool_pre_ping=True, future=True)

# Pick one. Edit the credentials.
engine = create_engine_mysql(
    user="gameday",
    password="wc(ozMy<aXl!iG4!8u:VXBg8yWHw",
    host="database-1.clo20gq8c0mz.us-east-1.rds.amazonaws.com",
    database="hallyudb",
    port=3307
)

Base = automap_base()
Base.prepare(autoload_with=engine)

clients = Base.classes.clients
projects = Base.classes.projects
data_files = Base.classes.data_files

S3_BUCKET_NAME = "files-0998039458"

def get_client(region=None):
    return boto3.client("s3", region_name=region)


def s3c_put_object(client, bucket, key, body):
    """Put raw bytes/str body directly (single request, no multipart)."""
    return client.put_object(Bucket=bucket, Key=key, Body=body)

def s3c_get_object(client, bucket, key):
    """Returns dict; body bytes via resp['Body'].read()."""
    return client.get_object(Bucket=bucket, Key=key)

s3_client = get_client("us-east-1")

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

## middleware
@app.before_request
def require_api_key():
    if request.path.startswith("/ingest"):
        if request.path.startswith("/ingest/"):
            return None
        if not request.headers.get("X-API-Key"):
            return jsonify({"error": "unauthorized"}), 401

@app.route("/ingest/upload", methods=["POST"])
def upload_file():
    try:
        with Session(engine) as session, session.begin():
            if "file" not in request.files:
                return jsonify({"error": "no 'file' field in request"}), 400

            file = request.files["file"]
            fileContent = file.read()

            filename = secure_filename(file.filename)
            response = s3c_put_object(s3_client, S3_BUCKET_NAME, filename, fileContent)
            
            project_id = request.form.to_dict().get("project_id")

            row = data_files(project_id=project_id, filename=filename, s3_key=filename, size=len(fileContent))
            session.add(row)
            session.flush()


            return jsonify({
                "fileId": row.id,
                "filename": row.filename,
                "size": row.size
            }), 201

    except Exception as e:
        logger.error(e)
        return jsonify({"error": str(e)}), 500 


@app.route("/ingest/download/<id>", methods=["GET"])
def download_file(id):
    try:
        with Session(engine) as session, session.begin():
            row = session.get(data_files, id)
            response = s3c_get_object(s3_client, S3_BUCKET_NAME, row.s3_key)
            bytes_content = response.get("Body").read()
            b_decode = bytes_content.decode('utf-8')
            # encoded = base64.b64encode(bytes_content).decode('utf-8')
            return jsonify(b_decode), 200
            
    except Exception as e:
        logger.error(e)
        return jsonify({"error": str(e)}), 500 
   
        
@app.route("/ingest/")
def health():
  return jsonify({"msg": "ok"}), 200

if __name__ == "__main__":
  app.run("0.0.0.0", 8080)
