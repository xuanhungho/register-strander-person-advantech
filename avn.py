# Nhận diện được
from websocket import create_connection
import cv2
import json
import wget
import os

print("Connecting...")
ws = create_connection("ws://172.21.113.202/fcsreconizedresult")
while True:
    print("Receiving...")
    result =  ws.recv()
    print ("Received '%s'" % result)
    try:
        json_result = json.loads(result)
        print(json_result)
        filename = wget.download("http://172.21.113.202/persons/snapshotimage/image=" + json_result["snapshot"])
        img = cv2.imread("image=" + json_result["snapshot"])
        cv2.imshow(json_result["person_info"]["fullname"] + " - " + str(json_result["score"]), img)
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        os.remove("image=" + json_result["snapshot"])
    except:
        pass
ws.close()