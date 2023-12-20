from bs4 import BeautifulSoup as soup
from datetime import date
import requests

class scrapertool:
    def __init__(self) -> None:
        self.today = date.today()
        
    def scrape(self):
        news=[]
        d = self.today.strftime("%m-%d-%y")
        # print("date =", d)

        cnn_url="https://retail.economictimes.indiatimes.com/tag/franchise".format(d)
        cnn_url
        html = requests.get(cnn_url)
        bsobj = soup(html.content,'lxml')
        # print(bsobj)
        i=0
        
        # print(news[0])
        # k=1

        for headline in bsobj.findAll('li', attrs={'class':'clearfix article-type-'}):
            # print('News-{}'.format(i))
            news.append([])

            for link in headline.findAll('a'):

                # print('page link:{}'.format(link['href']))
                if link['href'] not in news[i] :
                    news[i].append(link['href'])
                
                # print()
            for img in headline.findAll('img'):
                # print('imgsrc:{}'.format(img['data-src']))
                news[i].append(img['data-src'])
                # print()
            for heading in headline.findAll('h3'):
                # print('Heading-{}'.format(heading.text.strip()))
                news[i].append(heading.text.strip())
                # print()
            for desc in headline.findAll('p'):
                # print('desc.-{}'.format(desc.text.strip()))
                news[i].append(desc.text.strip())
                # print()
            # print ('imgurl:{}'.format(headline["data-src"]))
            # print('headline: {}'.format(headline.text.strip()))
            # print('-------------------------------------------------------------------------------------------------------------------------------')
            i=i+1
        # print('-------------------------------------------------------------------------------------------------------------------------------')
        

        # for data in bsobj.findAll('div',attrs={'class':'all-items'}):
            
        #     for headline in data.findAll('li',attrs={'class':'clearfix article-type-'}):
        #         print('News-{}'.format(i))

        #         # news.append([])
        #         for link in headline.findAll('a'):
        #             print('page link:{}'.format(link['href']))
        #             if link['href'] not in news[0] :
        #                 news[0].append(link['href'])
                    
        #             # print()
        #         for img in headline.findAll('img'):
        #             # print('imgsrc:{}'.format(img['data-src']))
        #             news[1].append(img['data-src'])
        #             # print()
        #         for heading in headline.findAll('h3'):
        #             # print('Heading-{}'.format(heading.text.strip()))
        #             news[2].append(heading.text.strip())
        #             # print()
        #         for desc in headline.findAll('p'):
        #             # print('desc.-{}'.format(desc.text.strip()))
        #             news[3].append(desc.text.strip())
        #             # print()
        #         print('-----------------------------------------------------------------------------------------------------------------------------')
        #         i=i+1
        # print(news)
        return(news)