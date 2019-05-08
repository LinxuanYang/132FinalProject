import re
import json
import time
import datetime
import requests


class Crawler:
    def __init__(self, header):
        self.header = header
        self.session = requests.session()

    def get_page(self, url):
        return self.session.get(url, headers=self.header)

    def match_all(self, regex, string):
        return re.findall(regex, string)


def get_title(crawler):
    """
    get book title, author, avg rating, published time, details url
    :param crawler:
    :return:
    """
    shelve_url = 'https://www.goodreads.com/shelf/show/'  # ?page=2
    shelve = ['kindergarten', 'elementary-school', 'middle-school', 'high-school', 'college']

    shelve_dict = {}
    for category in shelve:
        print("Processing: ", category)
        # target = shelve_url + category
        book = {}
        titles = []
        try:
            for i in range(26):
                print("Page: ", i)
                page_text = crawler.get_page(f'{shelve_url + category}?page={i}').text

                titles = crawler.match_all(r'<a class="bookTitle" href=".*">(.*?)</a>', page_text)
                for title in titles:
                    book[title] =

                book['author']
            shelve_dict[category] = titles
            time.sleep(1)
        except:
            with open('shelve/good_read_shelve_except.json', 'a') as f:
                json.dump(shelve_dict, f)
        time.sleep(3)

    with open('shelve/good_read_title_2.json', 'w') as f:
        json.dump(shelve_dict, f)


if __name__ == '__main__':
    begin_time = datetime.datetime.now()

    # cookie is required for crawler to work
    HEADER = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        'cookie': 'csid=BAhJIhg4ODQtMDc5Njg4NS03MTQ2ODEyBjoGRVQ%3D--f61d1c499cb7adb1262fc792a099966bd0842957; locale=en; csm-sid=274-5029145-7704351; __utma=250562704.1831914308.1555643816.1555643816.1555643816.1; __utmc=250562704; __utmz=250562704.1555643816.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __qca=P0-1653451374-1555643816529; __gads=ID=243f116325f3a7fb:T=1555643817:S=ALNI_MbwzHhy3XKh1sWim3f-5fvSWSvmTQ; never_show_interstitial=true; p=m20HCkzw2_Ht603f1CakRqrlMvSIxSUjs85PE378ThfcNPUm; u=-V8BLAxdnIhOxgiJiok18oyj5hSF0kukenkJbVf0gJtybA7S; _session_id2=7877422abf7cf24a8b8b358a4637811a; __utmb=250562704.30.10.1555643816'}

    crawler = Crawler(HEADER)

    get_title(crawler)

    print("Cost time: ", datetime.datetime.now() - begin_time)
