#!/usr/bin/env bash

docker run -d -e LISTEN_PORT=2020 -e LISTEN_HOST=0.0.0.0 -e EXTERNAL_HOST=$(hostname) -p 2020:2020 --net=host --restart=unless-stopped --name sonos-intercom sonos-intercom
