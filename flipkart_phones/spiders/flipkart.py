import scrapy
import time
from scrapy import Request
import logging
import json
from bs4 import BeautifulSoup
from lxml import etree
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml.etree import tostring



class FlipkartSpider(scrapy.Spider):
    name = 'flipkart'
    allowed_domains = ['*']
    DRIVER_PATH = r"E:\ChromeDriver\chromedriver.exe"
    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
    start_urls = ['https://www.flipkart.com/mobiles/pr?sid=tyy,4io&otracker=categorytree']
    

    def start_requests(self):
        for url in self.start_urls[:1]:
            self.driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            #create xml tree to use xpath
            dom = etree.HTML(str(soup))
            links = dom.xpath('//*[@class="_1fQZEK"]//@href')
            for link in links[0:1]:
                link = "https://www.flipkart.com" + link
                yield Request(link, callback=self.parse, dont_filter=True)


    def parse(self, response):
        self.driver.get(response.url)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        dom = etree.HTML(str(soup))
        
        title = dom.xpath('//*[@class="B_NuCI"]//text()')
        self.product = title
        
        price = dom.xpath('//*[@class="_30jeq3 _16Jk6d"]//text()')
        des = dom.xpath('//*[@class="_1mXcCf RmoJUa"]//text()')
        specs_title = dom.xpath('//*[@class="_1hKmbr col col-3-12"]//text()')
        specs = dom.xpath('//*[@class="_21lJbe"]//text()')
        specifications =  list(zip(specs_title,specs))

        dic = {str(title):{'price':price,'description':des,'specifications':specifications}}
        with open('products.json','w') as fl:
            json.dump(dic,fl)
            fl.write('\n')

        reviews_link = dom.xpath('//*[@class="_3UAT2v _16PBlm"]/parent::a/@href')
        reviews_link = "https://www.flipkart.com" + reviews_link[0]

        yield Request(reviews_link, callback=self.parse_reviews, dont_filter=True)
    
    
    def parse_reviews(self, response):
        print(response.url)
        text = response.xpath('//*[@class="t-ZTKy"]/div/div').extract()
        


        ratings = response.xpath('//*[@class="_3LWZlK _1BLPMq"]//text()|//*[@class="_3LWZlK _1rdVr6 _1BLPMq"]//text()').extract()

        reviewTitle = response.xpath('//*[@class="_2-N8zT"]//text()').extract()

        date = response.xpath('//*[@class="_2sc7ZR"]//text()').extract()
        

        a = list(zip(reviewTitle,ratings,date,text))

        dic = {self.product[0]:str(a)}

        with open('reviews.json','a') as fl:
            json.dump(dic,fl)
            fl.write('\n')
        nxt = response.xpath('//*[@class="_2MImiq _1Qnn1K"]//*[contains(text(),"Next")]/parent::a/@href').extract()
        if len(nxt) !=0:
            nxt_link = "https://www.flipkart.com" + nxt[0]
            yield Request(nxt_link, callback=self.parse_reviews, dont_filter=True)