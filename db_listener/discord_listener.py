import os
import random
import yaml
import discord
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import connect, Error
import json

with open("../config.yaml", "r") as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)


mydb = mysql.connector.connect(
  host=data['database']['host'],
  user=data['database']['user'],
  password=data['database']['password'],
  database=data['database']['database']
)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    search_keyword = 'Searching for Victim: ' 
    mycursor = mydb.cursor() 
    if "!search victim" in message.content:
        victim = message.content 
        victim = victim.replace("!search victim","")
        victim = victim.strip()
        print("Victim to search for is : " + victim)  
        dupecheck = "SELECT actor, victim, SUBSTRING(date,1,11) from rw_victims where victim like '%" + victim + "%'"
        mycursor.execute(dupecheck)
        duperesult = mycursor.fetchall()
        mycursor.close() 
        duperesult_string = str(duperesult)
        payload = []
        content = {}
        print(duperesult) 
        for result in duperesult:
            content = {'Threat Actor': result[0], 'Victim': result[1], 'Date': result[2]} 
            payload.append(content)
            content = {}
            json_result = "Threat Actor: " + result[0] + " Victim: " + result[1] + " Date: " + result[2]
            await message.channel.send(json_result) 
        await message.channel.send('Search Finished') 
        #json_result = json.dumps(payload)
        #for x in payload: 
        #print(json_result)
        #   json_result = x  
        #   print(x)
        #await message.channel.send(json_result) 

        #print(duperesult) 
        json_result = json.dumps(duperesult)
        if duperesult_string == "[]":
            duperesult = '{"Victim": "Not Found in Databse"}'
            print(duperesult)
            await message.channel.send(duperesult) 
        #response = search_keyword + victim
        response = json_result 
        #await message.channel.send(response)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.guild:
        if "!help" in message.content:
            await message.channel.send('To search victims, use \"!search victim <victim name>\"')  

        if "!search victim" in message.content:
            search_keyword = 'Searching for Victim: '
            mycursor = mydb.cursor()
            victim = message.content
            victim = victim.replace("!search victim","")
            print("Victim to search for is : " + victim)
            victim = victim.strip()
            dupecheck = "SELECT actor, victim, SUBSTRING(date,1,11) from rw_victims where victim like '%" + victim + "%'"
            print(dupecheck)
            mycursor.execute(dupecheck)
            duperesult = mycursor.fetchall()
            mycursor.close()
            duperesult_string = str(duperesult)
            payload = []
            content = {}
            print(duperesult)
            for result in duperesult:
                content = {'Threat Actor': result[0], 'Victim': result[1], 'Date': result[2]}
                payload.append(content)
                content = {}
                json_result = "Threat Actor: " + result[0] + " Victim: " + result[1] + " Date: " + result[2]
                await message.channel.send(json_result)

            json_result = json.dumps(duperesult)
            if duperesult_string == "[]":
                duperesult = '{"Victim": "Not Found in Databse"}'
                print(duperesult)
                await message.channel.send(duperesult)
            response = json_result


        #await message.channel.send('this is a dm')
client.run(TOKEN)

