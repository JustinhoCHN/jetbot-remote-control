import requests
import json
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--log', type=str, default='log/server.log', help='log path')
parser.add_argument('--api', type=str, default='http://localhost:5501/log', help='api')
args = parser.parse_args()

fn = args.log
api = args.api

p = 0
while True:
    f = open(fn, 'r+')
    f.seek(p, 0)

    lines = f.readlines()

    if lines:
        r = requests.post(api, data={'content': lines})

    p = f.tell()
    f.close()
    time.sleep(0.1)