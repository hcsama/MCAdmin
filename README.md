# MCAdmin - A simple Web GUI for monitoring and managing your Minecraft server
# *This is Version 2 of the GUI using svelte instead of vue.js and a more sophisticated interface to the server*

This release offers basic functionality:
- Connect to any Java Minecraft (forge or plain vanilla) server configured for RCON
- Show number of in-game days
- Show server uptime
- Show in-game time of day
- Send message to all players
- Show list of players on server
- Manage whitelist (only legitimate players)
- Turn whitelist on and off
- Set weather
- Set some of the gamerules

**MCAdmin has not been tested with Bedrock and will probably not work with Bedrock**

**It has been tested with Minecraft version 1.20.1 and should also work with later versions**

---
## Step 1: Prepare your Minecraft server
MCAdmin uses the [RCON](https://developer.valvesoftware.com/wiki/Source_RCON_Protocol) feature of the server. You don't really need to worry about understanding the protocol or the commands.  
You do have to activate the feature on your server in order for MCAdmin to work.

You need to set two variables in the [server.properties](https://minecraft.gamepedia.com/Server.properties) file of your Minecraft server. This obviously requires that you have access to where the server runs.

Find and override the following lines in your `server.properties` file. Pick any password you like for `rcon.password` - but do pick a password because RCON access provides superuser power over your server.

    rcon.port=25575
    rcon.password=PUT_YOUR_FAVOURITE_PASSWORD_HERE
    enable-rcon=true

If you are using a hosted server, maybe RCON is already enabled or you may be able to enable it in some other way. You need to check with your provider. Make sure to set the correct port for RCON. And make sure the port is accessible for MCAdmin.

If you are running your minecraft server in docker (very convenient!) you will have to expose the rcon port 25575 so that it can be accessed by MCAdmin. `itzg/minecraft-server` is a good choice for a minecraft server image. Refer to https://docker-minecraft-server.readthedocs.io/en/latest/ for how to use it.

**Note: You can use other ports instead of the Minecraft default ports. See the section on environment variables later**

---
## Step 2: Run MCAdmin

### Fundamentals
As of version 2, MCAdmin consists of two servers.
- `mcadmin-api` connects to the Minecraft server and maintains state information
- `mcadmin-frontend` servers the GUI elements and uses `mcadmin-api` to access Minecraft

### Simple setup
You can simply use docker.
#### 1 - API Server
Run the latest version of `hcsama/mcadmin-api`.
```
docker run -d -e MC_HOST=<your minecraft server IP or hostname> \
              -e MC_RCON_PASSWORD=<whatever password you set for RCON> \
              hcsama/mcadmin-api
```
This gives you the MCAdmin API server running on port 8000.

#### 2 - GUI Server
Run the latest version of `hcsama/mcadmin-frontend` once the API server is up and runing without errors.
```
docker run -d -e API_URL='http://localhost:8000' \
              -p 8080:3000 hcsama/mcadmin-frontend
```

This will give you access to MCAdmin at http://localhost:8080. Replace `localhost` with the name of your docker server if you are running docker on a separate machine.

### Using Docker Compose
You can also use docker-compose and maybe some simple management solution such as [Portainer](https://www.portainer.io/).

A sample docker compose file is included in the repository (`docker-compose.yaml`).

### Environment variables
#### API Server settings
MCAdmin API server requires your Minecraft server's address (ip or hostname) and RCON password. You can provide values through environment variables during container start.

    MC_HOST - The IP address or hostname of your Server
    MC_RCON_PASSWORD - The password you put in the server.properties (rcon.password)

See above for an example how to start the API server.

The server supports a number of additional environment variables (please also refer to `.env.example`):

- `MC_PORT` - The RCON port of the Minecraft server. Default is 25575
- `MC_GAME_PORT` - The regular Minecraft server port for game clients (MCAdmin also uses it during startup). Default is 25565
- `MC_POLL_INTERVAL_SERVER` - Number of seconds between updates of the overall server status. Default is 10s
- `MC_POLL_INTERVAL_WORLD` - Number of seconds between updates of the world time. Default is 5s
- `MC_POLL_INTERVAL_PLAYERS` - Number of seconds between updates of player list. Default is 5s
- `MC_POLL_INTERVAL_WHITELIST` - Number of seconds between updates of Whitelist. Default is 10s
- `MC_POLL_INTERVAL_GAMERULES` - Duration of a gamerules update cycle. During one cycle, all gamerules are polled once


#### GUI Server settings
The GUI server requires one environment variable that tells it where to find the API server.

    API_URL - A url in the format http://<API server host or IP>:8000

The API server by default publishes its services on port 8000. You could map that to another port through docker and adjust the `API_URL` if necessary for your environment.

---

## Step 3: Use MCAdmin

Now for the best part - using MCAdmin. Point your browser to MCAdmin (http://localhost:8080, or similar).  

You will see the MCAdmin web page.

If connectivity works and your password is correct, the status area at the top should show the name of your server, show that is online, show the server's uptime and on the right should show in-game time and phase of day (you can stop in-game time with a toggle).

If your server is a forge server, this will be indicated and you can drop down the list of mods and see exactly the list of active mods and their versions.

Below the status area, there is a tile where you can send (annoying) messages to all players.

Below that you have the list of active players and you can manage the whitelist if you want to limit access to your server. Note the player avatars. There also is a tile to control the weather and stop or continue the weather cycle.

Finally at the bottom you see all gamerules you can change and their current settings. Some rules might be greyed out, depending on the version of your server.

## Troubleshooting

- Are the values in server.properties correct?
- Did you restart the Minecraft server after enabling RCON?
- Is the rcon port 25575 exposed?
- Have you provided the right password to MCAdmin?

---
## Security
MCAdmin is not a production ready application. Connection is via `http` and thus not secure. It would be possible to set up NGINX to support `https`, but I have not done so.

Also, RCON connections should not be exposed over/on the internet.

---
## Contributing
I would welcome contributions. I am no web designer so anyone with a good feeling for design who wants to help make this application look more awsome and more Minecraft-like is more than welcome.

There are many more things that could be improved. RCON has many more commands and features that could be exploited. The Minecraft server offers more options for monitoring of minecraft.

---
## Acknowledgements

MCAdmin is a [Svelte + SveltekKit](https://svelte.dev/) application (it also uses [Tailwind CSS with Vite](https://tailwindcss.com/docs/installation/using-vite)) with a [python](https://www.python.org) server that uses [mcstatus](https://pypi.org/project/mcstatus/), [Aio-MC-RCON](https://pypi.org/project/aio-mc-rcon/) and [FastAPI](https://fastapi.tiangolo.com/). 

Yóu can find the source code on [github](https://github.com/hcsama/MCAdmin).

Please respect the MCAdmin GNU GPLV3 license.
