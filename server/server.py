from flask import Flask, jsonify, request
from flask_cors import CORS
from mcrcon import MCRcon
import logging
import threading
import os
import requests


# configuration
DEBUG = False
serverip = None
serversecret = None

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARN if os.getenv('MCSERVER_DEBG', '') == '' else logging.DEBUG)
rconlock = threading.Lock()

def rconRequest(req):
    global rconlock

    log.debug(req)
    if serverip is None or serversecret is None:
        return('-1')
    with rconlock:
        try:
            with MCRcon(serverip, serversecret) as mcr:
                resp = mcr.command(req)
        except:
            return('-1')
        return(resp)

@app.route('/api/connect', methods=['GET'])
def setConnectionParms():
    global serverip
    global serversecret
    serverip = request.args.get('serverip', serverip)
    serversecret = request.args.get('serversecret', serversecret)
    check = rconRequest('time query daytime')
    return(jsonify(serverip=serverip, serversecret=serversecret, connected=(check != '-1')))

@app.route('/api/gamerule', methods=['GET'])
def gamerule():
    rule = request.args.get('rule', None)
    value = request.args.get('value', None)
    if value is None:
        resp = rconRequest('gamerule ' + rule)
    else:
        resp = rconRequest('gamerule ' + rule + ' ' + value)
    if resp != '-1':
        words = resp.split(' ')
        if words[0] == 'Incorrect':
            log.warn(words)
            value = 'ERROR'
        else:
            value = words[-1]
    return(jsonify(rule=rule, value=value, connected=(resp != '-1')))

@app.route('/api/serverdefault', methods=['GET'])
def serverdefault():
    return(jsonify(serverdefault=os.getenv('MCSERVER_ADDR', ''), secretdefault=os.getenv('MCSERVER_SECR', '')))

@app.route('/api/time', methods=['GET'])
def mctime():
    resp = rconRequest("time query daytime")
    return(jsonify(daytime=int(resp.split(' ')[-1])))

@app.route('/api/daytime', methods=['POST'])
def mcdaytime():
    resp = rconRequest("time set " + request.json['cmd'])
    return (jsonify(msg=resp))

@app.route('/api/weather', methods=['POST'])
def mcweather():
    resp = rconRequest("weather " + request.json['cmd'])
    return (jsonify(msg=resp))

@app.route('/api/days', methods=['GET'])
def gamedays():
    resp = rconRequest("time query day")
    return(jsonify(days=int(resp.split(' ')[-1])))

@app.route('/api/serverup', methods=['GET'])
def serverup():
    resp = rconRequest("time query gametime")
    return(jsonify(ticks=int(resp.split(' ')[-1])))

@app.route('/api/motd', methods=['POST'])
def motd():
    if request.content_length > 0 and request.content_length < 100:
        rconRequest('say ' + request.get_data(as_text=True))
    return '{}'

@app.route('/api/players', methods=['GET'])
def players():
    resp = rconRequest("list uuids")
    pls = []
    if resp != '-1':
        words = resp.split(' ')
        counts = list(filter(lambda w : len(w) > 0 and w[0] >='0' and w[0] <= '9', words))
        nPlayers = int(counts[0])
        maxPlayers = int(counts[1])
        if nPlayers > 0:
            offset = 0
            for index, item in enumerate(words):
                if item[-1] == ':':
                    offset = index+1
            for i in range(nPlayers):
                pl = { "name": words[offset+i*2], "uuid": words[offset+1+i*2].split(',')[0]}
                pls.append(pl)
    else:
        nPlayers = 0
        maxPlayers = 0
    return(jsonify(nplayers=nPlayers, maxplayers=maxPlayers, players=pls))

@app.route('/api/whitelist', methods=['GET'])
def whitelist():
    resp = rconRequest("whitelist list")
    pls = []
    nPlayers = 0
    if resp != '-1':
        words = resp.replace(',', '').split(' ')
        if words[2] != 'no':
            nPlayers = int(words[2])
            for i in range(nPlayers):
                pl = { "name": words[i+5] }
                pls.append(pl)
    return(jsonify(nplayers=nPlayers, players=pls))

@app.route('/api/whitelistonoff', methods=['GET'])
def whitelistonoff():
    value = request.args.get('value', None)
    if value is None:
# In this case we just return status, using a little trick
        resp = rconRequest('whitelist off')
        if resp != '-1': 
            on_before = resp.split(' ')[2] != 'already'
            if on_before:
                resp = rconRequest('whitelist on')
            value = 'true' if on_before else 'false'
    else:
        resp = rconRequest('whitelist ' + ('on' if value == 'true' else 'off'))
    return(jsonify(msg=resp, value=value))

@app.route('/api/addwhitelist', methods=['POST'])
def addwhilelist():
    resp = requests.get('https://api.mojang.com/users/profiles/minecraft/' + request.json['name'])
    if resp.status_code != 200:
        return ('', 204)
    resp = rconRequest("whitelist add " + request.json['name'])
    return (jsonify(msg=resp))

@app.route('/api/delwhitelist', methods=['POST'])
def delwhilelist():
    resp = rconRequest("whitelist remove " + ' '.join(request.json['names']))
    return (jsonify(msg=resp))


if __name__ == '__main__':
    app.run()
