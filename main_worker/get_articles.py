import time
import requests
from os.path  import basename
import json

from datetime import datetime
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

articleLinks = set()
dataAll = list()

def download_article_image(src):
    with open('/data/today/images/'+basename(src),"wb") as f:
        f.write(requests.get(src).content)
  
def getArticles(tag, page):  
    url = f'https://www.trtworld.com/{tag}?page={page}'
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')   
    articleLinks = {'https://www.trtworld.com' + a['href'] for a in soup.find_all('a', {'class': 'gtm-topic-latest-article'})}

    for articleLink in articleLinks:
        r = requests.get(articleLink, headers=headers)
        item = BeautifulSoup(r.text, 'html.parser')
        content_image = item.find("figure", {"class":"content-image"})
        
        if content_image:
            content_image = content_image.find('img')
            content_image_src = content_image['src'].replace("w32", "w1080/h1080")
            content_image_src = content_image_src.replace("q50", "q75")
            content_image_basename = basename(content_image_src)
            print(content_image['src'])
        content = item.find("div", {"class":"contentBox bg-w noMedia"})

        if content:
            content = content.findAll('p')
            data = {'tag': tag,
                    'datetime': datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),  
                    'title': item.find('h1', {'class': 'article-title'}).text,
                    'website': 'trtworld',
                    'article_url': articleLink,
                    'article_image_src': content_image_src, 
                    'article_image_basename': content_image_basename,
                    'article': [p.text for p in content]}
            download_article_image(content_image_src)
            dataAll.append(data)
            time.sleep(1)
            #print(data)
    
    with open('/data/today/json/articles_' + 'trtworld_' + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+'.json', 'w') as outfile:
        json.dump(dataAll, outfile)

    return dataAll