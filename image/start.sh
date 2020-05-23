#!/bin/sh
#
python3 server/server.py &
nginx -g "daemon off;"