import mysql.connector
import requests
import urllib
from bs4 import BeautifulSoup
import re
from getpass import getpass
from mysql.connector import connect, Error
import json
import pymsteams
from datetime import datetime
from argparse import ArgumentParser
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb
from os.path import join, dirname, realpath
import time
import shutil
import base64
import yaml
import os
from discord_webhook import DiscordWebhook, DiscordEmbed
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from stem import Signal
from stem.control import Controller
import sys
sys.path.append("..")
import allinone as aio

#working pulling victims of Lockbit

def scrape(ta_url,ta,proxies,timestamp, mydb,writedb,screenshot,workingdir,tbb_dir,imgbb_key,imgbb_url, tor_ff_path, tor_control_pass, ff_binary, ff_profile):
    def new_identity():
      with Controller.from_port(port = 9051) as controller:
          controller.authenticate(password=tor_control_pass)
          controller.signal(Signal.NEWNYM)

#    os.popen(tor_ff_path)

    binary=FirefoxBinary(ff_binary)
    fp=FirefoxProfile(ff_profile)
    fp.set_preference('extensions.torlauncher.start_tor',False)#note this
    fp.set_preference('network.proxy.type',1)
    fp.set_preference('network.proxy.socks', '127.0.0.1')
    fp.set_preference('network.proxy.socks_port', 9050)
    fp.set_preference("network.proxy.socks_remote_dns", True)
    fp.update_preferences()

    ###GET COOKIES FOR LOCKBIT#####
    print("Jacking Cookies for Lockbit - Please wait")
    sel_driver = webdriver.Firefox(firefox_profile=fp,firefox_binary=binary)
    print("URL IS " + ta_url)
    sel_driver.get(ta_url)
    #sel_driver.quit
    #print(driver.page_source)
    cookies = sel_driver.get_cookies()
    str_cookie = str(cookies)
    #print("Full cookie is " + str_cookie)
    cookie = re.findall(r"('value': '[a-zA-Z0-9]+)",str_cookie)
    cookie = str(cookie)
    cookie = cookie.replace('[\"\'value\': \'', '')
    cookie = cookie.replace('\"]','')
    print(cookie)
    cookie_format = "{\"res\": \"" + cookie + "\"}"
    print(cookie_format)
    cookie_format = json.loads(cookie_format)
    sel_driver.quit()
    victim_count = 0
    imgbb_image_url = ""
    mycursor = mydb.cursor()
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    cookies = {'res': 'C7172F6792657FEE8D3E6C199043DD27AC578242895'}
    page = requests.get(ta_url, timeout=30, proxies=proxies, headers=headers, cookies=cookie_format)
    soup = BeautifulSoup(page.content, 'html.parser')
    #working pulling victims of Lockbitv2
    div = soup.find_all("div", class_="post-block-body")
    #pulls links for each victim post - otherwise names are truncated with ...
    for links in div:
        for victim_links in links.find_all("a", href=True):
            victim_links = victim_links['href']
            victim_links = ta_url + victim_links
            print("Pulling Victim from Page" + victim_links)
            vicpage = requests.get(victim_links, timeout=30, proxies=proxies, headers=headers, cookies=cookie_format)
            vicsoup = BeautifulSoup(vicpage.content, 'html.parser')
            vicdiv = vicsoup.find("div", class_="post-big-title")
            victim = vicdiv.text
            victim = victim.strip()
            print(victim)
            date = timestamp
            print("Date is: ")
            print(date)
            victim_count += 1
            dupecheck = "SELECT EXISTS(SELECT * from rw_victims where victim like '" + victim + "')"
            mycursor.execute(dupecheck)
            duperesult = mycursor.fetchall()
            duperesult = str(duperesult)
            if duperesult == "[(1,)]":
                print("DUPLICATE ENTRY --SKIPPING NOTIFICATION")
            else:
                print("New Victim Found!")
                sql = "INSERT IGNORE INTO rw_victims (id, actor, url, victim, date) VALUES (NULL, %s, %s, %s, %s)"
                val = (ta, ta_url, victim, date)
                if writedb == True:
                    mycursor.execute(sql, val)
                    mydb.commit()

                if screenshot == True:
                    time.sleep(3)
                    victim_screenshot = workingdir + "victims/" + victim + ".png"
                    print("Victim Screenshot Location:   " + victim_screenshot)
                    #delete old image if exists
                    if os.path.exists(victim_screenshot):
                        os.remove(victim_screenshot)
                    #print("Grabbing Screenshot of " + victim  + " leak site")
                    out_img = victim_screenshot
                    try:
                        # start a virtual display
                        xvfb_display = start_xvfb()
                        with TorBrowserDriver(tbb_dir) as tbb_driver:
                            tbb_driver.load_url(victim_links)
                            time.sleep(10)
                            height = tbb_driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight )")
                            tbb_driver.set_window_size(900,height+100)
                            tbb_driver.get_screenshot_as_file(out_img)
                            print("Screenshot is saved as %s" % out_img)

                        stop_xvfb(xvfb_display)

                        #EDIT LATER TO GET VICTIM SCREENSHOTS INTO DB#####
                        #sql_insert_blob_query = """ INSERT INTO rw_images (id, timestamp, actor, photo) VALUES (NULL,%s,%s,%s)"""
                        #ta_screenshot_blob = convertToBinaryData(out_img)
                        #insert_blob_tuple = (timestamp, actor, ta_screenshot_blob)
                        #result = mycursor.execute(sql_insert_blob_query, insert_blob_tuple)
                        #mydb.commit()
                        #def get_base64_encoded_image(image_path):
                        #    with open(image_path, "rb") as img_file:
                        #        return base64.b64encode(img_file.read()).decode('utf-8')

                        #data = get_base64_encoded_image(ta_screenshot)
                        #encoded_fig = f"data:image/png;base64,{data}"
                        #print("Image saved to database")
                        screenshot_success = True
                    except:
                        print("Screenshot Failed")
                        screenshot_success = False
                    if screenshot_success == True:
                        imgbb_image_url = aio.upload_screenshot(victim_screenshot,imgbb_url,imgbb_key)
                    aio.notifications(imgbb_image_url,victim,victim_links, victim_screenshot,ta,screenshot_success)
    if victim_count > 0:
        print("Total Victim Count for " + ta + ": " + str(victim_count))
    if victim_count == 0:
        aio.notifications_scraper_broken(ta)
