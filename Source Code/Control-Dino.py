#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Point
import numpy as np
import socket
import json


def calculate_servo_angles(x, y):
    # Corrected constants
    arm_length_1 = 3.3 # cm
    arm_length_2 = 6.1 # cm
    
    # Calculate theta in radians
    theta = np.arcsin(-y / arm_length_2)
    
    # Calculate phi in radians
    phi = np.arccos(x / (arm_length_1 + arm_length_2 * np.cos(theta)))
    
    # Convert radians to degrees and ensure they're within 0-90 degrees
    def adjust_angle(angle):
        angle_deg = np.degrees(angle) % 360
        if angle_deg > 90:
            angle_deg = 90 - (angle_deg % 90)
        return angle_deg

    theta_deg1 = adjust_angle(theta)
    phi_deg1 = adjust_angle(phi)

    theta_deg2 = adjust_angle(theta - np.pi/2)
    phi_deg2 = adjust_angle(phi - np.pi/2)

    theta_deg3 = adjust_angle(theta - np.pi)
    phi_deg3 = adjust_angle(phi - np.pi)

    theta_deg4 = adjust_angle(theta - 3*np.pi/2)
    phi_deg4 = adjust_angle(phi - 3*np.pi/2)
    
    # Convert degrees to servo command (assuming 0-180 degrees maps to 0-65535)
    def convert_to_command(angle_deg):
        return max(0, min(65535, int((angle_deg / 180.0) * 65535)))

    theta_cmd1 = convert_to_command(theta_deg1)
    phi_cmd1 = convert_to_command(phi_deg1)

    theta_cmd2 = convert_to_command(theta_deg2)
    phi_cmd2 = convert_to_command(phi_deg2)

    theta_cmd3 = convert_to_command(theta_deg3)
    phi_cmd3 = convert_to_command(phi_deg3)
    
    theta_cmd4 = convert_to_command(theta_deg4)
    phi_cmd4 = convert_to_command(phi_deg4)
    
    return [theta_cmd1, phi_cmd1, theta_cmd2, phi_cmd2, theta_cmd3, phi_cmd3, theta_cmd4, phi_cmd4]

def send_servo_commands(servo_commands, host='10.184.47.202', port=12345):
    """Send servo commands to the robot via TCP socket."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            message = json.dumps(servo_commands)
            s.sendall(message.encode())
    except Exception as e:
        print(f"Failed to send servo commands: {e}")

def calculate_and_send_swing_phase_commands():
    # Simulation parameters (as previously defined)
    swing_duration = 1.0  # seconds
    time_step = 0.01  # seconds
    max_height = 0.06  # meters
    forward_distance = 5  # cm

    # Generate time points and positions
    time_points = np.arange(0, swing_duration, time_step)
    y_positions = max_height * np.sin(np.pi * time_points / swing_duration)
    x_positions = forward_distance * (time_points / swing_duration)

    # Calculate and send servo commands for each time point
    for x, y in zip(x_positions, y_positions):
        servo_commands = calculate_servo_angles(x, y)
        send_servo_commands(servo_commands)  # Send the commands to the robot

def input_callback(msg):
    # Trigger the swing phase simulation and send commands on input
    calculate_and_send_swing_phase_commands()

def listener():
    rospy.init_node('servo_angle_calculator', anonymous=True)
    rospy.Subscriber("/input", Point, input_callback)
    rospy.spin()

if __name__ == '__main__':
    listener()