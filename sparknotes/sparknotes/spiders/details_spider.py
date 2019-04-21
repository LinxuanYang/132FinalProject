import json
import jsonlines
import scrapy
from sparknotes.items import Book


class DetailsSpider(scrapy.Spider):
    name = 'details'
    custom_settings = {
        'ITEM_PIPELINES': {
            'sparknotes.pipelines.JsonWriterPipeline': 300,
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_name = 'shelve/sparknotes_book_detail.jl'
        self.domain = 'https://www.sparknotes.com'
        self.book = Book()
        self.summary = {}

    def start_requests(self):
        domain = 'https://www.sparknotes.com'
        # with jsonlines.open('shelve/sparknotes_book_link.jl') as reader:
        #     for obj in reader:
        #         url = domain + obj['link']
        #         yield scrapy.Request(url=url, callback=self.parse)
        yield scrapy.Request(url='https://www.sparknotes.com/lit/1984/', callback=self.parse)

    def parse(self, response):
        self.book['title'] = response.xpath('normalize-space(/html/body/div[4]/div[1]/h1/a/text())').extract_first()
        self.book['author'] = response.xpath(
            'normalize-space(//*[@id="titlepage_author_link1"]/text())').extract_first()
        self.book['picture'] = 'https:' + response.xpath('//*[@id="buynow_thumbnail1"]/@src').extract_first()
        self.book['summary_sentence'] = ''.strip().join(response.xpath(
            '/html/body/div[4]/p/descendant-or-self::*/text()').extract())
        self.summary['link'] = self.domain + response.xpath(
            '//*[@id="content-container--expander"]/div[1]/div/div[2]/div[1]/ul/li[1]/a/@href').extract_first()
        yield scrapy.Request(url=self.summary['link'], callback=self.get_plot)

    def get_plot(self, response):
        text = response.xpath('//*[@id="plotoverview"]/descendant-or-self::*/text()').extract()
        self.summary['plot_overview'] = text
        self.book['summary'] = self.summary
        yield self.book
