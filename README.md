# Smart-Meter-Brute-Force-PIN
Brute forces a Smart Meter PIN

Run with:
docker run -d --device /dev/ttyS0:/dev/ttyS0 -e PYTHONUNBUFFERED=1 pin-bruteforce

and follow the logs with:
docker logs -f <container_id>
or in Portainer
