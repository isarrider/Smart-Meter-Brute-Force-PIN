# Smart-Meter-Brute-Force-PIN
Brute forces a Smart Meter PIN

Uart must be enabled:
#-------Serial/UART-----
# NB: "enable_uart=1" will enforce "core_freq=250" on RPi models with onboard WiFi.
enable_uart=1

and a Smart Meater IR Read Write Dongle (Schreib Lese Kopf) has to be attached - I use this one:
https://www.ebay.de/itm/296425429208?itmmeta=01KRE6PEXYJYT9Z03Q1V2C5TQ7&hash=item45045518d8:g:0yUAAOSwpDJl9wjE

Run with:
docker run -d --device /dev/ttyS0:/dev/ttyS0 -e PYTHONUNBUFFERED=1 pin-bruteforce

and follow the logs with:
docker logs -f <container_id>

or in Portainer




______

Still WIP, as I wanna test it...
