from pymongo.errors import PyMongoError


def is_mongo_error(exc: BaseException) -> bool:
    return isinstance(exc, PyMongoError)
