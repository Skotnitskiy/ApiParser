import argparse
import os
import logging.config
from datetime import datetime

import requests
import sys
import pickle
from pandas import *
from datetime import datetime
from pprint import pprint


import config as conf


class Parser(object):

    @staticmethod
    def init_reports():
        for categorie in conf.categories_list:
            if not os.path.exists('front/' + categorie + '.html'):
                DataFrame().to_html('front/' + categorie + '.html', index=False)

    def __init__(self):
        logging.config.dictConfig(conf.dictLogConfig)
        self.rep_empty = False
        self.logger = logging.getLogger("DataParserApp")
        self.logger.info("Program started")
        self.argpars = argparse.ArgumentParser(description='Data parse.')
        self.argpars.add_argument('-c', action="store", dest="categories", nargs='+', default=conf.default_categories,
                            choices=conf.categories_list)
        self.args = self.argpars.parse_args()
        self.init_reports()

    def get_records_id(self):
        ids_records = {}
        for categorie in self.args.categories:
            self.logger.info("request was sent to obtain the list of IDs by category {}".format(categorie))
            request = requests.get(conf.categorie_url.format(categorie))
            self.logger.info("list is received")
            try:
                ids_records.update({categorie: request.json()})
            except requests.exceptions.RequestException as e:
                self.logger.error(e)
                print(e)
                sys.exit(1)
            print(len(ids_records), "ids received")
        all_ids = []
        for vals in ids_records.values():
            all_ids += vals
        if not os.path.exists('ids.pic'):
            with open("ids.pic", "wb") as f:
                pickle.dump(all_ids, f)
            self.rep_empty = True
        return ids_records

    def get_records(self):
        ids_records = self.get_records_id()
        self.logger.info("report generation started...")
        all_records = []
        with open('ids.pic', 'rb') as f:
            pickle_ids = pickle.load(f)
        record_line = {}
        for key, val in ids_records.items():
            for id_rec in val:
                if id_rec not in pickle_ids or self.rep_empty:
                    try:
                        record_line = requests.get(conf.item_url.format(id_rec)).json()
                        if record_line is not None:
                            record_line.update({'temp_type': key})
                    except requests.exceptions.RequestException as e:
                        self.logger.error(e)
                        print(e)
                    if record_line is not None:
                        if record_line.get("score") >= conf.score:
                            date = datetime.date(datetime.fromtimestamp((record_line["time"])))
                            if date >= conf.from_date:
                                record_line["time"] = datetime.fromtimestamp((record_line["time"])).strftime(
                                    "%Y-%m-%d-%H:%M:%S")
                                all_records.append(record_line)
                                self.logger.info("record {} added to result list".format(id_rec))
                                pprint(record_line)
        all_ids = []
        for vals in ids_records.values():
            all_ids += vals
        with open('ids.pic', 'wb') as f:
            for id in all_ids:
                if id not in pickle_ids:
                    pickle_ids.append(id)
                    print('id', id, 'added')
            pickle.dump(pickle_ids, f)
        return all_records


def prepare_report(*args):
    for arg in args:
        for arr in arg:
            arr.pop('temp_type')


def json_to_html(all_records):
    with open('front/date.html', 'w') as f:
        date = '<center><h1> Report from: ' + datetime.today().strftime("%Y-%m-%d %H:%M:%S") + '</h1></center>'
        f.write(date)
    if len(all_records) != 0:
        askstories, showstories, newstories, jobstories = [], [], [], []
        for record in all_records:
            if record.get('temp_type') == 'askstories':
                askstories.append(record)
            elif record.get('temp_type') == 'showstories':
                showstories.append(record)
            elif record.get('temp_type') == 'newstories':
                newstories.append(record)
            elif record.get('temp_type') == 'jobstories':
                jobstories.append(record)

        prepare_report(askstories, showstories, newstories, jobstories)

        old_askstories_data_frames = pandas.read_html('front/askstories.html')
        if len(old_askstories_data_frames) != 0:
            old_askstories = old_askstories_data_frames[0]
            new_askstories = DataFrame(askstories)
            askstories_rep = pandas.concat([old_askstories, new_askstories])
            askstories_rep.to_html('front/askstories.html', index=False)
        else:
            DataFrame(askstories).to_html('front/askstories.html', index=False)

        old_showstories_data_frames = pandas.read_html('front/showstories.html')
        if len(old_showstories_data_frames) != 0:
            old_showstories = old_showstories_data_frames[0]
            new_showstories = DataFrame(showstories)
            showstories_rep = pandas.concat([old_showstories, new_showstories])
            showstories_rep.to_html('front/showstories.html', index=False)
        else:
            DataFrame(showstories).to_html('front/showstories.html', index=False)

        old_newstories_data_frames = pandas.read_html('front/newstories.html')
        if len(old_newstories_data_frames) != 0:
            old_newstories = old_newstories_data_frames[0]
            new_newstories = DataFrame(newstories)
            newstories_rep = pandas.concat([old_newstories, new_newstories])
            newstories_rep.to_html('front/newstories.html', index=False)
        else:
            DataFrame(newstories).to_html('front/newstories.html', index=False)

        old_jobstories_data_frames = pandas.read_html('front/jobstories.html')
        if len(old_jobstories_data_frames) != 0:
            old_jobstories = old_jobstories_data_frames[0]
            new_jobstories = DataFrame(jobstories)
            jobstories_rep = pandas.concat([old_jobstories, new_jobstories])
            jobstories_rep.to_html('front/jobstories.html', index=False)
        else:
            DataFrame(jobstories).to_html('front/jobstories.html', index=False)


parser = Parser()
records = parser.get_records()
json_to_html(records)