from flask import Flask, request, jsonify, Response

import logging
import sys

import boto3
from boto3.dynamodb.conditions import Key, Attr

def get_resource(region=None):
    return boto3.resource("dynamodb", region_name=region)

ddb_resource = get_resource("us-east-1")
TABLE = "unicorn"

def ddbr_scan_all(resource, table):
    """Scan every page (handles LastEvaluatedKey pagination)."""
    table_obj = resource.Table(table)
    items, kwargs = [], {}
    while True:
        resp = table_obj.scan(**kwargs)
        items.extend(resp.get("Items", []))
        if "LastEvaluatedKey" not in resp:
            break
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
    return items


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/all")
def list_all():
    items = ddbr_scan_all(ddb_resource, TABLE)
    return jsonify({"items": items}), 200

if __name__ == "__main__":
  app.run("0.0.0.0", 3000)
