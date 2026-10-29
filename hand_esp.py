import cv2
import mediapipe as mp
import math
import serial
import time

# ✅ Connect to ESP32
# For Linux: /dev/ttyUSB0 or /dev/ttyUSB1
# For Windows: COM3, COM4, etc.
esp32 = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
time.sleep(2)  # Wait for ESP32 to reset

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Open Webcam
cap = cv2.VideoCapture(0)

# Conversion factor (pixels to mm)
PIXEL_TO_MM = 0.30

# Track time for sending serial data
last_send_time = 0
SEND_INTERVAL = 0.05  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror effect
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            h, w, c = frame.shape

            # Thumb tip = 4, Index fingertip = 8
            x1, y1 = int(hand_landmarks.landmark[4].x * w), int(hand_landmarks.landmark[4].y * h)
            x2, y2 = int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h)

            # Draw circles and line
            cv2.circle(frame, (x1, y1), 10, (0, 0, 255), -1)
            cv2.circle(frame, (x2, y2), 10, (0, 255, 0), -1)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

            # Distance in pixels → mm
            distance_pixels = math.hypot(x2 - x1, y2 - y1)
            distance_mm = distance_pixels * PIXEL_TO_MM

            # Display distance
            cv2.putText(frame, f"Distance: {distance_mm:.2f} mm", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get fingertip coordinates (Index finger tip)
            x_pixel = float(hand_landmarks.landmark[8].x)
            y_pixel = float(hand_landmarks.landmark[8].y)

            # Display coordinates
            cv2.putText(frame, f"({int(x_pixel*w)}, {int(y_pixel*h)})",
                        (int(x_pixel*w) + 10, int(y_pixel*h) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # ✅ Send 3 inputs: X, Y, Distance
            current_time = time.time()
            if current_time - last_send_time >= SEND_INTERVAL:
                # Map x and y (0–1) → 0–180 range for servo compatibility
                x_mapped = int(x_pixel * 180)
                y_mapped = int(y_pixel * 180)
                d_mapped = int(min(distance_mm, 180))  # cap at 180 if using servo

                data = f"{x_mapped},{y_mapped},{d_mapped}\n"
                esp32.write(data.encode())
                print(f"Sent -> {data.strip()}")
                last_send_time = current_time

    cv2.imshow("Fingertip Tracking with Distance", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
