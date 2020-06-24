# MCAdmin - A simple Web GUI for monitoring and managing your Minecraft server

This release offers basic functionality:
- Connect to any Minecraft server configured for RCON
- Show number of in-game days
- Show server uptime
- Show in-game time of day
- Send message to all players
- Show simple list of players on server
- Set some of the gamerules
- Set day/night and weather
- Manage whitelist (only legitimate players)
- Turn whitelist on and off

**MCAdmin has been tested with a plain vanilla server. Some features will not work with Bedrock servers.**
**The currently supported minecraft version is 1.16.1.**

---
## Step 1: Prepare your Minecraft server
MCAdmin uses the [RCON](https://developer.valvesoftware.com/wiki/Source_RCON_Protocol) feature of the server. You don't really need to worry about understanding the protocol or the commands.  
You do have to activate the feature on your server in order for MCAdmin to work.

You need to set two variables in the [server.properties](https://minecraft.gamepedia.com/Server.properties) file of your Minecraft server. This obviously requires that you have access to where the server runs.

Find and override the following lines in your `server.properties` file. Pick any password you like for `rcon.password` - but do pick a password because RCON access provides superuser power over your server.

    rcon.port=25575
    rcon.password=PUT_YOUR_FAVOURITE_PASSWORD_HERE
    enable-rcon=true

If you are using a hosted server, maybe RCON is already enabled or you may be able to enable it in some other way. You need to check with your provider. Make sure to set the correct port for RCON. And make sure the port is accessible from MCAdmin.

If you are running your minecraft server in docker (very convenient!) you will have to expose the rcon port 25575 so that it can be accessed by MCAdmin. Alternatively you can add a container link to mcadmin (see below for example) to avoid having to expose this potentially dangerous port.

After making this change, you will have to restart your server.

---
## Step 2: Run MCAdmin

### Simple setup

Just run the latest version of `hcsama/mcadmin`. You can simply use docker.

    docker run -d -p 8080:80 hcsama/mcadmin

This would give you access to MCAdmin at http://localhost:8080. Replace `localhost` with the name of your docker server if you are running docker on a separate machine.

### Linking to Minecraft server container in docker

By linking your Minecraft container with your MCAdmin container you avoid having to expose the RCON port which is generally a good idea.

    docker run -d -p 8080:80 --link <name or id>:minecraft hcsama/mcadmin

You'll need to replace `<name or id>` with the container id or name of your Minecraft server container.

### Environment variables
#### Server settings
MCAdmin requires your Minecraft server's address (ip or hostname) and RCON password. You can simply enter this information on the MCAdmin page or you can predefine values through environment variables during container start.

    MCSERVER_ADDR - The IP address or hostname of your Server
    MCSERVER_SECR - The password you put in the server.properties (rcon.password)

It is up to you if you really want to put the password into an inherently unsecure environment variable - but you can.

Starting MCAdmin with a predefined server address:

    docker run -d -p 8080:80 --env MCSERVER_ADDR=<hostname of docker machine> hcsama/mcadmin

That's the most simple way again. Assuming your Minecraft server is visible on your docker server and you have exposed the RCON port, too. You could add another `--env MCSERVER_SECR=iamsosecret` to this command if you also wanted to predefine the RCON password.

If you are using container linking above, your run command looks like:

    docker run -d -p 8080:80 --env MCSERVER_ADDR=minecraft hcsama/mcadmin
#### Debugging
    MCSEERVER_DEBG - Debug mode for backend
Setting this to a non-empty string turns on debug logging on backend.

---
## Step 3: Use MCAdmin

Now for the best part - using MCAdmin. Point your browser to MCAdmin (http://localhost:8080, or similar).  
You will see the MCAdmin web page. At the top you enter the server address (will be pre-populated if you used the environment variables) and next to it you enter the RCON password. That's it!  
If connectivity works and your password is correct the indicator at the top should turn to green/connected and you should see information about your server and can send annoying messages to your players.

## Troubleshooting

- Are the values in server.properties correct?
- Did you restart the server?
- Is the rcon port 25575 exposed?
- Have you provided the right password to MCAdmin?
---
## Security
MCAdmin is not a production ready application. Connection is via `http` and thus not secure. It would be possible to set up NGINX to support `https`, but I have not done so.

Also, RCON connection should not be exposed over/on the internet.

---
## Contributing
I would welcome contributions. I am no web designer so anyone with a good feeling for design who wants to help make this application look more awsome and more Minecraft-like is more than welcome.

There are many more things that could be improved. RCON has many more commands and features that could be exploited. The Minecraft server offers more options for monitoring of minecraft.

---
## Acknowledgements

MCAdmin is a [vuejs](https://vuejs.org) application with a [python](https://www.python.org) server. The http server and router is [NGINX](https://www.nginx.com).

Yóu can find the source code on [github](https://github.com/hcsama/MCAdmin).

In building this application I used the following excellent components:

- vue-clock2: https://www.npmjs.com/package/vue-clock2
- vue-good-table: https://xaksis.github.io/vue-good-table/?ref=madewithvuejs.com
- Flask: https://palletsprojects.com/p/flask/
- mcrcon: https://pypi.org/project/mcrcon/

I copied some code from here: https://codepen.io/gau/pen/LjQwGp

Please respect the MCAdmin GNU GPLV3 license.
