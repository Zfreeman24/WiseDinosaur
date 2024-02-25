import cv2
# import os
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 
import time
from cvzone.PoseModule import PoseDetector

pose_detector = PoseDetector()
cap = cv2.VideoCapture(0)

# Reference dimensions in centimeters
reference_chest_width_cm = 30.0
reference_hip_width_cm = 20.0

# Placeholder for actual focal length you need to calibrate
focal_length = 1426.50314625

# Initialize a list to store the last few distance measurements for averaging
distance_measurements = []

# Define the maximum number of measurements to use for the moving average
max_measurements = 5

# Define the maximum allowed change in distance per frame to filter out large spikes
max_change_per_frame = 10.0

# Define a variable to keep the last known good measurement
last_known_good_measurement = None

avg_distance_cm = "Calculating..."
start_time = time.time()
warm_up_duration = 3  # 3 seconds

# Warm-up loop: Capture and discard frames for the warm-up duration
while (time.time() - start_time) < warm_up_duration:
    ret, frame = cap.read()
    if not ret:
        break  # If frame capture fails, exit the loop
    # Optionally, display the frame during warm-up with a notice
    cv2.putText(frame, "Warming up...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow('Body Pose Detection with Distance Measurement', frame)
    cv2.waitKey(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip the frame horizontally

    # Detect pose and find landmarks
    frame = pose_detector.findPose(frame, draw=True)
    lmlist, _ = pose_detector.findPosition(frame, draw=True)

    if len(lmlist) > 24:  # Check if we have hip landmarks
        # Use hip landmarks for distance calculation
        x3, y3 = lmlist[23][1], lmlist[23][2]
        x4, y4 = lmlist[24][1], lmlist[24][2]
  

        hip_width_px = abs(x4 - x3)

        if hip_width_px > 5:
            # Calculate distance using the hip width
            distance_cm = (focal_length * reference_hip_width_cm) / hip_width_px
            # Inside your main loop, after calculating distance_cm:
            print(f"Current Hip Width (px): {hip_width_px}, Distance (cm): {distance_cm}")

            # Add the new measurement to the list and trim the list to maintain the size
            distance_measurements.append(distance_cm)
            if len(distance_measurements) > max_measurements:
                distance_measurements.pop(0)

            # Calculate the moving average of the distance measurements
            if len(distance_measurements) == max_measurements:
                avg_distance_cm = sum(distance_measurements) / len(distance_measurements)

                # Use the moving average as the new measurement if the change is not too large
                if last_known_good_measurement is None or abs(avg_distance_cm - last_known_good_measurement) < max_change_per_frame:
                    last_known_good_measurement = avg_distance_cm
                else:
                    # If the change is too large, keep the last known good measurement
                    avg_distance_cm = last_known_good_measurement

                # # Clear the distance_measurements after calculating the moving average
                distance_measurements.pop(0)  # This resets the list for new measurements
        else:
            avg_distance_cm = last_known_good_measurement if last_known_good_measurement is not None else "Calculating..."

        # Display the smoothed distance on the frame
        print(f"Average Distance (cm): {avg_distance_cm}")
        text = f"Smoothed Distance: {avg_distance_cm:.2f} cm" if isinstance(avg_distance_cm, float) else avg_distance_cm
        cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow('Body Pose Detection with Distance Measurement', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
