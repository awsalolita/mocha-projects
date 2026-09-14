"""API Gateway REST API (Lambda proxy integration, v1) handler.

The proxy integration passes the raw HTTP request in a flat structure and
expects a response shaped like {statusCode, headers, body}.
"""

import base64
import json
import logging
import hashlib
import hmac
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET = "4ffbc46692158801e950989b3d5a1ffa783044ef86da30effc4ac581aedaac16"

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

def compute_hmac(secret, message):
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()

def call(url, data, headers):
    x = requests.post(url, json=data, headers=headers)
    return x.json()

def lambda_handler(event, context):
    body = _parse_body(event)
    leg_list = []
    net_exposure = 0

    for leg in body.get("legs"):
        leg_id = leg.get("leg_id")
        side = leg.get("side")
        amount = leg.get("amount")
        credit_amount = 0
        debit_amount = 0

        if side == "debit":
            debit_amount = amount
        else:
            credit_amount = amount

        net_exposure = debit_amount - credit_amount
            
        leg_msg = f"{leg_id}:{side}:{amount}"
        leg_list.append(leg_msg)

    final_leg = ",".join(leg_list)

    claim_id = body.get("claim_id")
    nonce = body.get("nonce")
    house = body.get("house")
    posted_collateral = body.get("posted_collateral")
    signature = body.get("signature")

    msg = f"{claim_id}|{nonce}|{house}|{final_leg}|{posted_collateral}"
    url = "http://95.182.115.9:8080"
    headers = {
        "x-api-key": "BpRBnq8g1W4qQ6ECLvKYpYVZ"
    }
    data = {
        "claim_id": claim_id
    }
    computed_signature = compute_hmac(SECRET, msg)
    quarantine_url = "http://95.182.115.9:8080/authority/quarantine"
    settle_url = "http://95.182.115.9:8080/gateway/settle"

    if computed_signature != signature:
        token = call(url, json=data, headers=headers).get("token")
        data = {
            "claim_id": claim_id, 
            "token": token
        }
        resp = call(quarantine_url, json=data, headers=headers)
        return {
            'statusCode': 200,
            'body': resp
        }
    elif computed_signature == signature and net_exposure > posted_collateral:
        token = call(url, json=data, headers=headers).get("token")
        data = {
            "claim_id": claim_id, 
            "token": token
        }
        resp = call(quarantine_url, json=data, headers=headers)
        return {
            'statusCode': 200,
            'body': resp
        }        
    else:
        token = call(url, json=data, headers=headers).get("token")
        data = {
            "claim_id": claim_id, 
            "token": token
        }
        resp = call(settle_url, json=data, headers=headers)
        return {
            'statusCode': 200,
            'body': resp
        }
