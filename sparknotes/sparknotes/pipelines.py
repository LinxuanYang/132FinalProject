# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy.exporters import JsonLinesItemExporter


class JsonWriterPipeline(object):
    """
    A typical output of this exporter would be:
    {"name": "Color TV", "price": "1200"}
    {"name": "DVD player", "price": "200"}
    """

    def __init__(self):
        self.file = open('shelve/sparknotes_book_link.json', 'wb')
        # the format produced by this exporter is well suited for serializing large amounts of data.
        self.exporter = JsonLinesItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
