from bs4 import BeautifulSoup as soup
from datetime import date
import requests

class scrapertool:
    def __init__(self) -> None:
        self.today = date.today()
        
    def scrape(self):
        news=[]
        d = self.today.strftime("%m-%d-%y")
        print("date =", d)

        cnn_url="https://retail.economictimes.indiatimes.com/tag/franchise".format(d)
        cnn_url
        html = requests.get(cnn_url)
        bsobj = soup(html.content,'lxml')
        # print(bsobj)
        i=0
        for headline in bsobj.findAll('li', attrs={'class':'clearfix article-type-'}):
            # print('News-{}'.format(i))
            news.append({})
            for link in headline.findAll('a'):
                # print('page link:{}'.format(link['href']))
                news[i]['pagelink']=link['href']
                # print()
            for img in headline.findAll('img'):
                # print('imgsrc:{}'.format(img['data-src']))
                news[i]['imgurl']=img['data-src']
                # print()
            for heading in headline.findAll('h3'):
                # print('Heading-{}'.format(heading.text.strip()))
                news[i]['heading']=heading.text.strip()
                # print()
            for desc in headline.findAll('p'):
                # print('desc.-{}'.format(desc.text.strip()))
                news[i]['desc']=desc.text.strip()
                # print()
            # print ('imgurl:{}'.format(headline["data-src"]))
            # print('headline: {}'.format(headline.text.strip()))
            # print('-------------------------------------------------------------------------------------------------------------------------------')
            i=i+1
        for data in bsobj.findAll('div',attrs={'class':'all-items'}):
            
            for headline in data.findAll('li',attrs={'class':'clearfix article-type-'}):
                news.append({})
                for link in headline.findAll('a'):
                    # print('page link:{}'.format(link['href']))
                    news[i]['pagelink']=link['href']
                    # print()
                for img in headline.findAll('img'):
                    # print('imgsrc:{}'.format(img['data-src']))
                    news[i]['imgurl']=img['data-src']
                    # print()
                for heading in headline.findAll('h3'):
                    # print('Heading-{}'.format(heading.text.strip()))
                    news[i]['heading']=heading.text.strip()
                    # print()
                for desc in headline.findAll('p'):
                    # print('desc.-{}'.format(desc.text.strip()))
                    news[i]['desc']=desc.text.strip()
                    # print()
                # print('-----------------------------------------------------------------------------------------------------------------------------')
                i=i+1
        # print(news)
        return(news)


def article_scrapper(article_url):
    try:
        html = requests.get(article_url)
        bsobj = soup(html.content,'lxml')
        img_url=bsobj.findAll('meta', attrs={'property':'og:image'})[0]['content']
        title=bsobj.findAll('meta', attrs={'property':'og:title'})[0]['content']
        desc=bsobj.findAll('meta', attrs={'property':'og:description'})[0]['content']
        return {'status':True, 'img_url':img_url, 'title':title, 'desc':desc}
    except Exception as e: 
        print(str(e))
        return {'status':False}
