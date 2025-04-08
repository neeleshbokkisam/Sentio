import cv2
img = cv2.imread("test.jpg")  # use any small image file
cv2.imshow("Test Window", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
