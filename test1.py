import cv2
cap = cv2.VideoCapture('http://192.168.1.172')
while True:
    ret, img = cap.read()
    if ret == True:
        cv2.imshow('video output', img)
        k = cv2.waitKey(10)& 0xff
        if k == 27:
            break
cap.release()
cv2.destroyAllWindows()