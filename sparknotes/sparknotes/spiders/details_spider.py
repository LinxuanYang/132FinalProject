import json
import scrapy
# from sparknotes.items import Book


class DetailsSpider(scrapy.Spider):
    name = 'details'

    def start_requests(self):
        domain = 'https://www.sparknotes.com'
        with open('shelve/sparknotes_titles.json', 'r') as f:
            # books = f
            for book in f:
                book = json.loads(book)
                url = domain + book['link']
                print(url)
                # yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        pass
        # summary_sentence = '/html/body/div[4]/p/text()'
        #
        # summary = {}
        # for link in response.xpath('//*[@id="content-container--expander"]/div[1]/div/div[2]/div[1]/ul'):
        #     summary[link.xpath('./li[1]/a')] = ''
        #
        # yield {
        #     'title': response.xpath('/html/body/div[4]/div[1]/h1/a/text()'),
        #     'author': response.xpath('normalize-space(//*[@id="titlepage_author_link1"]/text())'),
        #     'picture': 'https:' + response.xpath('//*[@id="buynow_thumbnail1"]/@src'),
        #     'summary_sentence': response.xpath(
        #         'normalize-space(/html/body/div[4]/p/descendant-or-self::*/text())').extract(),
        #     'summary': summary,
        #
        # }
        # for item in response.xpath('//div[@class="letter-list__filter-item"]'):
        #     yield {
        #         'title': item.xpath('normalize-space(./h3/a/text())').extract_first(),
        #         'author': item.xpath('./p/descendant-or-self::*/text()').extract(),
        #         'link': item.xpath('./h3/a/@href').extract_first()
        #     }
