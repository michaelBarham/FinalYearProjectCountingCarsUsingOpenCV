import cv2

cap = cv2.VideoCapture('images/MVI_0360.AVI')
frames = []
for i in range(100):
    ret, frame = cap.read()
    tmp = cv2.CreateImage(cv2.GetSize(frame),8,3)
    cv2.CvtColor(frame,tmp,cv2.CV_BGR2RGB)
    frames.append(asarray(cv2.GetMat(tmp))) 
frames = array(frames)
