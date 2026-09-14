import json
import pymongo
import urllib.parse
from pymongo import MongoClient

# 1. URL-encode the username and password safely
username = urllib.parse.quote_plus("awsmongo")
password = urllib.parse.quote_plus("nn_x_Vl(~a)_nAI?5y0V4|7K_-Q5") # Rotate this password in AWS!

# 2. Inject the safely encoded credentials into the URI using an f-string
uri = f"mongodb://{username}:{password}@mealmint-recipes.c8t8o4e8myfc.us-east-1.docdb.amazonaws.com:27018/?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"

def lambda_handler(event, context):
    # Added a default empty string to .get() to prevent NoneType errors if "path" is missing
    id = event.get("path", "").replace("/recipes/", "").replace("/rating", "")
    
    try:
        with pymongo.MongoClient(uri) as client:
            database = client.mealmint
            recipes = database.recipes
            result = recipes.find_one({ "recipeId" : id })
            ratings = result.get("ratings")
            sum = 0
            for rate in ratings:
                sum += rate.get("score")

            data = {
                "recipeId": id,
                "rating": sum / len(ratings),
                "count": len(ratings)
            }

            return {
                'statusCode': 200,
                'body': json.dumps(
                    data
                )
            }
            
    except Exception as e:
        raise Exception("The following error occurred: ", e)
    
