from flask import Flask, request, jsonify, render_template
from OpenSSL import SSL
import os
import json
from flask_mysqldb import MySQL
import yaml

with open("../config.yaml", "r") as yamlfile:
    data = yaml.load(yamlfile, Loader=yaml.FullLoader)

#Post to Teams true or false
teamsnotify = data['notifications']['teamsnotify']
app = Flask(__name__)
app.config['MYSQL_HOST'] = data['database']['host'] 
app.config['MYSQL_USER'] = data['database']['user']
app.config['MYSQL_PASSWORD'] = data['database']['password'] 
app.config['MYSQL_DB'] = data['database']['database'] 
 
mysql = MySQL(app)



@app.route('/', methods=['POST','GET'])
def index():
        if request.method == 'GET':
            return '<h1>Hello from Webhook Listener!</h1>'
        if request.method == 'POST':
            cursor = mysql.connection.cursor()
            req_data = request.get_json()
            str_obj = json.dumps(req_data)
            print(str_obj)
            if "victim" in str_obj:
                print("Querying for Victim")
                vic_name = json.loads(str_obj)
                victim = vic_name['victim']
                victim = victim.strip()
                victim = ''.join(e for e in victim if e.isalnum())
                if victim == "":
                    return "PLEASE ENTER A SEARCH TERM"
                print("Victim you are searching for is: " + victim)
                dupecheck = "SELECT actor, victim, SUBSTRING(date,1,11) from rw_victims where victim like '%" + victim + "%'"
                #print(dupecheck)
                cursor.execute(dupecheck)
                duperesult = cursor.fetchall()
                cursor.close() 
                duperesult_string = str(duperesult)
                print(duperesult)
                payload = []
                content = {}
                for result in duperesult:
                    content = {'Threat Actor  ': result[0], 'Victim  ': result[1], 'Date': result[2]}
                    payload.append(content)
                    content = {}
                json_result = jsonify(payload)

                if duperesult_string == "()":
                    #print("VICTIM DOES NOT EXIST!")
                    duperesult = '{"Victim": "Not Found in Databse"}'
                    json_result = jsonify(duperesult)
                    print(json_result)
                    return json_result
                    #return '{"victim_found":"false"}'
                else:
                    print("Victim Found!")
                    # return '{"victim_found": duperesult}'
                    print(json_result)
                    return json_result
            if "stats" in str_obj:
                print("Grabbing TA Stats")
                getstats = "SELECT actor, count(*) AS 'Victim Count', min(SUBSTRING(date,1,11)) as 'Oldest Victim Date', max(SUBSTRING(date,1,11)) as 'Newest Victim Date' FROM `rw_victims` WHERE 1 GROUP BY actor order by count(*) DESC"
                cursor.execute(getstats)
                getstats = cursor.fetchall()
                cursor.close() 
                payload = []
                content = {}
                for result in getstats:
                    content = {'Threat Actor': result[0], 'Victim Count ': result[1], 'Oldest Victim Date': result[2], 'Newest Victim Date': result[3]}
                    payload.append(content)
                    content = {}
                json_result = jsonify(payload)
                print(json_result)
                return json_result

            if "scraper" in str_obj:
                print("Grabbing Scraper Stats")
                getstats = "SELECT actor, max(SUBSTRING(last_seen,1,11)) as 'Latest Successful Scrape' FROM `rw_status` WHERE 1 GROUP BY actor order by actor asc"
                cursor.execute(getstats)
                getstats = cursor.fetchall()
                cursor.close() 
                payload = []
                content = {}
                for result in getstats:
                    content = {'Threat Actor': result[0], 'Last Successful Scrape': result[1]}
                    payload.append(content)
                    content = {}
                json_result = jsonify(payload)
                print(json_result)
                return json_result

if __name__ == "__main__":
    #context = ('ssl.cert', 'ssl.key') # certificate and key file. Cannot be self signed certs
    #app.run(host='0.0.0.0', port=5000, ssl_context=context, threaded=True, debug=True) # will listen on port 5000
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True) # will listen on port 5000
