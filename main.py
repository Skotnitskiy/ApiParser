import argparse
import os
import logging.config

import psycopg2
import requests
import sys
from pandas import *
from datetime import datetime
from pprint import pprint

from psycopg2.extras import RealDictCursor
from psycopg2.sql import SQL, Identifier

import config as conf

conn = psycopg2.connect(database=conf.db_name, user=conf.db_user, host=conf.db_host)
cursor = conn.cursor()
dict_cur = conn.cursor(cursor_factory=RealDictCursor)


def init_database():
    for categorie in conf.categories_list:
        cursor.execute(conf.db_init.format(categorie))
    conn.commit()


def create_report(table_name):
    with open('front/date.html', 'w') as f:
        date = '<center><h1> Report from: ' + datetime.today().strftime("%Y-%m-%d %H:%M:%S") + '</h1></center>'
        f.write(date)

        get_table_query = SQL("SELECT * FROM {}").format(Identifier(table_name))
        dict_cur.execute(get_table_query)
        r = dict_cur.fetchall()
        rep = DataFrame(r)
        rep.to_html('front/{}.html'.format(table_name), index=False)


class Parser(object):

    @staticmethod
    def init_reports():
        for categorie in conf.categories_list:
            if not os.path.exists('front/' + categorie + '.html'):
                DataFrame().to_html('front/' + categorie + '.html', index=False)

    @staticmethod
    def write_record(table, record, old_ids):
        id = record.get('id')
        if id not in old_ids:
            cursor.execute(SQL("INSERT INTO {}(id) VALUES (%s)").format(Identifier(table)), (id, ))
            conn.commit()
            print("===================Inserted new record!===================")
        for column, value in record.items():
            cursor.execute(SQL("UPDATE {} SET {} = %s WHERE id = %s;").
                           format(Identifier(table), Identifier(column)), (value, str(id)))
            conn.commit()

    @staticmethod
    def get_old_ids(table_name):
        get_ids_query = SQL("SELECT id FROM {}").format(Identifier(table_name))
        cursor.execute(get_ids_query)
        ids = cursor.fetchall()
        ids_int = []
        for id in ids:
            ids_int += [int(id[0])]
        return ids_int

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
        init_database()

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
            print('categorie', categorie, "ids received")
        return ids_records

    def record(self):
        ids_records = self.get_records_id()
        self.logger.info("report generation started...")
        record_line = {}
        for key, val in ids_records.items():
            old_ids = self.get_old_ids(key)
            for id_rec in val:
                try:
                    record_line = requests.get(conf.item_url.format(id_rec)).json()
                except requests.exceptions.RequestException as e:
                    self.logger.error(e)
                    print(e)
                if record_line is not None:
                    if record_line.get("score") >= conf.score:
                        date = datetime.date(datetime.fromtimestamp((record_line.get('time'))))
                        if date >= conf.from_date:
                            self.write_record(key, record_line, old_ids)
                            self.logger.info("record {} added to result list".format(id_rec))
                            pprint(record_line)
            create_report(key)


parser = Parser()
parser.record()
