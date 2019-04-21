import scrapy
from sparknotes.items import BookLink


class TitlesSpider(scrapy.Spider):
    name = 'titles'
    custom_settings = {
        'ITEM_PIPELINES': {
            'sparknotes.pipelines.JsonWriterPipeline': 300,
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.file_name = 'shelve/sparknotes_book_links.jl'

    def start_requests(self):
        urls = [
            'https://www.sparknotes.com/lit/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for item in response.xpath('//div[@class="letter-list__filter-item"]'):
            book = BookLink()
            book['title'] = item.xpath('normalize-space(./h3/a/text())').extract_first()
            book['author'] = item.xpath('./p/descendant-or-self::*/text()').extract()
            book['link'] = item.xpath('./h3/a/@href').extract_first()
            yield book

    def get_html(self, response):
        filename = 'sparknotes_lit.html'
        with open('html/' + filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
