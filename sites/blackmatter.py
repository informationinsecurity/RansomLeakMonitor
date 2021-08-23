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
import sys
sys.path.append("..")
import allinone as aio


def scrape(ta_url,ta,proxies,timestamp, mydb,writedb,screenshot,workingdir,tbb_dir,imgbb_key,imgbb_url):
    imgbb_image_url = ""
    mycursor = mydb.cursor()
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'} 
    page = requests.get(ta_url, timeout=30, proxies=proxies, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    #working pulling victims of blackmatter
    div = soup.find_all("div", class_="col-6 pl-1")
    #pulls links for each victim post - otherwise names are truncated with ...
    for links in div:
        for victim_links in links.find_all("a", href=True):
            victim_links = victim_links['href']
            victim_links = ta_url + victim_links
            print("Pulling Victim from Page" + victim_links)
            vicpage = requests.get(victim_links, timeout=30, proxies=proxies, headers=headers)
            vicsoup = BeautifulSoup(vicpage.content, 'html.parser')
            vicdiv = vicsoup.find("div", class_="text-center pt-4")
            victim = vicdiv.text
            print(victim)
            date = timestamp
            print("Date is: ")
            print(date)
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
                        with TorBrowserDriver(tbb_dir) as driver:
                            driver.load_url(victim_links)
                            time.sleep(3)
                            height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight )")
                            driver.set_window_size(900,height+100)
                            driver.get_screenshot_as_file(out_img)
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
