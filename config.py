import datetime

categories_list = ["askstories", "showstories", "newstories", "jobstories"]
default_categories = categories_list
results_path = "../results/"
rep_file_name = "report.csv"
log_file_name = "hn_parser.log"
categorie_url = "https://hacker-news.firebaseio.com/v0/{}.json?print=pretty"
item_url = 'https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty'
from_date = datetime.date(2012, 1, 1)
score = 1
dictLogConfig = {
    "version": 1,
    "handlers": {
        "fileHandler": {
            "class": "logging.FileHandler",
            "formatter": "logFormatter",
            "filename": results_path + log_file_name
        }
    },
    "loggers": {
        "DataParserApp": {
            "handlers": ["fileHandler"],
            "level": "INFO",
        }
    },
    "formatters": {
        "logFormatter": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
}
db_init = 'CREATE TABLE IF NOT EXISTS {}(\
   by            VARCHAR(100),\
   descendants 	 VARCHAR(15),\
   id            TEXT UNIQUE,\
   kids          TEXT,\
   score         VARCHAR(20),\
   text          TEXT,\
   time          TEXT,\
   title         VARCHAR(300),\
   type          VARCHAR(100),\
   url           TEXT\
);'

db_host = 'localhost'
db_name = 'api_parser'
db_user = 'serg'
