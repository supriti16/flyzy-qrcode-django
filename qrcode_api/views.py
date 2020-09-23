from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
import requests
import json
import cv2
from wand.image import Image
from pyzbar.pyzbar import decode
import numpy as np
import urllib.request as rq


@api_view(['POST'])
def User_Info(request):
    payload = {

        "userId": request.data['userId'],
        "flightId": request.data['flightId']

    }
    try:
        resp = requests.post('https://us-central1-flyzydev.cloudfunctions.net/flight/getBoardingPassURLNew/', json=payload)
        resp.json()
        body = resp.json()[0].get("boardingPassesInfo")
        boardingDataArray = []
        for ele in body:
            url=ele.get('boardingPassUrl')
            r = requests.get(url)
            file = open("sample_image.png", "wb")
            file.write(r.content)
            img = cv2.imread("sample_image.png")

            for barcode in decode(img):
                mydata = barcode.data.decode('utf-8')
                print(mydata)
                mydata = "{\""+mydata+"\"}"
                mydata = mydata.replace(": ", "\":\"").replace("\r\n", "\",\"").replace("\",", "\",\n")
                mydata=json.loads(mydata)
                jsonData = {
                    "passengerName": mydata["Passanger name"],
                    "imageUrl": url,
                    "pnr": "LKI997",
                    "seatNo": mydata["Seat"],
                    "seatClass": "Economy"
                }
                boardingDataArray.append(jsonData)
        updateUrl = 'https://us-central1-flyzydev.cloudfunctions.net/flight/updateBoardingPass/'
        uploadPayload = {
                "userId": request.data['userId'],
                "flightId": request.data['flightId'],
                "passengerInfo": boardingDataArray
        }

        x = requests.post(updateUrl, json=uploadPayload)



        print(x.text)


        data = {'message': 'data uploaded successfully' }
        return JsonResponse(data,safe=False)
    except ValueError as e:
        print(e)
