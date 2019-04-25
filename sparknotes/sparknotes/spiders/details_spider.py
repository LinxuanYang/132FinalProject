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
        self.characters = {}
        self.main_ideas = {}
        self.quotes = {}
        self.further_study = {}
        self.pagination_links = []
        self.index = 0

    def start_requests(self):
        # with jsonlines.open('shelve/sparknotes_book_link.jl') as reader:
        #     for obj in reader:
        #         url = self.domain + obj['link']
        #         yield scrapy.Request(url=url, callback=self.parse)
        urls = ['https://www.sparknotes.com/lit/absalom/', 'https://www.sparknotes.com/lit/1984/',
                'https://www.sparknotes.com/lit/the-absolutely-true-diary-of-a-part-time-indian/']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        root_url = response.url
        self.summary['link'] = root_url + 'summary/'
        self.characters['link'] = root_url + 'characters/'
        self.characters['character_list'] = {}
        self.main_ideas['link'] = root_url + 'themes/'
        self.main_ideas['themes'] = {}
        self.quotes['link'] = root_url + 'quotes/'
        self.quotes['important_quotations_explained'] = {}
        self.further_study['context_link'] = root_url + 'context/'
        self.further_study['study-questions_link'] = root_url + 'study-questions/'
        self.further_study['study-questions'] = {}

        self.book['title'] = response.xpath('normalize-space(/html/body/div[4]/div[1]/h1/a/text())').extract_first()
        self.book['author'] = response.xpath(
            'normalize-space(//*[@id="titlepage_author_link1"]/text())').extract_first()
        self.book['summary_sentence'] = response.xpath('/html/body/div[4]/p/descendant-or-self::*/text()').extract()

        picture_link = response.xpath('//*[@id="buynow_thumbnail1"]/@src').extract_first()
        if picture_link is not None:
            self.book['picture'] = self.domain + picture_link

        yield scrapy.Request(url=self.summary['link'], callback=self.get_plot)
        yield self.book

    def get_plot(self, response):
        text = response.xpath('//*[@id="plotoverview"]/descendant-or-self::*/text()').extract()
        self.summary['plot_overview'] = text
        self.book['summary'] = self.summary
        yield scrapy.Request(url=self.characters['link'], callback=self.get_character)
        yield self.book

    def get_character(self, response):
        if response.status == 200:
            for character in response.xpath('//*[@id="characterlist"]/div[@class="content_txt"]'):
                name = character.xpath('./@id').extract_first()
                text = character.xpath('./text()').extract()
                self.characters['character_list'][name] = text
            self.book['character_list'] = self.characters
        yield scrapy.Request(url=self.main_ideas['link'], callback=self.get_main_ideas)
        yield self.book

    def get_main_ideas(self, response):
        if response.status == 200:
            if self.index == 0:
                self.pagination_links = response.xpath('//*[@class="pagination-links"][1]/a/@href').extract()
                self.index = 0 if self.pagination_links == [] or len(self.pagination_links) == 1 else 1

            for index, theme in enumerate(response.xpath('//*[@id="section"]/h3')):
                name = theme.xpath('./text()').extract_first()
                # 终于写出来了(´；ω；`)
                text = theme.xpath('./following-sibling::p[count(preceding::h3)=%d]/descendant-or-self::*/text()' % (
                        index + 1)).extract()
                self.main_ideas['themes'][name] = text

            if 0 < self.index < len(self.pagination_links):
                next_page = self.main_ideas['link'] + self.pagination_links[self.index]
                yield scrapy.Request(url=next_page, callback=self.get_main_ideas)
                self.index += 1
            else:
                self.book['main_ideas'] = self.main_ideas
                self.index = 0
                yield scrapy.Request(url=self.quotes['link'], callback=self.get_quotes)
                yield self.book

        else:
            yield scrapy.Request(url=self.quotes['link'], callback=self.get_quotes)

    def get_quotes(self, response):
        if response.status == 200:
            if self.index == 0:
                self.pagination_links = response.xpath('//*[@class="pagination-links"][1]/a/@href').extract()
                self.index = 0 if self.pagination_links == [] or len(self.pagination_links) == 1 else 1
            if 0 < self.index < len(self.pagination_links):
                page = response.xpath('//*[@id="importantquotations"]/descendant-or-self::*/text()').extract()
                self.quotes['important_quotations_explained'][self.index] = page
                next_page = self.quotes['link'] + self.pagination_links[self.index]
                yield scrapy.Request(url=next_page, callback=self.get_quotes)
                self.index += 1
            else:
                page = response.xpath('//*[@id="importantquotations"]/descendant-or-self::*/text()').extract()
                self.quotes['important_quotations_explained'][self.index] = page
                self.book['quotes'] = self.quotes
                yield self.book
        else:
            yield self.book
