import cv2
import time
import numpy as np
from cvzone.PoseModule import PoseDetector

def start_moving_forward():
    print("Robot starts moving forward.")  # Placeholder for actual robot movement command

def stop_moving():
    print("Robot stops.")  # Placeholder for actual robot stop command

pose_detector = PoseDetector()
cap = cv2.VideoCapture(4)  # Adjust the camera index if needed

# Configuration and initialization
reference_hip_width_cm = 20.0
focal_length = 1426.50314625  # Calibrated focal length in pixels
distance_measurements = []  # Store recent distance measurements
distance_averages = []  # Store the last five average distances
max_measurements = 5  # Max measurements for averaging
last_known_good_measurement = None  # Initialize the last known good measurement
last_distance_cm = None  # Track the last average distance to detect significant changes
start_time = time.time()
warm_up_duration = 2  # 2 seconds warm-up duration

def weighted_average(measurements, weight_increment=0.2):
    if not measurements:
        return None
    weight = 1.0  # Starting weight
    weighted_sum = 0
    total_weights = 0
    for measurement in reversed(measurements):
        weighted_sum += measurement * weight
        total_weights += weight
        weight += weight_increment  # Increment weight for recent measurements
    return weighted_sum / total_weights

def is_reasonable_measurement(new_measurement, last_good_measurement, base_threshold=1000, percentage_threshold=0.1):
    if last_good_measurement is None:
        return True  # Accept if no previous measurement
    absolute_threshold = last_good_measurement * percentage_threshold
    threshold = max(base_threshold, absolute_threshold)  # Use the larger of the base or percentage-based threshold.
    
    return abs(new_measurement - last_good_measurement) < threshold

# Warm-up loop
while (time.time() - start_time) < warm_up_duration:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.putText(frame, "Warming up...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    cv2.imshow('Frame', frame)
    cv2.waitKey(1)

# Main loop
avg_distance_cm = "Calculating..."  # Initialize as a string

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame = pose_detector.findPose(frame, draw=True)
    lmlist, _ = pose_detector.findPosition(frame, draw=True)
        
    if len(lmlist) > 24:
        # Hip landmarks
        x3, y3 = lmlist[23][1], lmlist[23][2]
        x4, y4 = lmlist[24][1], lmlist[24][2]
        hip_width_px = abs(x4 - x3)
        
        # Chest landmarks
        x1, y1 = lmlist[11][1], lmlist[11][2]
        x2, y2 = lmlist[12][1], lmlist[12][2]
        chest_width_px = abs(x2 - x1)

        # Calculate the centers of the hip and chest
        hip_center_x = (x3 + x4) // 2
        chest_center_x = (x1 + x2) // 2

        # Average the centers for a more stable center point
        object_center_x = (hip_center_x + chest_center_x) // 2
        frame_center_x = frame.shape[1] // 2

        # X-axis distance: Correctly represents left/right distance from center
        distance_from_center = object_center_x - frame_center_x

        # Use the average of hip and chest width for distance calculation
        average_width_px = (hip_width_px + chest_width_px) / 2

        if average_width_px > 5:
            distance_cm = (focal_length * reference_hip_width_cm) / average_width_px
            print(f"Calculated Distance (cm): {distance_cm}")

            # Update the array of last five average distances
            distance_averages.append(distance_cm)
            if len(distance_averages) > 5:
                distance_averages.pop(0)  # Keep the array size fixed at 5

            # Check if 2 or more of the last elements vary by 500 or more from the first 3 elements
            if len(distance_averages) == 5:
                first_three_avg = np.mean(distance_averages[:3])
                variances = [abs(first_three_avg - x) for x in distance_averages[3:]]
                significant_changes = sum(var >= 500 for var in variances)

                if significant_changes >= 2:
                    start_moving_forward()
                    # Optionally reset the array after moving forward
                    # distance_averages.clear()

                cv2.putText(frame, f"Distance: {distance_cm:.2f} cm", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Calculating distance...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            stop_moving()
    else:
        stop_moving()
        cv2.putText(frame, "No object detected", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
