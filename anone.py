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


################ HERE YOU DEFINE YOUR CONFIG ################
FRS_IP = "172.21.113.202"
USERNAME = "Admin"
PASSWORD = "123456"
REGISTER_PER_FRAME = 15

# Creating an object + Setting the threshold of logger to DEBUG
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger=logging.getLogger() 
logger.setLevel(logging.DEBUG) 

# Connect to websocket
logger.info('CONNECTING TO ' + FRS_IP + ' ...')
ws = create_connection("ws://" + FRS_IP + "/fcsnonreconizedresult")
logger.info("Connect successfully !!!")

# Login
headers = {'Content-Type': "application/json"} 
res = requests.post("http://" + FRS_IP + ":80/users/login", 
                    json = {"username": USERNAME, "password": PASSWORD}, 
                    headers=headers)
logger.debug("Login status " + str(res.status_code) + ": " + str(res.json()))

# receive data
count_frame = -1
while True:
    logger.info("Receiving data ...")
    result =  ws.recv()
    try:
        # show stranger person
        json_result = json.loads(result)
        img_name = "image=" + json_result["snapshot"]
        logger.info("Received: snapshot - " + img_name)
        count_frame += 1
    
        # Every 10 frame
        if count_frame % REGISTER_PER_FRAME == 0:
            filename = wget.download("http://" + FRS_IP + "/persons/snapshotimage/" + img_name)
            img = cv2.imread(img_name)
            cv2.imshow("PROCCESSING...", img)
            cv2.waitKey(1)
            cv2.destroyAllWindows()

            # stranger registration 
            with open(img_name, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                UUID = str(uuid.uuid1())
                data = {
                    "session_id": res.json()["sessionId"],
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
                
                res2 = requests.post("http://" + FRS_IP + ":80/frs/cgi/createperson", json = data, headers=headers)
                if res2.status_code == 200:
                    logger.debug(" --- REGISTER SUCCESSFULLY: " + UUID + "!!!!")
                else:
                    logger.debug(" --- REGISTER FAILED: " + str(res2.json()))

            # delete image after proccess
            os.remove(img_name)
            logger.debug("Deleted " + img_name)
    except:
        pass

ws.close()