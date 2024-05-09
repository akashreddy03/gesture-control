import cv2
import time

cap = cv2.VideoCapture(0)

count = 0
frame_count = 0

while(True):
    success, frame = cap.read()

    if(not success):
        print("Emtpy Frame")
        continue

    frame_count += 1

    cv2.imshow('Display', frame)

    if(cv2.waitKey(1) & 0xFF == ord('z')):
        
        count += 1

        file_name = 'IMG_' + str(time.time()) + '.jpg'

        cv2.imwrite('./dataset/none/'+file_name, frame)

        print(file_name)

    if count >= 100 or (cv2.waitKey(1) & 0xFF == ord('q')):
        break

cap.release()
cv2.destroyAllWindows()