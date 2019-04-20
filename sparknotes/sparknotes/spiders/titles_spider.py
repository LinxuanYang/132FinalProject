import scrapy


class TitlesSpider(scrapy.Spider):
    name = 'titles'

    def start_requests(self):
        urls = [
            'https://www.sparknotes.com/lit/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url
        filename = 'sparknotes_lit.html'
        with open('html/' + filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
