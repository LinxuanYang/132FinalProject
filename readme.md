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
## Index
- Clean and organize raw data from @sparknotes
```$ index.py```
- For each book, each key/field associate with a string of related text
## References
- https://doc.scrapy.org/en/xpath-tutorial/intro/tutorial.html
- https://jsonlines.readthedocs.io/en/latest/
