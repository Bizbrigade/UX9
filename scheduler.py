from newsscraper import scrapertool
import numpy as np
import pandas as pd
import schedule
import time

def job():
    a=scrapertool()
    news=a.scrape()
    # print(len(news[0]))
    # print(len(news[1]))
    # print(len(news[2]))
    # print(len(news[3]))


    # print(news)
    news=np.array(news)

    # print(news)
    df=pd.DataFrame(news, columns=['link','img','head','desc'])
    # print(df)
    df.to_csv('news.csv')
    # testarray=df.to_numpy()
    # print(testarray[0])
schedule.every(20).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

