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
   author        VARCHAR(100),\
   descendants 	 VARCHAR(15),\
   id_record     VARCHAR(20) UNIQUE,\
   kids          TEXT,\
   score         VARCHAR(20),\
   article_text  TEXT,\
   article_time  TIMESTAMP,\
   title         VARCHAR(300),\
   article_type  VARCHAR(100),\
   url           TEXT\
);'