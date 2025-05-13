import RPi.GPIO as GPIO
import time
import subprocess
from datetime import datetime
import os

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define pin numbers
TRIG_PIN = 23      # GPIO pin for ultrasonic trigger
ECHO_PIN = 24      # GPIO pin for ultrasonic echo
BUZZER_PIN = 17    # GPIO pin for buzzer

# Set up the GPIO pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Initialize buzzer as PWM device
buzzer = GPIO.PWM(BUZZER_PIN, 440)  # 440 Hz (A4 note)

def get_distance():
    """Measure distance using ultrasonic sensor"""
    # Clear the trigger pin
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.2)
    
    # Send a 10us pulse to trigger
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)
    
    # Measure the echo time
    pulse_start = time.time()
    timeout = pulse_start + 0.1  # 100ms timeout
    
    # Wait for echo to go high
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
        if pulse_start > timeout:
            return None  # Timeout, no echo received
    
    # Wait for echo to go low
    pulse_end = time.time()
    timeout = pulse_end + 0.1  # 100ms timeout
    
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
        if pulse_end > timeout:
            return None  # Timeout, echo too long
    
    # Calculate distance
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound: 343 m/s = 34300 cm/s
                                      # Divide by 2 for round trip
    return round(distance, 2)  # Return distance in cm

def sound_buzzer():
    """Sound the buzzer for alert"""
    buzzer.start(50)  # 50% duty cycle
    time.sleep(0.5)
    buzzer.stop()

def capture_video(duration=10):
    """Capture video using libcamera-vid for specified duration"""
    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"detection_{timestamp}.mp4"
    
    # Create videos directory if it doesn't exist
    os.makedirs("videos", exist_ok=True)
    filepath = os.path.join("videos", filename)
    
    print(f"Recording video to {filepath}...")
    
    try:
        # Use libcamera-vid command to record video
        cmd = [
            "libcamera-vid",
            "-t", str(duration * 1000),  # Duration in milliseconds
            "-o", filepath,
            "--width", "1280",
            "--height", "720",
            "--framerate", "30",
            "--codec", "h264"
        ]
        
        # Run the command
        subprocess.run(cmd, check=True)
        print("Video recording complete")
        
    except subprocess.CalledProcessError as e:
        print(f"Error recording video: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Define the detection threshold (in cm)
DETECTION_THRESHOLD = 30

try:
    print("Starting object detection system with libcamera...")
    print("Press CTRL+C to exit")
    
    while True:
        distance = get_distance()
        
        # Check if we got a valid distance reading
        if distance is not None:
            print(f"Distance: {distance} cm")
            
            # If object is detected within threshold
            if distance < DETECTION_THRESHOLD:
                print("Object detected!")
                sound_buzzer()
                capture_video(10)  # Record for 10 seconds
                
                # Wait after recording to avoid triggering again immediately
                time.sleep(2)
        
        # Short delay between measurements
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Program stopped by user")

finally:
    # Clean up GPIO pins
    GPIO.cleanup()
    print("GPIO cleanup completed")
