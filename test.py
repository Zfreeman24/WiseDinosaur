import cv2
import time
from cvzone.PoseModule import PoseDetector

pose_detector = PoseDetector()
cap = cv2.VideoCapture(0)

# Configuration and initialization
reference_hip_width_cm = 20.0
focal_length = 1426.50314625  # Calibrated focal length in pixels
distance_measurements = []  # Store recent distance measurements
max_measurements = 5  # Max measurements for averaging
last_known_good_measurement = None  # Initialize the last known good measurement
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

def is_reasonable_measurement(new_measurement, last_good_measurement, threshold=1000):
    if last_good_measurement is None:
        return True  # Accept if no previous measurement
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
        x3, y3 = lmlist[23][1], lmlist[23][2]
        x4, y4 = lmlist[24][1], lmlist[24][2]
        object_center_x = (x3 + x4) // 2
        frame_center_x = frame.shape[1] // 2

        # X-axis distance: Correctly represents left/right distance from center
        distance_from_center = object_center_x - frame_center_x

        hip_width_px = abs(x4 - x3)
        if hip_width_px > 5:
            # Correct Z-axis distance calculation
            distance_cm = (focal_length * reference_hip_width_cm) / hip_width_px

            if is_reasonable_measurement(distance_cm, last_known_good_measurement, threshold=1000):
                distance_measurements.append(distance_cm)
                if len(distance_measurements) > max_measurements:
                    distance_measurements.pop(0)

                avg_distance_cm = weighted_average(distance_measurements)  # Ensure this updates
                last_known_good_measurement = avg_distance_cm
            else:
                print("Discarded outlier measurement")

        # Ensure avg_distance_cm is a float before formatting
        if isinstance(avg_distance_cm, float):
            z_axis_text = f"Z-axis: {avg_distance_cm:.2f} cm"  # Correctly updated Z-axis distance
        else:
            z_axis_text = "Z-axis: Calculating..."

        cv2.putText(frame, f"X-axis: {distance_from_center}px", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, z_axis_text, (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Determine direction based on X-axis distance
        direction = "Move Forward"  # Default direction
        turn_threshold = 10  # Adjust based on your setup
        if distance_from_center > turn_threshold:
            direction = "Turn Left"  # Object is to the right; robot should turn left to center it
        elif distance_from_center < -turn_threshold:
            direction = "Turn Right"  # Object is to the left; robot should turn right to center it

        cv2.putText(frame, f"Direction: {direction}", (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()