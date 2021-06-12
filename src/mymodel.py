from sklearn.linear_model import LinearRegression as lr
from sklearn.metrics.pairwise import cosine_similarity as cs
from scipy.spatial.distance import pdist, squareform
import pymongo
import datetime
from pymongo import MongoClient
from src import mylogger
from src import myconfig
import numpy as np
import pdb
import os

class model1:
    """Model for service 1 (predict future(tomorrow) stock values)
    """
    def predict(self, data, logger, D, W):
        """Predict future(tomorrow) stock value based on the previous data

        :param data: a sequence of stock values of a company
        :type data: list
        :param logger: logger instance
        :type logger: logging.Logger
        :param D: # of stock values to use for training model
        :type D: int
        :param W: feature dimension (window size)
        :type W: int
        :return: predicted stock value
        :rtype: float
        """
        logger.info('Model 1 begin')
        if not data:
            logger.error('No instances in data')
            return None
        if len(data) < W + 1:
            logger.info('Not enough instances in data, so the last instance becomes a result')
            return data[-1]
        if len(data) <= D:
            target_data = data[:]
        else:
            target_data = data[len(data)-D:]
        self._model = lr()
        X = []
        y = []
        for i in range(len(target_data)-W):
            X += [target_data[i:i+W]]
            y += [target_data[i+W]]
        self._model.fit(X, y)

        X = [target_data[len(target_data)-W:]]
        y = self._model.predict(X)
        logger.info('Model 1 end: result = {}'.format(y[0]))
        return y[0]

def run_model1(logger, D=10, W=3):
    """Run model 1

    :param logger: logger instance
    :type logger: logging.Logger
    :param D: # of recent data instances to use for model training
    :type D: int
    :param W: window size (feature dimension)
    :type W: int
    """
    project_root_path = os.getenv("DA_DESIGN_SERVER")
    cfg = myconfig.get_config('{}/share/project.config'.format(project_root_path))
    db_ip = cfg['db']['ip']
    db_port = int(cfg['db']['port'])
    db_name = cfg['db']['name']

    db_client = MongoClient(db_ip, db_port)
    db = db_client[db_name]

    col_company = db[cfg['db']['col_contents']]
    col_pred_company_stock = db[cfg['db']['col_favorite']]

    doc_companies = col_company.find();
    if doc_companies:
        for doc_company in doc_companies:
            # If the document of this company doesn't exist, make it
            doc_pred_company_stock = col_pred_company_stock.find_one({'Company': doc_company['_id']})
            if not doc_pred_company_stock:
                col_pred_company_stock.insert_one({
                    'Company': doc_company["_id"],
                    'company_stock': []})
                doc_pred_company_stock = col_pred_company_stock.find_one({
                    'Company': doc_company['_id']})
            # Append new data
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            tomorrow = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day)
            doc_new_pred = col_pred_company_stock.find_one({
                'Company': doc_company['_id'], 'company_stock.date': tomorrow})
            if not doc_new_pred:
                m1 = model1()
                input_data = [x["value"] for x in doc_company["company_stock"]]
                output_value = m1.predict(input_data, logger, D, W)
                col_pred_company_stock.update_one(
                        {'Company': doc_company['_id']},
                        {'$push': {
                            'company_stock': {
                                'date': tomorrow,
                                'value': float(output_value)
                            }
                        }}
                    )
                logger.info('{} {}: new prediction in DB = {}'.format(
                    tomorrow, doc_company['name'], output_value))
            else:
                logger.info('{} {}: prediction already exists, so skipped.'.format(
                    tomorrow, doc_company['name']))

    db_client.close()

class model2:
    """Model for service 2 (get a list of similar companies)
    """
    def predict(self, data, logger, D):
        """Compute similarities between companies, and get ranked lists of the most similar companies

        :param data: dictionary of stock sequences {company: [{date, value}, ...]}
        :type data: dict
        :param logger: logger instance
        :type logger: logging.Logger
        :param D: # of stock values to use for training model
        :type D: int
        :return: Ranked lists [#company][#company]
        :rtype: list
        """
        logger.info('Model 2 begin')
        if not data:
            logger.error('No companies in data')
            return None
        for _, v in data.items():
            if not v:
                logger.error('No stock values in data')
                return None
        # data conversion
        company_names = list(data.keys())
        target_data = []
        for c in company_names:
            dv_pairs = data[c]
            if len(dv_pairs) <= D:
                dv_pairs = [dv_pairs[0]] * (D-len(dv_pairs)) + dv_pairs
            else:
                dv_pairs = dv_pairs[len(dv_pairs)-D:]
            target_data += [dv_pairs]

        target_data = np.array(target_data)
        mean = target_data.mean(axis=1)
        adjusted_data = target_data - mean[:, None]
        sim_matrix = 1 - squareform(pdist(adjusted_data, 'cosine'))
        nans = np.isnan(sim_matrix)
        sim_matrix[nans] = -1

        ranked_list = np.fliplr(np.argsort(sim_matrix, axis=1)[:, :-1])

        result = dict()
        for i, c in enumerate(company_names):
            result[c] = [(company_names[x], sim_matrix[i][x]) for x in ranked_list[i]]

        logger.info('Model 2 end')
        return result

def run_model2(logger, D=10):
    """Run model 2

    :param logger: logger instance
    :type logger: logging.Logger
    :param D: # of recent data instances to use for model training
    :type D: int
    """
    project_root_path = os.getenv("DA_DESIGN_SERVER")
    cfg = myconfig.get_config('{}/share/project.config'.format(project_root_path))
    db_ip = cfg['db']['ip']
    db_port = int(cfg['db']['port'])
    db_name = cfg['db']['name']

    db_client = MongoClient(db_ip, db_port)
    db = db_client[db_name]

    col_company = db[cfg['db']['col_contents']]
    col_similar_company_list = db[cfg['db']['col_favorite']]

    doc_companies = col_company.find();
    if not doc_companies:
        return

    # prepare data & create document if it doesn't exist
    input_data = dict()
    for doc_company in doc_companies:
        # If the document of this company doesn't exist, make it
        doc_sim_companies = col_similar_company_list.find_one({'Company': doc_company['_id']})
        if not doc_sim_companies:
            col_similar_company_list.insert_one({
                'Company': doc_company["_id"],
                'similar_list': []})
            #doc_sim_companies = col_similar_company_list.find_one({
            #    'Company': doc_company['_id']})
        tmp_stocks = []
        for dv_dict in doc_company['company_stock']:
            tmp_stocks += [dv_dict['value']]
        input_data[doc_company['name']] = tmp_stocks
    # compute results
    m2 = model2()
    result = m2.predict(input_data, logger, D)

    for c, sims in result.items():
        doc_company = col_company.find_one({'name': c})
        col_similar_company_list.update_one(
                {'Company': doc_company['_id']},
                {'$set': {'similar_list': sims}}
                )
        logger.info('{}: {} new similar list in DB'.format(
                    c, len(sims)))
    db_client.close()


def get_service1_result(companies, logger):
    """Get stuff for service 1.

    :param companies: list of companies(names)
    :type companies: list
    :param logger: logger instance
    :type logger: logging.Logger
    :return: {company: {recent: {date: _, value: _}, predicted: {date: _, value: _}}}
    :rtype: dict
    """
    project_root_path = os.getenv("DA_DESIGN_SERVER")
    cfg = myconfig.get_config('{}/share/project.config'.format(project_root_path))
    db_ip = cfg['db']['ip']
    db_port = int(cfg['db']['port'])
    db_name = cfg['db']['name']

    db_client = MongoClient(db_ip, db_port)
    db = db_client[db_name]

    col_company = db[cfg['db']['col_contents']]
    col_pred_company_stock = db[cfg['db']['col_favorites']]

    result = dict()
    for cname in companies:
        result[cname] = dict()
        result[cname]['recent'] = dict()
        result[cname]['predicted'] = dict()
        doc_company = col_company.find_one({"name": cname})
        if not doc_company:
            db_client.close()
            continue
        if doc_company['company_stock']:
            result[cname]['recent'] = list(doc_company['company_stock'])[-1]
        doc_pred_stock = col_pred_company_stock.find_one({'Company': doc_company['_id']})
        if not doc_pred_stock:
            db_client.close()
            continue
        preds = doc_pred_stock['company_stock']
        if not preds:
            db_client.close()
            continue
        result[cname]['predicted'] = preds[-1]

    db_client.close()
    return result

def get_service2_result(company, logger):
    """ Get stuff for service 2.


    :param company: company name
    :type company: str
    :param logger: logger instance
    :type logger: logging.Logger
    :return: {similar_list: [(company_name, score), ...]}
    :rtype: dict
    """
    project_root_path = os.getenv("DA_DESIGN_SERVER")
    cfg = myconfig.get_config('{}/share/project.config'.format(project_root_path))
    db_ip = cfg['db']['ip']
    db_port = int(cfg['db']['port'])
    db_name = cfg['db']['name']

    db_client = MongoClient(db_ip, db_port)
    db = db_client[db_name]

    col_company = db[cfg['db']['col_contents']]
    col_similar_company_list = db[cfg['db']['col_favorites']]

    result = dict()
    doc_company = col_company.find_one({'name': company})
    if not doc_company:
        db_client.close()
        return result

    doc_sims = col_similar_company_list.find_one({'Company': doc_company['_id']})
    if not doc_sims:
        db_client.close()
        return result

    tmp_result = doc_sims['similar_list']
    if not tmp_result:
        db_client.close()
        return result

    db_client.close()
    result['similar_list'] = tmp_result
    return result

