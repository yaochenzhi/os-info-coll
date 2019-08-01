#!/opt/datadog-agent/embedded/bin/python
# Date: 38
# Auth: yao
# Desc: null

from requests.exceptions import ConnectTimeout
from os import path
import requests
import socket
import json


local_ip = socket.gethostbyname(socket.gethostname())
req_host_file = "/opt/req_host_file"
update_url = "http://20.26.37.208:8080/api/web"


def get_req_host():
    hl = []
    if path.exists(req_host_file):
        with open(req_host_file) as f:
            for l in f:
                hl.append(l.strip())
    return hl


def get_req_status(hl):
    hsl = []
    for h in hl:
        try:
            l = "http://{}:{}".format(h, "2345")
            r = requests.get(l, timeout=3)
            s = r.status_code
            t = r.elapsed.total_seconds()
        except ConnectTimeout:
            s = -1
            t = -1
        except Exception:
            s = -2
            t = -2
        hsl.append({
            "local_ip": local_ip,
            "remote_ip": h,
            "update_status": s,
            "response_time": t
            })
    return hsl


def update_status(hsl):
    print(json.dumps(hsl, indent=4))
    r = requests.post(update_url, json=hsl)
    print(r.text)


def main():
    update_status(get_req_status(get_req_host()))


if __name__ == '__main__':
    main()