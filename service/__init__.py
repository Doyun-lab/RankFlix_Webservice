from flask import Flask
from flask import request
from flask import render_template
import os
from src import user, mylogger, myconfig
import pdb

app = Flask(__name__)

# create a logger.
project_root_path = os.getenv("DA_DESIGN_SERVER")
cfg = myconfig.get_config('{}/share/project.config'.format(
    project_root_path))
log_directory = cfg['logger'].get('log_directory')
logger = mylogger.get_logger('login', log_directory)

@app.route('/login', methods=["POST"])
def login():
    user_id = request.json.get('user_id')
    passwd = request.json.get('passwd')
    logger.info('{}: login'.format(user_id))

    ret = {"result": None,
        "session_id": None,
        "msg": ""}

    session_key = user.login(user_id, passwd, logger)
    logger.info('{}: session_key = {}'.format(user_id, session_key))
    if not session_key:
        ret["result"] = False
        ret["msg"] = "Failed to login"
    else:
        ret["result"] = True
        ret["session_id"] = session_key["session_id"]

    logger.info('{}: login result = {}'.format(user_id, ret))
    return ret

@app.route('/favorite', methods=["POST"])
def favorite():
    """favorite (company) API function.

    Specification can be found in `API.md` file.

    :return: JSON serialized string containing the result with session_id
    :rtype: str
    """
    session_id = request.json.get('session_id')
    request_type = request.json.get('request_type')
    loggers['favorite'].info('{}: favorite with request type = {}'.format(
        session_id, request_type))

    ret = {"result": None,
        "msg": ""}

    if request_type == 'add':
        what_time_is_it = datetime.datetime.now()
        doc_user = user.check_session(session_id,
                what_time_is_it.timestamp())
        if not doc_user:
            msg = '{}: Invalid session'.format(session_id)
            loggers['favorite'].error(msg)
            ret['result'] = False
            ret['msg'] = msg
        else:
            favorites = request.json.get('favorite')
            how_many_added = user.add_favorite(doc_user,
                    favorites, loggers['favorite'])
            new_session = user.generate_session(doc_user)
            if how_many_added:
                msg = '{}: {} favorite items added'.format(
                    session_id, how_many_added)
                ret['result'] = True
            else:
                msg = '{}: No favorite items added'.format(
                    session_id)
                ret['result'] = False
            ret['msg'] = msg
            ret['session_id'] = new_session["session_id"]
    elif request_type == 'get':
        pass
    else:
        msg = '{}: Invalid request type = {}'.format(
                session_id, request_type)
        loggers['favorite'].error(msg)
        ret['result'] = False
        ret['msg'] = msg

    loggers['favorite'].info('{}: favorite result = {}'.format(
        session_id, ret))
    return ret

@app.route('/')
def web_login():
    return render_template("index.html")

@app.route('/help')
def web_help():
    return render_template("help.html")

@app.route('/handle-login', methods=["POST"])
def handle_login():
    """Login function for web service.

    :return: HTML document (render_template() result)
    :rtype: str
    """
    user_id = request.values.get('user_id')
    passwd = request.values.get('passwd')
    loggers['login'].info('{}: login(web)'.format(user_id))

    ret = {"result": None,
        "session_id": None,
        "service_type": "service1",
        "msg": ""}

    session_key = user.login(user_id, passwd, loggers['login'])
    loggers['login'].info('{}: session_key = {}'.format(user_id, session_key))
    if not session_key:
        ret["result"] = False
        ret["msg"] = "Failed to login"
    else:
        ret["result"] = True
        ret["session_id"] = session_key["session_id"]

    loggers['login'].info('{}: login(web) result = {}'.format(user_id, ret))

    if not ret["result"]:
        return render_template("login_failed.html")

    ret_json = json_util.dumps(ret, ensure_ascii=False)

    return render_template("service.html",
            session_info=ret_json)

@app.route('/services', methods=["POST"])
def services():
    """API function of services.

    Specification can be found in `API.md` file.

    :return: JSON serialized string containing the result with session_id
    :rtype: str
    """
    session_id = request.json.get('session_id')
    request_type = request.json.get('request_type')
    loggers['service'].info('{}: service with request type = {}'.format(
        session_id, request_type))

    ret = {"result": None,
        "msg": ""}

    if request_type not in ['service1', 'service2']:
        msg = '{}: Invalid request type = {}'.format(
                session_id, request_type)
        loggers['service'].error(msg)
        ret['result'] = False
        ret['msg'] = msg
        return ret

    what_time_is_it = datetime.datetime.now()
    doc_user = user.check_session(session_id,
            what_time_is_it.timestamp())
    if not doc_user:
        msg = '{}: Invalid session'.format(session_id)
        loggers['service'].error(msg)
        ret['result'] = False
        ret['msg'] = msg
        return ret

    if request_type == 'service1':
        favorites = user.get_favorite(doc_user, loggers['service'])
        ret['msg'] = mymodel.get_service1_result(favorites, loggers['service'])
        ret['result'] = True
    elif request_type == 'service2':
        company_name = request.json.get('company_name')
        ret['msg'] = mymodel.get_service2_result(company_name, loggers['service'])
        ret['result'] = True

    loggers['service'].info('{}: service result = {}'.format(
        session_id, ret))
    return ret

