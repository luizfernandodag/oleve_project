# app/utils.py
from bson import ObjectId


def serialize_mongo(obj):

    if isinstance(obj, list):
        return [serialize_mongo(o) for o in obj]
    elif isinstance(obj, dict):
        return {k: serialize_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj
