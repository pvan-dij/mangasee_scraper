import sys
import re
import os
import tqdm
import urllib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup



def verify_args():
	# verify arg number
	if (len(sys.argv) != 2):
		sys.exit('Mangasee_scraper: Wrong number of args')

	# verify link is a mangasee manga link
	link = sys.argv[1]
	if not re.search('https:\/\/mangasee123\.com\/manga\/.*', link):
		sys.exit('Mangasee_scraper: Not a valid link')
	

def scrape(url):

	#selenium driver options
	options = Options()
	options.headless = True
	options.add_argument("--window-size=1920,1200")
	options.add_argument('--blink-settings=loadsImagesAutomatically=false')

	#start selenium webdriver and get the mangasee page
	driver = webdriver.Chrome(options=options)
	driver.get(url)

	# dots act as replacement for spaces 
	try:
		element = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.CLASS_NAME,"list-group-item.ShowAllChapters.ng-scope"))
		element.click() #click the show all pages button to get all the chapters
	except:
		pass

	element = driver.find_element(By.CLASS_NAME,"list-group.top-10.bottom-5.ng-scope") #contains all the chapter links
	content = BeautifulSoup(element.get_attribute('innerHTML'),'html.parser') #get html of all chapters
	links = [a.get('href') for a in content.find_all('a', href=True)]  #all links
	links = ["https://mangasee123.com" + l.replace("-page-1","") for l in links] #modify the links to get all imgs on one page

	manga_title = url[url.rfind("/") + 1:]
	os.mkdir(manga_title)


	count = 1 #TODO: base this of the actual chapter numbers
	for link in links:

		driver.get(link)
		#xpath of where the image files are, wait until this path exists to see if theyve been loaded
		WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.XPATH,"//div/div/img")) 

		#get all the raw image links
		elems = driver.find_elements(By.XPATH, "//div[@class='ImageGallery']/div/div/img[@ng-src]")
		img_links = []
		for e in elems:
			html = e.get_attribute('outerHTML')
			img_links.append(html[html.find(" src=") + 6:-2])
		
		#add user-agent header for bot detection prevention
		opener = urllib.request.build_opener()
		opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		urllib.request.install_opener(opener)

		#download all the images
		for e in tqdm.tqdm(img_links, desc=f"Downloading images of chapter {count}"):
			urllib.request.urlretrieve(e, manga_title+e[e.rfind("/"):])
		count += 1
	print("All chapters downloaded")		

	driver.close()

  
def main():
	verify_args()
	print("Mangasee_scraper: Valid args, starting process...")
	url = sys.argv[1]
	scrape(url)
	
  
if __name__=="__main__":
	main()