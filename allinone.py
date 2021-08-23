import requests
import urllib
from bs4 import BeautifulSoup
import re
from getpass import getpass
import json
import pymsteams
from datetime import datetime
from argparse import ArgumentParser
import time
import yaml
from discord_webhook import DiscordWebhook, DiscordEmbed
import mysql.connector
from mysql.connector import connect, Error
import os
from tbselenium.tbdriver import TorBrowserDriver
from tbselenium.utils import start_xvfb, stop_xvfb
import base64
#import sites.avoslocker as avoslocker

with open("config.yaml", "r") as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)

#Post to Teams true or false
teamsnotify = data['notifications']['teamsnotify']

#Post to Discord if true
discordnotify = data['notifications']['discordnotify']

#Teams and Discord Webhook definitions
teams_webhook = data['webhooks']['teams']
discord_webhook = data['webhooks']['discord']

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

mydb = mysql.connector.connect(
  host=data['database']['host'],
  user=data['database']['user'],
  password=data['database']['password'],
  database=data['database']['database']
)

#take screenshot
screenshot = data['screenshot']

#IMGBB API KEY TO UPLOAD SCREENSHOTS
imgbb_key = data['imgbb_key']
imgbb_url = data['imgbb_url']

mycursor = mydb.cursor()
threatactors = data['ta_urls']

#Path to Torbrowser (for screenshot)
tbb_dir = data['torbrowser']['tbbdir']

#Working Directory for script
workingdir = data['working_dir'] 

#used to get timestamps for db entries
timestamp = datetime.now()

#write to database true or false
writedb = data['database']['writedb']


isup = ''
##################END VARIABLES#############################

#checks status of TA site to make sure it's online
def check_status(ta_url,ta):
    isup = "" 
    print("Checking  " + ta + " site status: ")
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
    try:
        page = requests.get(ta_url, timeout=30, proxies=proxies, headers=headers)
        print(ta + " site is online!")
        isup = True
    except:
        #  last_seen = "SELECT last_seen from rw_status where actor like '" + ta + "' order by id desc limit 1"
        isup = False
        #  mycursor.execute(last_seen)
        # last_seen = mycursor.fetchone()
        print(ta + " site is offline!")
        # last_seen = last_seen[0]
        # print(ta + " leak site last seen " + last_seen)
    return isup 

#converts screen shot to b64 for database
def get_base64_encoded_image(image_path):
  with open(image_path, "rb") as img_file:
      return base64.b64encode(img_file.read()).decode('utf-8')

#converts png to binary data for notifications
def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

#uploads screenshot and returns an imgbb link (for teams notifications)
def upload_screenshot(ta_screenshot,imgbb_url,imgbb_key):
  print("Uploading Image to ImageBB")
  with open(ta_screenshot, "rb") as file:
      payload = {
          "key": imgbb_key,
          "image": base64.b64encode(file.read()),
      }
  res = requests.post(imgbb_url, payload, proxies=proxies)
  json_response = res.json()
  imgbb_image_url = json_response['data']['url']
  return imgbb_image_url

 
def notifications(imgbb_image_url,victim,victim_links,victim_screenshot,ta,screenshot_success):
    #If teamsnotify set to true - post data to teams
    if teamsnotify == True:
        print("Sending Teams Notification")
        myTeamsMessage = pymsteams.connectorcard(teams_webhook)
        myMessageSection = pymsteams.cardsection()
        myMessageSection.title(victim)
        myMessageSection.activityTitle('Threat Group: ' + ta)
        myMessageSection.activityText('Victim Link: ' + victim_links)
        if screenshot_success == True: 
            myMessageSection.addImage(imgbb_image_url, ititle="TA_Screenshot")
            myTeamsMessage.addLinkButton("View Screenshot", imgbb_image_url)
        myTeamsMessage.addSection(myMessageSection)
        myTeamsMessage.text('New Victim Found!')
        myTeamsMessage.send()

    #If discordnotify set to true - post data to discord_webhook
    if discordnotify == True:
        print("Sending Discord Notifications") 
        discord_notify = DiscordWebhook(url=discord_webhook, username="Hermes")
        embed = DiscordEmbed(title='New Victim Posted', color='238076')
        embed.set_timestamp()
        embed.add_embed_field(name='Actor', value=ta, inline=False)
        embed.add_embed_field(name='Victim', value=victim, inline=False)
        embed.add_embed_field(name='Victim Link: ', value=victim_links)
        discordpicturename = victim + ".png"
        if screenshot_success == True:
            with open(victim_screenshot, "rb") as f:
                discord_notify.add_file(file=f.read(), filename=discordpicturename)
        discord_notify.add_embed(embed)
        response = discord_notify.execute() 

#captures screenshot for given ta_url
def screenshot_site(ta_url,ta):
  print("Grabbing Screenshot of " + ta + "leak site")
  print(ta_url) 
  #print(tbb_dir) 
  out_img = workingdir + "screenshots/" + ta + ".png" 
  
  try:
      # start a virtual display
      xvfb_display = start_xvfb()
      with TorBrowserDriver(tbb_dir) as driver:
          driver.load_url(ta_url)
          time.sleep(3)
          height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight )")
          driver.set_window_size(900,height+100)
          driver.get_screenshot_as_file(out_img)
          print("Screenshot is saved as %s" % out_img)

      stop_xvfb(xvfb_display)
      print("Screenshot Successful")
      screenshot_success = True
  except:
      print("Screenshot Failed")
      screenshot_success = False
  print(screenshot_success)

  #If Screenshot worked, save a copy in the db
  if screenshot_success == True:
      print("Attempting to update screenshot database") 
      data = get_base64_encoded_image(out_img)
      encoded_fig = f"data:image/png;base64,{data}"
      sql_insert_blob_query = """ INSERT INTO rw_images (id, timestamp, actor, photo) VALUES (NULL,%s,%s,%s)"""
      ta_screenshot_blob = convertToBinaryData(out_img)
      insert_blob_tuple = (timestamp, ta, ta_screenshot_blob)
      try: 
          result = mycursor.execute(sql_insert_blob_query, insert_blob_tuple)
          mydb.commit()
          print("Screenshot for " + ta + " added to databse")
      except:
          print("screenshot for " + ta + " failed!") 

#update the last_seen database for each TA
def update_lastseen(ta,timestamp):
  print("Updating Last Seen Time")
  last_seen = timestamp
  sql_update_seen = "INSERT INTO rw_status (id, actor, last_seen) VALUES (NULL, %s, %s)"
  seen_val = (ta, last_seen)
  try: 
      mycursor.execute(sql_update_seen, seen_val)
      mydb.commit()
      print("Last Seen Time for " + ta + " Updated Successfully")
  except:
      print("Unable to update Last Seen time in DB!")

def main():
    for ta in threatactors:  
        #sets module to proper TA for scraping 
        import importlib
        threatactor = "sites." + ta
        threatactor = importlib.import_module(threatactor) 
        ta_url = data['ta_urls'][ta]  
        isup = check_status(ta_url,ta)
        if isup == True: 
            screenshot_site(ta_url,ta)                                                                                                          
            update_lastseen(ta,timestamp)
            try: 
                threatactor.scrape(ta_url,ta,proxies,timestamp,mydb,writedb,screenshot,workingdir,tbb_dir,imgbb_key,imgbb_url)
            except:
                print("Scrapting of " + ta + " has failed!")
if __name__== "__main__":
  main()
