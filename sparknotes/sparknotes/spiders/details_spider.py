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
        self.file_name = 'shelve/sparknotes_book_detail2.jl'
        self.domain = 'https://www.sparknotes.com'
        saved = {}
        self.saved = saved
        with jsonlines.open('shelve/sparknotes_book_detail.jl') as reader:
            for obj in reader:
                saved[obj['title']] = True

    def start_requests(self):
        # yield scrapy.Request(url='https://www.sparknotes.com/lit/1984/', callback=self.parse)
        print('start')
        with jsonlines.open('shelve/sparknotes_book_link.jl') as reader:
            for index, obj in enumerate(reader):
                if obj['title'] in self.saved:
                    continue
                url = self.domain + obj['link']
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        root_url = response.url
        book = Book()
        summary = {}
        characters = {}
        main_ideas = {}
        quotes = {}
        further_study = {}
        pagination_links = []
        index = 0

        summary['link'] = root_url + 'summary/'
        characters['link'] = root_url + 'characters/'
        characters['character_list'] = {}
        main_ideas['link'] = root_url + 'themes/'
        main_ideas['themes'] = {}
        quotes['link'] = root_url + 'quotes/'
        quotes['important_quotations_explained'] = {}
        further_study['context_link'] = root_url + 'context/'
        further_study['study-questions_link'] = root_url + 'study-questions/'
        further_study['study-questions'] = {}

        book['title'] = response.xpath('normalize-space(/html/body/div[4]/div[1]/h1/a/text())').extract_first()
        book['author'] = response.xpath(
            'normalize-space(//*[@id="titlepage_author_link1"]/text())').extract_first()
        book['summary_sentence'] = response.xpath('/html/body/div[4]/p/descendant-or-self::*/text()').extract()

        picture_link = response.xpath('//*[@id="buynow_thumbnail1"]/@src').extract_first()
        if picture_link is not None:
            book['picture'] = self.domain + picture_link

        request = scrapy.Request(url=summary['link'], callback=self.get_plot)
        request.meta['payload'] = {
            'book': book,
            'summary': summary,
            'characters': characters,
            'main_ideas': main_ideas,
            'quotes': quotes,
            'further_study': further_study,
            'pagination_links': pagination_links,
            'index': index,
        }
        yield request

    def get_plot(self, response):
        payload = response.meta['payload']

        text = response.xpath('//*[@id="plotoverview"]/descendant-or-self::*/text()').extract()
        payload['summary']['plot_overview'] = text
        payload['book']['summary'] = payload['summary']

        request = scrapy.Request(url=payload['characters']['link'], callback=self.get_character)
        request.meta['payload'] = payload
        yield request

    def get_character(self, response):
        payload = response.meta['payload']

        if response.status == 200:
            for character in response.xpath('//*[@id="characterlist"]/div[@class="content_txt"]'):
                name = character.xpath('./@id').extract_first()
                text = character.xpath('./text()').extract()
                payload['characters']['character_list'][name] = text
            payload['book']['character_list'] = payload['characters']

        request = scrapy.Request(url=payload['main_ideas']['link'], callback=self.get_main_ideas)
        request.meta['payload'] = payload
        yield request

    def get_main_ideas(self, response):
        payload = response.meta['payload']

        if response.status == 200:
            if payload['index'] == 0:
                payload['pagination_links'] = response.xpath('//*[@class="pagination-links"][1]/a/@href').extract()
                payload['index'] = 0 if payload['pagination_links'] == [] or len(
                    payload['pagination_links']) == 1 else 1

            for index, theme in enumerate(response.xpath('//*[@id="section"]/h3')):
                name = theme.xpath('./text()').extract_first()
                # 终于写出来了(´；ω；`)
                text = theme.xpath('./following-sibling::p[count(preceding::h3)=%d]/descendant-or-self::*/text()' % (
                        index + 1)).extract()
                payload['main_ideas']['themes'][name] = text

            if 0 < payload['index'] < len(payload['pagination_links']):
                next_page = payload['main_ideas']['link'] + payload['pagination_links'][payload['index']]
                payload['index'] += 1

                request = scrapy.Request(url=next_page, callback=self.get_main_ideas)
                request.meta['payload'] = payload
                yield request
            else:
                payload['book']['main_ideas'] = payload['main_ideas']
                payload['index'] = 0

                request = scrapy.Request(url=payload['quotes']['link'], callback=self.get_quotes)
                request.meta['payload'] = payload
                yield request

        else:
            request = scrapy.Request(url=payload['quotes']['link'], callback=self.get_quotes)
            request.meta['payload'] = payload
            yield request

    def get_quotes(self, response):
        payload = response.meta['payload']

        if response.status == 200:
            if payload['index'] == 0:
                payload['pagination_links'] = response.xpath('//*[@class="pagination-links"][1]/a/@href').extract()
                payload['index'] = 0 if payload['pagination_links'] == [] or len(
                    payload['pagination_links']) == 1 else 1

            quote = response.xpath(
                '//*[@id="importantquotations"]/div/div/div/blockquote/descendant-or-self::*/text()').extract()
            quote = ' '.join(list(map(str.strip, quote)))
            text = response.xpath('//*[@id="importantquotations"]/div/p/descendant-or-self::*/text()').extract()
            payload['quotes']['important_quotations_explained'][quote] = text

            if 0 < payload['index'] < len(payload['pagination_links']):
                next_page = payload['quotes']['link'] + payload['pagination_links'][payload['index']]
                payload['index'] += 1

                request = scrapy.Request(url=next_page, callback=self.get_quotes)
                request.meta['payload'] = payload
                yield request
            else:
                payload['book']['quotes'] = payload['quotes']
                yield payload['book']
        else:
            yield payload['book']
