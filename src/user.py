import pdb
import hashlib
import datetime
from bson.timestamp import Timestamp

db_client = MongoClient(db_ip, db_port)
db = db_client[db_name]

col_user = db[cfg['db']['col_user']]
col_contents = db[cfg['db']['col_contents']]
col_favorites = db[cfg['db']['col_favorites']]

def add_favorite(doc_user, favorites, logger, favorite_limit=10):
    """add one or more favorite company to the user's list.

    :param doc_user: user document (DB)
    :type doc_user:
    :param favorites: favorite company list to add
    :type favoriates: list
    :param favorite_limit: maximum number of favorite companies for a user
    :type favorite_limit: int
    :return: the number of added items
    :rtype: int
    """
    my_favorites = col_favorite.find_one({"User": doc_user["_id"]})
    if my_favorites == None:
        logger.info('{}: a favorite list created'.format(
            doc_user["user_id"]))
        my_favorites = {"User": doc_user["_id"],
            "Company": []}
        col_favorite.insert_one(my_favorites)
    if len(my_favorites["Company"]) >= favorite_limit:
        logger.info('{}: favorite list is already full'.format(
            doc_user["user_id"]))
        return 0
    ret = 0
    for f in favorites:
        doc_company = col_company.find_one({"name": f})
        if not doc_company:
            continue
        if doc_company["_id"] in my_favorites["Company"]:
            continue
        my_favorites["Company"] += [doc_company["_id"]]
        logger.info('{}: {} added into favorite list'.format(
            doc_user["user_id"], f))
        ret += 1

    if ret >= 1:
        col_favorite.find_one_and_replace({"User": doc_user["_id"]}, my_favorites)

    return ret


def convert_to_SHA256(x):
    """Convert a given string to SHA256-encoded string.

    :param x: arbitrary string.
    :type x: str
    :return: SHA256 encoded string
    :rtype: str
    """
    result = hashlib.sha256(x.encode())
    result = result.hexdigest()
    return result

def convert_to_bson_timestamp(ts):
    """Convert a given timestamp (of datetime) to bson Timestamp.

    :param ts: datetime timestamp
    :type ts: float
    :return: bson Timestamp
    :rtype: bson.timestamp.Timestamp
    """
    lowpart = int(ts)
    return Timestamp(lowpart, 1)

def check_passwd(col_user, userid, passwd):
    """Check if the password is correct or not.

    :param col_user: Database collection of user.
    :type col_user: collection
    :param userid: user ID
    :type userid: str
    :param passwd: password
    :type passwd: str
    :return: user document (DB) or False
    :rtype: dict or bool
    """
    the_user = col_user.find_one({"user_id": userid})
    if not the_user:
        return False

    hashed_passwd = convert_to_SHA256(passwd)
    db_passwd = the_user['passwd']
    if hashed_passwd != db_passwd:
        return False
    return the_user

def generate_session(doc_user, col_user):
    """Generate session key.

    :param doc_user: user's document (DB)
    :type doc_user: dict
    :param col_user: user's collection (DB)
    :type col_user: pymongo.collection.Collection
    :return: session key dictionary
    :rtype: dict
    """
    raw_string = doc_user["user_id"] + str(datetime.datetime.now())
    new_session_id = convert_to_SHA256(raw_string)
    i = 1
    while True:
        exist_session = col_user.find_one({"session_key.session_id": new_session_id})
        if not exist_session:
            break
        raw_string = doc_user["user_id"] + str(datetime.datetime.now()) * (i+1)
        new_session_id = convert_to_SHA256(raw_string)
        i += 1

    timestamp = datetime.datetime.now()
    timestamp = convert_to_bson_timestamp(timestamp.timestamp())
    doc_user["session_key"] = {"session_id": new_session_id,
            "timestamp": timestamp}
    col_user.find_one_and_replace({"user_id": doc_user["user_id"]}, doc_user)
    return doc_user["session_key"]

def check_session(col_user, session_id, timestamp, elapse_limit=60):
    """Check if the session is valid.

    :param col_user: user's collection (DB)
    :type col_user: pymongo.collection.Collection
    :param session_id: session ID
    :type session_id: str
    :param timestamp: timestamp (usually, this is current timestamp)
    :type timestamp: float
    :param elapse_limit: time limit for checking session validity
    :type elapse_limit: int
    :return: user document (DB) or False
    :rtype: dict or bool
    """
    the_user = col_user.find_one({"session_key.session_id": session_id})
    if not the_user:
        return False

    the_timestamp = the_user["session_key"].get("timestamp")
    current_timestamp = convert_to_bson_timestamp(timestamp)

    elapsed = current_timestamp.time - the_timestamp.time
    if elapsed >= elapse_limit:
        return False
    return the_user
