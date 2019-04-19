import requests
import time
key='wHQjdSjf6cPw5IymLLWw'
secret= 'MthQ2PLjm4LuRWOIjk8AMnQZziSLUi3UUoNVu8oST4'


for i in range(1,26):
    r = requests.get(f'https://www.goodreads.com/shelf/show/high-school?page={i}')
    with open(f'./good_reads/high_school/{i}.txt','w',encoding='utf-8') as file:
        file.write(r.text,)
    time.sleep(0.5)

