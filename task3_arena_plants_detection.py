import cv2
import cv2.aruco
import numpy
#906x893


img=cv2.imread("/Users/vivekyadav/Downloads/Task3.png",1)
img_hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
lb=numpy.array([20,150,50])
ub=numpy.array([30,255,255])
img_yel=cv2.inRange(img_hsv,lb,ub)
con,hi=cv2.findContours(img_yel,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)         #masked_gray worked

areas=[]
areasd={}

for id,bound in enumerate(con):
    mom=cv2.moments(bound)
    areas.append(mom["m00"])
    areasd[mom["m00"]]=id

areas.sort(reverse=True)
plants=[con[areasd[areas[0]]],con[areasd[areas[1]]]]

for i in plants:
    cv2.drawContours(img,[i],0,(255,0,0),2)


#---------------------------------------------------------------------------------------------


dic = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
myrules = cv2.aruco.DetectorParameters()
myrules.adaptiveThreshWinSizeMin = 5
device = cv2.aruco.ArucoDetector(dic, myrules)
vrt, cod, otcst = device.detectMarkers(img)

X=[]
Y=[]
for i, n in enumerate(vrt):
    n = n[0]
    for _,cord in enumerate(n):
        X.append(int(cord[0]))
        Y.append(int(cord[1]))
        #print(cord[0])

x1,x2=min(X),max(X)
y1,y2=min(Y),max(Y)

cv2.rectangle(img,(x1,y1),(x2,y2),(255, 0, 0),3)
    
#cv2.imwrite("task3_output_arena_plants.png",img)
cv2.imshow("dis",img)
cv2.waitKey(0)
cv2.destroyAllWindows()