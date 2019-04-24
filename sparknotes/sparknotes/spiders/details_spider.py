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
        self.file_name = 'shelve/sparknotes_book_detail.json'
        self.domain = 'https://www.sparknotes.com'
        self.book = Book()
        self.summary = {}
        self.characters = {}
        self.main_ideas = {}
        self.quotes = {}
        self.pagination_links = []
        self.index = 0

    def start_requests(self):
        # with jsonlines.open('shelve/sparknotes_book_link.jl') as reader:
        #     for obj in reader:
        #         url = self.domain + obj['link']
        #         yield scrapy.Request(url=url, callback=self.parse)

        yield scrapy.Request(url='https://www.sparknotes.com/lit/1984/', callback=self.parse)
        # yield scrapy.Request(url='https://www.sparknotes.com/lit/2001/', callback=self.parse)

    def parse(self, response):
        self.book['title'] = response.xpath('normalize-space(/html/body/div[4]/div[1]/h1/a/text())').extract_first()
        self.book['author'] = response.xpath(
            'normalize-space(//*[@id="titlepage_author_link1"]/text())').extract_first()

        picture_link = response.xpath('//*[@id="buynow_thumbnail1"]/@src').extract_first()
        if picture_link is not None:
            self.book['picture'] = self.domain + picture_link

        self.book['summary_sentence'] = response.xpath('/html/body/div[4]/p/descendant-or-self::*/text()').extract()
        self.summary['link'] = self.domain + response.xpath(
            '//*[@id="content-container--expander"]/div[1]/div/div[2]/div[1]/ul/li[1]/a/@href').extract_first()

        character_link = response.xpath(
            '//*[@id="content-container--expander"]/div[2]/div/div[2]/div/ul/li[1]/a/@href').extract_first()
        if character_link is not None:
            self.characters['link'] = self.domain + character_link

        main_ideas_link = response.xpath(
            '//*[@id="content-container--expander"]/div[3]/div/div[2]/div/ul/li[1]/a/@href').extract_first()
        if main_ideas_link is not None:
            self.main_ideas['link'] = self.domain + main_ideas_link
            self.main_ideas['themes'] = {}

        quotes_link = response.xpath(
            '//*[@id="content-container--expander"]/div[4]/div/div[2]/ul/li/a/@href').extract_first()
        if quotes_link is not None:
            self.quotes['link'] = self.domain + quotes_link
            self.quotes['important_quotations_explained'] = {}
        # '//*[@id="content-container--expander"]/div[4]/div/div[2]/div/ul/li/a'

        yield scrapy.Request(url=self.summary['link'], callback=self.get_plot)

    def get_plot(self, response):
        text = response.xpath('//*[@id="plotoverview"]/descendant-or-self::*/text()').extract()
        self.summary['plot_overview'] = text
        self.book['summary'] = self.summary
        # yield self.book
        yield scrapy.Request(url=self.characters['link'], callback=self.get_character)

    def get_character(self, response):
        self.characters['character_list'] = {}
        for character in response.xpath('//*[@id="characterlist"]/div[@class="content_txt"]'):
            name = character.xpath('./@id').extract_first()
            text = character.xpath('./text()').extract()
            self.characters['character_list'][name] = text
        self.book['character_list'] = self.characters
        yield scrapy.Request(url=self.main_ideas['link'], callback=self.get_main_ideas)

    def get_main_ideas(self, response):
        if self.index == 0:
            self.pagination_links = response.xpath('//*[@class="pagination-links"][1]/a/@href').extract()
            self.index = 0 if self.pagination_links == [] or len(self.pagination_links) == 1 else 1

        for index, theme in enumerate(response.xpath('//*[@id="section"]/h3')):
            print("!!!!!!!!!!!!!!!!", index)
            name = theme.xpath('./text()').extract_first()
            # 终于写出来了(´；ω；`)
            text = theme.xpath('./following-sibling::p[count(preceding::h3)=%d]/descendant-or-self::*/text()' % (index + 1)).extract()
            self.main_ideas['themes'][name] = text

        if 0 < self.index < len(self.pagination_links):
            # for theme in response.xpath('//*[@id="section"]/h3'):
            #     name = theme.xpath('./text()').extract_first()
            #     text = theme.xpath('./following-sibling::p/text()')
            #     self.main_ideas['themes'][name] = text
            next_page = self.main_ideas['link'] + self.pagination_links[self.index]
            yield scrapy.Request(url=next_page, callback=self.get_main_ideas)
            self.index += 1
        else:
            # page = response.xpath('//*[@class="studyGuideText"]/descendant-or-self::*/text()').extract()
            # self.main_ideas['themes'][self.index] = page
            self.book['main_ideas'] = self.main_ideas
            self.index = 0
            yield scrapy.Request(url=self.quotes['link'], callback=self.get_quotes)

    def get_quotes(self, response):
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
