#author: Lixuan Yang, Chenfeng Fan, Ye Hong, Limian Guo
from elasticsearch_dsl.analysis import tokenizer, analyzer, char_filter, token_filter

short_term_analyzer = analyzer('short_term_analyzer',
                               tokenizer='standard',
                               filter=['lowercase', 'stop', 'asciifolding', 'snowball'])

my_char_filter = char_filter(name_or_instance="my_char_filter", type='mapping',
                             mappings=["one => 1", "two => 2", "three => 3", "four => 4", "five => 5", "six => 6",
                                       "seven => 7", "eight => 8", "nine =>9",
                                       "- => ", "'=> ", ":=> "])

text_analyzer = analyzer('text_analyzer', tokenizer='pattern', char_filter=my_char_filter,
                         filter=['lowercase', 'snowball', 'asciifolding'])
name_analyzer = analyzer('name_analyzer', tokenizer='standard', filter=['lowercase', 'stop', 'asciifolding'])
