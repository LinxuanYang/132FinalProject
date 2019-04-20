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
- Get book titles classified by school year @goodreads  
```$ python crawler/goodreads_title_crawler.py```

- Get literature book titles index html file @sparknotes  
    1. Go to 'sparknotes/' directory
    2. Run ```$ scrapy crawl titles```
