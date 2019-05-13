# 132 Final Project

## Topic
Student reading carnival

## Goal
All purpose search on books

## Team Members 
- Linxuan Yang
- Ye Hong
- Chenfeng Fan 
- Limian Guo 

## Dependencies
- [Python 3](https://www.python.org/)
- [Requests](https://2.python-requests.org//en/master/)
- [Scrapy](https://docs.scrapy.org/en/latest/)

## Build Instructions
```$ pip3 install requests```  
```$ pip3 install Scrapy```

## Run Instructions
- Get book titles json file with category @goodreads  
```$ python goodreads/goodreads_title_crawler.py```

- Get literature json file @sparknotes  
    1. ```$ cd sparknotes```
    2. ```$ scrapy crawl titles```, this will get all book titles and links in literature tab
    3. ```$ scrapy crawl details```, this will get all data for each book

    ```2019-05-09 16:52:48 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
        {'downloader/exception_count': 22,
         'downloader/exception_type_count/twisted.internet.error.NoRouteError': 16,
         'downloader/exception_type_count/twisted.internet.error.TimeoutError': 6,
         'downloader/request_bytes': 5375772,
         'downloader/request_count': 5985,
         'downloader/request_method_count/GET': 5985,
         'downloader/response_bytes': 48833687,
         'downloader/response_count': 5963,
         'downloader/response_status_count/200': 5667,
         'downloader/response_status_count/404': 296,
         'dupefilter/filtered': 9,
         'finish_reason': 'finished',
         'finish_time': datetime.datetime(2019, 5, 9, 20, 52, 48, 906551),
         'item_scraped_count': 579,
         'log_count/DEBUG': 6565,
         'log_count/INFO': 396,
         'log_count/WARNING': 1,
         'memusage/max': 78176256,
         'memusage/startup': 50728960,
         'request_depth_max': 12,
         'response_received_count': 5963,
         'retry/count': 22,
         'retry/reason_count/twisted.internet.error.NoRouteError': 16,
         'retry/reason_count/twisted.internet.error.TimeoutError': 6,
         'robotstxt/request_count': 1,
         'robotstxt/response_count': 1,
         'robotstxt/response_status_count/200': 1,
         'scheduler/dequeued': 5984,
         'scheduler/dequeued/memory': 5984,
         'scheduler/enqueued': 5984,
         'scheduler/enqueued/memory': 5984,
         'start_time': datetime.datetime(2019, 5, 9, 5, 29, 9, 874055)}
        2019-05-09 16:52:48 [scrapy.core.engine] INFO: Spider closed (finished)
    ```
## Data
- what we achieve
- methods

## Index
- what we achieve
- methods\
  1. Clean and organize raw data from @sparknotes ```$ index.py```\
  2. For each book, each key/field associate with a string of related text

## Query
- what we achieve
- methods
    1. Words in ```""```: phrase search
    2. ```-word```: difference search only
    3. ```+word```: conjunctive search only
    4. "More like this" button
    5. input auto completion function
- running instruction
```python3 query.py```
## Databse
- you need a proper SQLite command working on your computer to have
access to our databse
## UI
- we use Bootstrap to build a progressive single page web application
- methods


## References
- https://doc.scrapy.org/en/xpath-tutorial/intro/tutorial.html
- https://jsonlines.readthedocs.io/en/latest/


