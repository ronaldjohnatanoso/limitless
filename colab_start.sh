#!/bin/bash

!curl -fsSL https://tailscale.com/install.sh | sh

!sudo apt install daemonize -y

!sudo daemonize /usr/sbin/tailscaled --tun=userspace-networking --socks5-server=localhost:1055 --outbound-http-proxy-listen=localhost:1055

!sudo tailscale up --auth-key=tskey-auth-ky7ec7hSoq11CNTRL-i9DayYuP6oXT2qDRhbSZnXyYYBu3UeScf --hostname=colab

!tailscale status