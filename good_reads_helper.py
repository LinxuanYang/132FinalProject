import json

dict_by_type = {}
with open('./goodreads/shelve/reformed_goodread.json') as file:
    data = json.load(file)
    for key in data:
        item = data[key]
        for cate in item['category']:
            cate_list = dict_by_type.get(cate, [])
            cate_list.append(item)
            dict_by_type[cate] = cate_list
        rate = item['rate'][11:14]
        rate_num = item['rate']
        item['rate'] = float(rate)
        left = rate_num.rindex('(') + 1
        right = rate_num.rindex('ratings') - 1
        item['rate_num'] = rate_num[left:right]
    for key in dict_by_type:
        dict_by_type[key].sort(key=lambda x: -x['rate'])


def find_recommendation(category, page_num=1):
    return dict_by_type[category]
