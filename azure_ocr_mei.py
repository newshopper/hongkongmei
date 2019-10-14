import os
import sys
import time

import http.client, urllib.request, urllib.parse, urllib.error, base64

import json 
import requests

# Add your Computer Vision subscription key to your environment variables.
if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
    subscription_key = os.environ['COMPUTER_VISION_SUBSCRIPTION_KEY']
else:
    print("\nSet the COMPUTER_VISION_SUBSCRIPTION_KEY environment variable.\n**Restart your shell or IDE for changes to take effect.**")
    sys.exit()
# Add your Computer Vision endpoint to your environment variables.
if 'COMPUTER_VISION_ENDPOINT' in os.environ:
    endpoint = os.environ['COMPUTER_VISION_ENDPOINT']
else:
    print("\nSet the COMPUTER_VISION_ENDPOINT environment variable.\n**Restart your shell or IDE for changes to take effect.**")
    sys.exit()


mei_url = "https://i.redd.it/10ot7yocodr31.png"

#https://{endpoint}/vision/v2.0/ocr[?language][&detectOrientation]
# url = "{}vision/v2.0/ocr?{}&true".format(endpoint,"zh-Hans")
# print(url)


headers = {
    'Content-Type': "application/json",
    'Ocp-Apim-Subscription-Key': subscription_key
}

params = urllib.parse.urlencode({
    'language': "unk",
    "detectOrientation": 'true',
})

dict_body = {"url":mei_url}
json_body = json.dumps(dict_body)
# try:
#     conn = http.client.HTTPSConnection('eastus.api.cognitive.microsoft.com')
#     conn.request("POST", "/vision/v2.0/ocr?%s" % params, "{body}", headers)
#     response = conn.getresponse()
#     data = response.read()

#     decoded_output = data.decode('utf8').replace("'", '"')

#     # load = json.loads(decoded_output)

#     # output = json.dumps(load, indent=4, sort_keys=True)

#     print(decoded_output)
#     conn.close()
# except Exception as e:
#     print("[Errno {0}] {1}".format(e.errno, e.strerror))

params = {'language': 'unk', 'detectOrientation':'true'}
headers = {'Content-type': 'application/json', 'Ocp-Apim-Subscription-Key': subscription_key}
req = requests.post('https://eastus.api.cognitive.microsoft.com/vision/v2.0/ocr', headers=headers, params=params, data=json_body)
print(req.json())    

with open('mei_test.txt', 'w') as outfile:
    json.dump(req.json(), outfile)