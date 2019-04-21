import json
import jsonlines
import scrapy
from sparknotes.items import Book


class DetailsSpider(scrapy.Spider):
    name = 'details'
    custom_settings = {
        'ITEM_PIPELINES': {
            'sparknotes.pipelines.BookLinkJsonWriterPipeline': 300,
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_name = 'shelve/sparknotes_book_detail.jl'

    def start_requests(self):
        domain = 'https://www.sparknotes.com'
        with jsonlines.open('shelve/sparknotes_book_link.jl') as reader:
            for obj in reader:
                url = domain + obj['link']
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        summary_sentence = '/html/body/div[4]/p/text()'

        summary = {}
        for link in response.xpath('//*[@id="content-container--expander"]/div[1]/div/div[2]/div[1]/ul'):
            summary[link.xpath('./li[1]/a')] = ''

        yield {
            'title': response.xpath('/html/body/div[4]/div[1]/h1/a/text()'),
            'author': response.xpath('normalize-space(//*[@id="titlepage_author_link1"]/text())'),
            'picture': 'https:' + response.xpath('//*[@id="buynow_thumbnail1"]/@src'),
            'summary_sentence': response.xpath(
                'normalize-space(/html/body/div[4]/p/descendant-or-self::*/text())').extract(),
            'summary': summary,

        }
