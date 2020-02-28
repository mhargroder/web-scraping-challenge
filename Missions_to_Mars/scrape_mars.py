#Dependencies
from bs4 import BeautifulSoup as bs
import requests
from splinter import Browser
from selenium import webdriver
import pandas as pd
import pymongo

def init_browser():

    executable_path = {'executable_path':r'C:\Users\mharg\chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=True)


def scrape():

	browser = init_browser()

	# recent mars news from NASA
	url = 'https://mars.nasa.gov/news/'
	browser.visit(url)
	html = browser.html
	soup = bs(html, 'lxml')
	news_title = soup.find('div', class_= 'content_title').text
	news_content = soup.find('div', class_= 'article_teaser_body')

	#featured image from JPL
	url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
	response = requests.get(url)
	soup = bs(response.text, 'lxml')
	image_substr =soup.find('a', class_ = 'button fancybox')['data-fancybox-href']
	jpl_image = 'https://www.jpl.nasa.gov/'+image_substr


	#mars weather
	url = 'https://twitter.com/marswxreport?lang=en'
	response = requests.get(url)
	soup = bs(response.text, 'lxml')
	mars_weather = soup.find('p', class_='TweetTextSize').text

	# mars fact table
	url = 'https://space-facts.com/mars/'
	df = pd.read_html(url)[0]
	df.columns = ['Measure', 'Value']
	df.set_index('Measure', inplace = True)
	fact_table = df.to_html()
	fact_table.replace('\n', '')

	#mars hemispheres
	url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
	browser.visit(url)
	html = browser.html
	soup = bs(html, 'lxml')
	items = soup.find_all('div', class_='item')

	base_url = 'https://astrogeology.usgs.gov'
	mars_hemis = []
		
	for i in items:
	    title = i.find('h3').text
	    partial_img = i.find('a', class_='itemLink product-item')['href']
	    browser.visit(base_url + partial_img)
	    partial_img = browser.html
	    soup = bs( partial_img, 'lxml')
	    #larger images
	    img_url = base_url + soup.find('img', class_='wide-image')['src']
	    mars_hemis.append({'title' : title, 'img_url' : img_url})



	# add scraped vars to a dictionary
	s_dict = {}
	s_dict['news_title'] = news_title 
	s_dict['news_content'] = news_content
	s_dict['jpl_image'] = jpl_image
	s_dict['mars_weather'] = mars_weather
	s_dict['fact_table'] = fact_table
	s_dict['mars_hemis'] =  mars_hemis

	# create connection to mongo db
	client = pymongo.MongoClient('mongodb://localhost:27017/')
	db = client.planets_db
	db.mars.drop()

	#insert record to mongo db
	db.mars.insert_one(s_dict)

