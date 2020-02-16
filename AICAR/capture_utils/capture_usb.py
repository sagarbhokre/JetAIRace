import cv2

cap = cv2.VideoCapture(1)
while True:
    ret, frame = cap.read()
    cv2.imshow("USB Camera" , frame)
    k = cv2.waitKey(33) & 0xFF
    if k == 27 or k == ord('q'):
        break

