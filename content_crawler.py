import json

from crawler_test import Crawler
from collections import defaultdict

def read_from_json(filename):
    json_data = open(filename, encoding='UTF-8').read()
    return json.loads(json_data)

def content_from_sparknote(crawler, url):
    

def content_from_wikipedia():
    pass 

def list_from_sparknote():
    pass 

def output_to_json():
    pass

if __name__ == "__main__":
    book_with_content = defaultdict()
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    }
    crawler = Crawler(HEADER)
    url = 'https://www.sparknotes.com/lit/'
    bookdata = read_from_json('shelve/good_read_shelve.json')
    for category in bookdata:
        for bookname in bookdata[category]:
            content_from_sparknote(crawler, url, bookname)

    

