import os
import sys
import wget
import ntpath
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from operator import itemgetter
from bs4 import BeautifulSoup
from anki import Collection as aopen
 
 
coll_path   = os.path.abspath("C:\\Users\\bzwol_000\\Documents\\Anki\\User 1\\collection.anki2")
img_dir = "C:/tempImg"
userName = '@.edu'
password = ''

def make_cards(card_front, card_back, img, rx_tags):
    fpath = img.decode('utf-8')
    fname = ntpath.basename(fpath).decode('utf-8')
    a_coll = aopen(coll_path)
    a_coll.media.addFile(fpath)
    card_type = 'Basic'
    deck_name = 'USMLErx'
    deck_id = a_coll.decks.id(deck_name)
    a_coll.decks.select(deck_id)
    model = a_coll.models.byName(card_type)
    model['did'] = deck_id
    a_coll.models.save(model)
    a_coll.models.setCurrent(model)
    card            = a_coll.newNote()
    card['Front']   = card_front.decode('utf-8')
    card['Back']    = card_back.decode('utf-8')
    card['Back Image'] = u'<img src="%s">' % fname
    card.tags       = rx_tags
    a_coll.addNote(card)
    a_coll.save()
    a_coll.close()
 
 
#open browser , load page, login
driver = webdriver.Firefox() #opens browser
wait = WebDriverWait(driver, 10)
driver.get("http://usmle-rx.com/dashboard")
user = driver.find_element_by_xpath('//*[(@id = "edit-name-wrapper")]//*[(@id = "edit-name")]')
pass2 = driver.find_element_by_xpath('//*[(@id = "edit-pass-wrapper")]//*[(@id = "edit-pass")]')
user.send_keys(userName)
pass2.send_keys(password)
loginform = driver.find_element_by_xpath('//*[(@id = "content-inner-main")]//*[(@id = "edit-submit")]')
loginform.submit()
 
element = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="content-inner-main"]/table[2]/tbody/tr[1]/td[1]/a')))
#click the image and load the flashfact ui
ff = driver.find_element_by_xpath('//*[@id="content-inner-main"]/table[2]/tbody/tr[1]/td[1]/a')
ff.click()
 
driver.implicitly_wait(60)

#load the TOC for the cards
driver.find_element_by_xpath('//*[@id="lnkBrowseFirstAid"]').click()
driver.implicitly_wait(60)
#iterate this muthafucka
sectionList = driver.find_elements_by_class_name('spnSectionName')
for section in sectionList:
	section.click()
	subsection = driver.find_elements_by_css_selector('.spnSubsectionName')
	for sub in subsection:
		if sub.is_displayed():
			sub.click() 
			topics = driver.find_elements_by_css_selector('li.liTopic') 
			for topic in topics:
				if topic.is_displayed():
					topic.click()
					driver.implicitly_wait(30) #make sure there is time for the image to load
					img = driver.find_element_by_id('imgFFImg')
					url = img.get_attribute('src')
					file = wget.download(url,img_dir)
					driver.implicitly_wait(20)
					driver.find_element_by_id('spnViewCards').click()
					driver.implicitly_wait(20)#make sure there is time for the card table to load
					qa = driver.find_elements_by_css_selector('#ulFactCardList')[0].text
					qaT=qa.split('\n')
					qaTup = zip(qaT[0::2],qaT[1::2]) 
 					tags=[] 
					tags.append(section.text.lower().strip().decode('utf-8'))
					tags.append(sub.text.lower().strip().decode('utf-8'))
					tags.append(topic.text.lower().strip().decode('utf-8'))
					#Add loop to iterate qaTup here or pass the whole thing
					### we differ in opinion here, and more importantly i have no way of testing the code, thus this is all you...
					for qa in qaTup:
						make_cards(qa[0], qa[1], file, tags)
					
					driver.implicitly_wait(20)
					topic.click() # need to click back to topic image to be able to load the next one, breaks otherwise.
					driver.implicitly_wait(20)
			sub.click()
			driver.implicitly_wait(30)
		else:
			sub.clear()
	section.click()
	driver.implicitly_wait(10)

