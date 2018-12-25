import time
import requests
import os
import csv
import json

# Import selenium reqs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import re
import traceback
import sys

urls = ['https://www.linkedin.com/pulse/rise-india-one-big-stories-asia-next-20-years-piyush-gupta/',
                'https://www.linkedin.com/pulse/future-banking-piyush-gupta/',
                'https://www.linkedin.com/pulse/belt-road-initiative-implications-asia-singapore-piyush-gupta/',
                'https://www.linkedin.com/pulse/what-trump-led-us-augurs-asia-markets-year-piyush-gupta/',
                'https://www.linkedin.com/pulse/why-im-keeping-faith-china-piyush-gupta/',
        ]


class LinkedInArticle:
    '''
    Initialize necessary variables
    This one works for the non-public profiles
    Requires login
    '''
    def __init__(self, url):
        # options = webdriver.ChromeOptions()
        # Replace the dir with the profile of your google chrome
        # To do this, goto google-chrome, and type: chrome://version, and get the profile path
        # Also make sure to clear all caches before starting
        # options.add_argument('user-data-dir=/home/dipes/.config/google-chrome/Profile')
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.email = ''
        self.password = ''
        self.url = url


    def login(self):
        driver = self.driver
        url = 'https://www.linkedin.com/'
        try:
            driver.get(url)
            emailFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id('login-email') )
            passwordFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id('login-password')) 
            loginbutton = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id('login-submit'))
        except Exception as e:
            print(e)
            print('Error in elements for login...')
        else:
            emailFieldElement.send_keys(self.email)
            time.sleep(2)
            passwordFieldElement.send_keys(self.password)
            time.sleep(2)
            loginbutton.click()
            print('Logging in...')
            time.sleep(3)


    def scrollToBottom(self):
        # Time to pause for the page to load
        SCROLL_PAUSE_TIME = 2

        driver = self.driver
        # Get scroll height
        last_height = driver.execute_script("return document.body.scrollHeight;")

        while True:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight;")
            if new_height == last_height:
                break
            last_height = new_height


    def getContent(self):
        driver = self.driver

        driver.get(self.url)
        driver = self.driver
        content = driver.find_element_by_class_name('reader-article-content').text
        print(content)
        return content

    
    def getComments(self):
        driver = self.driver
        
        time.sleep(3)

        body = driver.find_element_by_tag_name('body')
        comments = []
        while True:
            print("Scrolling..")
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)
            if len(driver.find_elements_by_xpath(".//button[@data-control-name='more_comments']")) > 0:
                print("Yes..")
                comment_button = WebDriverWait(driver,5).until(lambda driver:driver.find_element_by_xpath(".//button[@data-control-name='more_comments']"))
                # print(comment_button)
                action_comments = ActionChains(driver)
                action_comments.move_to_element(comment_button).click(comment_button).perform()
                time.sleep(5)
                body.send_keys(Keys.PAGE_DOWN)
                break

        comments_div = driver.find_element_by_class_name("feed-base-comments-list")
        # print(comments_div.text)
        comments_divs = comments_div.find_elements_by_xpath(".//article")
        print(len(comments_divs))
        time.sleep(3)
        for div in comments_divs:
            if len(div.find_elements_by_xpath(".//p[@dir='ltr']")) > 0:
                comment_element = div.find_element_by_xpath(".//p[@dir='ltr']")
                comment_text = comment_element.text
                print(comment_text)
                commenter_url_element = div.find_element_by_xpath(".//a[@data-control-name='comment_actor']")
                commenter_url = commenter_url_element.get_attribute("href")
                commenter = commenter_url_element.text
                
            i_comment = {'commenter': commenter, 'commenter_url': commenter_url, 'comment_text': comment_text}
            comments.append(i_comment)

        print("\n")
        print(len(comments))
        return comments



    def getLikes(self):
        driver = self.driver
        
        # for i in urls:
        time.sleep(3)

        body = driver.find_element_by_tag_name('body')
        comments = []
        
        while True:
            print("Scrolling..")
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)
            if len(driver.find_elements_by_xpath("//button[@data-control-name='likes']")) > 0:
                print("Yes..")
                likes_element = driver.find_element_by_xpath("//button[@data-control-name='likes']")
                action_likes = ActionChains(driver)
                action_likes.move_to_element(likes_element).click(likes_element).perform()
                time.sleep(1.5)
                break

        # Wait until the modal is opened
        try:
            modal_element = WebDriverWait(driver, 10).until(
                                                        EC.presence_of_element_located((By.ID, "artdeco-modal-outlet")))

            likes = []
            # Scroll to bottom
            last_height = driver.execute_script("return arguments[0].scrollHeight", modal_element.find_element_by_tag_name("ul"))
            while True:
                # Scroll down to bottom
                scrollHelght = driver.execute_script("arguments[0].scrollTop = " + str(last_height), modal_element.find_element_by_tag_name("ul"))
                time.sleep(1.5)
                # Calculate new scroll height and compare with last scroll height
                new_height = driver.execute_script("return arguments[0].scrollHeight", modal_element.find_element_by_tag_name("ul"))
                if new_height == last_height:
                    break
                    print("Reached the end of list ...")
                last_height = new_height
                print("Scrolling down ...")
            modal_content = modal_element.find_element_by_tag_name("ul")
            actor_elements = modal_element.find_elements_by_tag_name("li")
            # Taking too long for large no. of likes
            for actor_element in actor_elements:
                actor_element = actor_element.find_element_by_tag_name("a")
                url = actor_element.get_attribute('href')
                name = actor_element.find_element_by_class_name("name").text
                headline = actor_element.find_element_by_class_name("headline").text
                likes.append({'url':url, 'name': name, 'headline':headline})
            print("All likes extracted..\n")
            close_button = driver.find_element_by_class_name('artdeco-dismiss')
            action_close = ActionChains(driver)
            action_close.move_to_element(close_button).click(close_button).perform()
            time.sleep(1.5)
            
            print(likes)


        except Exception as e:
            print(e)
            return []

        else:
            return likes
            


    def getShares(self):
        driver = self.driver

        try:
            shares = driver.find_element_by_xpath("//ul[@class='reader-social-bar__items']/li[2]/span").text
        except Exception as e:
            print(e)
            return 'No shares found ...'
        else:            
            print(shares)
            return shares



    def quitDriver(self):
        driver = self.driver
        driver.quit()


article = LinkedInArticle(url=url[2])
article.login()
article.getContent()
article.getLikes()
article.getShares()
article.getComments()






 # with open('articles_comments.csv', 'w') as csvfile:
 #    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
 #    writer.writerow(['commenter', 'comment_url', 'comment_text'])
 #    for i in comments:
 #        for j in comments[i]:
 #            writer.writerow([j['commenter'], j['commenter_url'], j['comment_text']])





# with open('articles_shares.csv','w') as csvfile:
#     writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
#     writer.writerow(['article_url', 'n_shares'])
#     for i in shares:
#          writer.writerow([i, shares[i]])
