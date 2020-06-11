from flask import Flask, jsonify, request
from flask_cors import CORS
from mcrcon import MCRcon
import logging
import threading
import os


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
log.setLevel(logging.WARN)
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
    return '{}'

@app.route('/api/weather', methods=['POST'])
def mcweather():
    resp = rconRequest("time set " + request.json['cmd'])
    return '{}'

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
        nPlayers = int(words[2])
        maxPlayers = int(words[6])
        for i in range(nPlayers):
            pl = { "name": words[9+i*2], "uuid": words[10+i*2].split(',')[0]}
            pls.append(pl)
    else:
        nPlayers = 0
        maxPlayers = 0
    return(jsonify(nplayers=nPlayers, maxplayers=maxPlayers, players=pls))

@app.route('/api/whitelist', methods=['GET'])
def whitelist():
    resp = rconRequest("whitelist list")
    pls = []
    if resp != '-1':
        words = resp.replace(',', '').split(' ')
        nPlayers = int(words[2])
        for i in range(nPlayers):
            pl = { "name": words[i+5] }
            pls.append(pl)
    else:
        nPlayers = 0
    return(jsonify(nplayers=nPlayers, players=pls))

if __name__ == '__main__':
    app.run()
