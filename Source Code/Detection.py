import cv2
import time
import os
import numpy as np
import multiprocessing
from cvzone.PoseModule import PoseDetector
import pygame
from pydub import AudioSegment
from pydub.playback import play

def start_moving_forward():
    print("Robot starts moving forward.")  # Placeholder for actual robot movement command

def stop_moving():
    print("Robot stops.")  # Placeholder for actual robot stop command

def check_for_stop_signal(signal_file="stop_signal.txt"): # Check if the stop signal file was generated
    if os.path.exists(signal_file):
        with open(signal_file, "r") as file:
            content = file.read().strip()
            return content == "True"
    return False

def start_speech_process():
    """
    Starts the speech conversation logic from WiseDinosaur.py in a separate process.
    """
    from WiseDinosaur import main as wisedino_main
    speech_process = multiprocessing.Process(target=wisedino_main)
    speech_process.start()
    return speech_process

def play_roar_sound_if_condition_met():
    pygame.mixer.init()
    roar_sound = pygame.mixer.Sound("mp3/roar.mp3")
    roar_sound.play()
    pygame.time.wait(int(roar_sound.get_length() * 1000))

def main_position_detector():
    pose_detector = PoseDetector()
    cap = cv2.VideoCapture(0)  # Adjust the camera index if needed

    # Configuration and initialization
    reference_hip_width_cm = 20.0 # This is a estimation of the persons measured hips to use later in calculations, change as needed

    # Calibrate this through 'focal_length.py' to get a more accurate measurement!
    focal_length = 1426.50314625 # Calibrated focal length in pixels through 'focal_length.py' 
    
    distance_averages = []  # Store the last five average distances
    start_time = time.time()
    warm_up_duration = 2  # 2 seconds warm-up duration

    # Initialize and start the speech process
    speech_process = start_speech_process()

    # Warm-up loop
    while (time.time() - start_time) < warm_up_duration:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.putText(frame, "Warming up...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.imshow('Frame', frame)
        cv2.waitKey(1)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame = pose_detector.findPose(frame, draw=True)
        lmlist, _ = pose_detector.findPosition(frame, draw=True)
        
        # Check if we are saying 'goodbye' in the speech process
        if check_for_stop_signal():
            print("Stop signal received. Exiting program.")
            os.remove("stop_signal.txt") #Remove the temp file
            break

        if len(lmlist) > 24:
            # Hip landmarks
            x3, y3 = lmlist[23][1], lmlist[23][2] # Right hip measurement
            x4, y4 = lmlist[24][1], lmlist[24][2] # Left hip measurement
            hip_width_px = abs(x4 - x3)
            
            # Chest landmarks
            x1, y1 = lmlist[11][1], lmlist[11][2] # Right chest measurement
            x2, y2 = lmlist[12][1], lmlist[12][2] # Left chest measurement
            chest_width_px = abs(x2 - x1)

            # Calculate the centers of the hip and chest
            hip_center_x = (x3 + x4) // 2
            chest_center_x = (x1 + x2) // 2

            # Average the centers for a more stable center point
            object_center_x = (hip_center_x + chest_center_x) // 2
            #frame_center_x = frame.shape[1] // 2 # Note: This could be used to figure out when to turn the robot

            # X-axis distance: Correctly represents left/right distance from center
            #distance_from_center = object_center_x - frame_center_x # Note: This would be used later for calculuting when to turn the robot 

            if object_center_x > 5:
                distance_cm = (focal_length * reference_hip_width_cm) / object_center_x
                #print(f"Calculated Distance (cm): {distance_cm}")

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
                        play_roar_sound_if_condition_met() # for some reason this is causing lag, need to look at multiprocessing issues?
                        print("roaring")
                        start_moving_forward()

                    cv2.putText(frame, f"Distance: {distance_cm:.2f} cm", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Calculating distance...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                stop_moving()
        else:
            stop_moving()
            cv2.putText(frame, "No object detected", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the frame
        cv2.imshow('Frame', frame)
    
        # Check if user quit the program manually
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    speech_process.terminate()  # Terminate the speech process if it's still running
    speech_process.join()  # Wait for the speech process to properly terminate

if __name__ == "__main__":
    main_position_detector()