# Không nhận diện được
from websocket import create_connection
import cv2
import json
import wget
import base64
import requests 
import uuid 
import os
import time
import logging

################ HERE YOU DEFINE YOUR IP ADDRESS ################
FSR_IP = "172.21.113.202"


# Creating an object + Setting the threshold of logger to DEBUG
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 

# Connect to websocket
logger.info('CONNECTING TO ' + FSR_IP + ' ...')
ws = create_connection("ws://" + FSR_IP + "/fcsnonreconizedresult")
logger.info("Connect successfully !!!")

# Login
headers = {'Content-Type': "application/json"} 
res = requests.post("http://" + FSR_IP + ":80/users/login", 
                    json = {"username": "Admin", "password": "123456"}, 
                    headers=headers)
res_json = res.json()
logger.debug("login status: " + str(res) + str(res_json))

# receive data
while True:
    logger.info("Receiving data ...")
    result =  ws.recv()
    logger.info ("Received: '%s'" % result)
    try:

        # show stranger person
        json_result = json.loads(result)
        filename = wget.download("http://" + FSR_IP + "/persons/snapshotimage/image=" + json_result["snapshot"])
        img = cv2.imread("image=" + json_result["snapshot"])
        cv2.imshow("UNKNOWN", img)
        cv2.waitKey(1)
        cv2.destroyAllWindows()

        # stranger registration
        with open("image=" + json_result["snapshot"], "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            UUID = str(uuid.uuid1())
            data = {
                "session_id": res_json["sessionId"],
                "person_info": {
                    "fullname": UUID,
                    "employeeno": UUID,
                    "cardno": UUID,
                    "group_list": [
                        {
                            "id": "5ebc9dc8978c5f076be8c31e",
                            "groupname": "Employee"
                        }
                    ],
                    "department_list": [
                        {
                            "objectId": "N5Lr5E2OzD",
                            "no": "",
                            "name": "0001"
                        }
                    ]
                },
                "image": str(encoded_string.decode('utf-8'))
            }
            logger.debug(data)
            res2 = requests.post("http://" + FSR_IP + ":80/frs/cgi/createperson", 
                                json = data, 
                                headers=headers)
            logger.debug(res2 + str(res2.json()))
        
        # delete image after proccess
        os.remove("image=" + json_result["snapshot"])
    except:
        pass
ws.close()