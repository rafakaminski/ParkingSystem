import cv2
import numpy as np

vaga1 = [563, 381, 95, 203]
vaga2 = [429, 362, 116, 219]
vaga3 = [312, 358, 112, 212]
vaga4 = [192, 348, 110, 216]
vaga5 = [676, 374, 121, 229]
vaga6 = [796, 383, 126, 228]
vaga7 = [922, 392, 135, 225]
vaga8 = [1072, 404, 112, 219]

# vaga1 = [1, 89, 108, 213]
# vaga2 = [115, 87, 152, 211]
# vaga3 = [289, 89, 138, 212]
# vaga4 = [439, 87, 135, 212]
# vaga5 = [591, 90, 132, 206]
# vaga6 = [738, 93, 139, 204]
# vaga7 = [881, 93, 138, 201]
# vaga8 = [1027, 94, 147, 202]

vagas = [vaga1,vaga2,vaga3,vaga4,vaga5,vaga6,vaga7,vaga8]

video = cv2.VideoCapture('video2.mp4')

while True:
    check,img = video.read()
    imgCinza = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgTh = cv2.adaptiveThreshold(imgCinza,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,25,16)
    imgBlur = cv2.medianBlur(imgTh,5)
    kernel = np.ones((3,3),np.int8)
    imgDil = cv2.dilate(imgBlur,kernel)

    qtVagasAbertas = 0
    for x,y,w,h in vagas:

        recorte = imgDil[y:y+h,x:x+w]
        qtPxBranco = cv2.countNonZero(recorte)
        cv2.putText(img,str(qtPxBranco),(x,y+h-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1)

        if qtPxBranco > 3000:
            cv2.rectangle(img, (x,y), (x + w, y + h), (0, 0, 255), 3)
        else:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
            qtVagasAbertas +=1

    cv2.rectangle(img,(90,0),(300,60),(255,0,0),-1)
    cv2.putText(img,f'LIVRE: {qtVagasAbertas}/8',(95,45),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),5)

    cv2.imshow('video', img)
    cv2.imshow('video TH', imgDil)
    cv2.waitKey(10)