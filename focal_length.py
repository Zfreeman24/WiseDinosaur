import cv2

# Used to calculate focal length for Detection.py
# Choose an object with a known width and place it at a known exact distance.
# Run the program and measure the known object by selecting two points on either side of the object to get the pixel width
#distance is 36" or 91cm 376.22061 pixels
# width is 9.5"or 24 cm
# focal length = 1426.50314625
# 1691.43785
# 63" 160.02
# 12" 30cm
# 317.1049598406741 pixels

def calculate_focal_length(knownWidth, knownDistance, perWidth):
    # Calculate and return the focal length
    return (perWidth * knownDistance) / knownWidth

# Known dimensions and distance
KNOWN_WIDTH_CM = 21.0  # Width of A4 paper
KNOWN_DISTANCE_CM = 50.0  # Distance from camera to object

# Capture an image
cap = cv2.VideoCapture(4)
ret, frame = cap.read()
cap.release()

# Check if image was captured
if not ret:
    print("Failed to capture image")
    exit()

# Display the image and use mouse clicks to measure object width in pixels
def click_event(event, x, y, flags, params):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(frame, (x,y), 2, (255, 0, 0), -1)
        points.append((x, y))
        
        if len(points) == 2:
            cv2.line(frame, points[0], points[1], (255, 0, 0), 2)
            perWidth = cv2.norm(points[0], points[1], cv2.NORM_L2)
            focal_length = calculate_focal_length(KNOWN_WIDTH_CM, KNOWN_DISTANCE_CM, perWidth)
            print(f"Focal Length: {focal_length} pixels")
            cv2.imshow("Frame", frame)

points = []
cv2.imshow("Frame", frame)
cv2.setMouseCallback("Frame", click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()
