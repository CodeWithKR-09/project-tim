import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import subprocess

# ======================================================================
# 1. SYSTEM SETTINGS
# ======================================================================
MOBILE_CAM_URL = "http://192.168.1.36:8080/video"

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.01
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Sensitivity & Boundary Settings
MARGIN = 90             # Larger margin = easier to reach screen edges
SMOOTHING = 0.20        # Lower value = smoother cursor (less jitter)
prev_x, prev_y = 0, 0

# --- THRESHOLDS FOR PREVENTING ACCIDENTAL CLICKS ---
PINCH_START = 25        # Distance (px) to START a click/drag (Tighter)
PINCH_RELEASE = 38      # Distance (px) to RELEASE a drag (Prevents chatter)

RIGHT_CLICK_DIST = 26   # Middle-finger pinch distance
FIST_DIST = 45          # Minimum distance to consider fingers closed into a fist

# Debounce Counters & Hold Timers
right_click_frames = 0
fist_frames = 0
open_palm_start = None
PALM_HOLD_DURATION = 1.0  # Must hold open palm for 1 full second to open app

last_action_time = 0
ACTION_COOLDOWN = 1.5
is_dragging = False

# ======================================================================
# 2. MEDIAPIPE INITIALIZATION
# ======================================================================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75, # Slightly higher confidence to reduce noise
    min_tracking_confidence=0.75
)

print(f"[*] Connecting to Mobile Stream: {MOBILE_CAM_URL}")
cap = cv2.VideoCapture(MOBILE_CAM_URL)

def count_extended_fingers(landmarks):
    """Counts open fingers excluding the thumb."""
    tips = [8, 12, 16, 20]
    count = 0
    for tip in tips:
        if landmarks[tip].y < landmarks[tip - 2].y:
            count += 1
    return count

# ======================================================================
# 3. MAIN LOOP
# ======================================================================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        time.sleep(0.5)
        cap = cv2.VideoCapture(MOBILE_CAM_URL)
        continue

    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    current_time = time.time()

    # Draw region box
    cv2.rectangle(frame, (MARGIN, MARGIN), (w - MARGIN, h - MARGIN), (255, 255, 0), 2)
    cv2.putText(frame, "Air-Mouse Active (Calibrated)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            # Key positions
            index_tip = np.array([lm[8].x * w, lm[8].y * h])
            thumb_tip = np.array([lm[4].x * w, lm[4].y * h])
            middle_tip = np.array([lm[12].x * w, lm[12].y * h])

            # Coordinate mapping
            x_mapped = np.interp(index_tip[0], [MARGIN, w - MARGIN], [0, SCREEN_WIDTH])
            y_mapped = np.interp(index_tip[1], [MARGIN, h - MARGIN], [0, SCREEN_HEIGHT])

            # Exponential Cursor Smoothing
            curr_x = prev_x + (x_mapped - prev_x) * SMOOTHING
            curr_y = prev_y + (y_mapped - prev_y) * SMOOTHING
            prev_x, prev_y = curr_x, curr_y

            extended_count = count_extended_fingers(lm)
            pinch_index = np.linalg.norm(index_tip - thumb_tip)
            pinch_middle = np.linalg.norm(middle_tip - thumb_tip)

            # ----------------------------------------------------------
            # ACTION 1: HYSTERESIS CLICK & DRAG (Eliminates Chatter)
            # ----------------------------------------------------------
            if not is_dragging:
                if pinch_index < PINCH_START:
                    pyautogui.mouseDown()
                    is_dragging = True
                    print("[Action] Left Mouse Down")
                else:
                    pyautogui.moveTo(curr_x, curr_y)
            else:
                cv2.putText(frame, "HOLDING / DRAGGING", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                pyautogui.moveTo(curr_x, curr_y)
                # Requires explicit opening past PINCH_RELEASE to drop mouse
                if pinch_index > PINCH_RELEASE:
                    pyautogui.mouseUp()
                    is_dragging = False
                    print("[Action] Left Mouse Up")

            # ----------------------------------------------------------
            # ACTION 2: RIGHT CLICK (Requires 3 consecutive frames)
            # ----------------------------------------------------------
            if pinch_middle < RIGHT_CLICK_DIST and not is_dragging:
                right_click_frames += 1
                if right_click_frames >= 3 and (current_time - last_action_time > ACTION_COOLDOWN):
                    pyautogui.rightClick()
                    print("[Action] Right Click Triggered")
                    last_action_time = current_time
                    right_click_frames = 0
            else:
                right_click_frames = 0

            # ----------------------------------------------------------
            # ACTION 3: CLOSE WINDOW (Fist Gesture - Requires 4 frames)
            # ----------------------------------------------------------
            if extended_count == 0 and pinch_index > FIST_DIST:
                fist_frames += 1
                if fist_frames >= 4 and (current_time - last_action_time > ACTION_COOLDOWN):
                    pyautogui.hotkey('alt', 'f4')
                    print("[Action] Closed Window (Alt+F4)")
                    last_action_time = current_time
                    fist_frames = 0
            else:
                fist_frames = 0

            # ----------------------------------------------------------
            # ACTION 4: OPEN APP (Open Palm - Requires 1s Hold + Visual Bar)
            # ----------------------------------------------------------
            if extended_count == 4 and pinch_index > 50 and not is_dragging:
                if open_palm_start is None:
                    open_palm_start = current_time
                
                elapsed = current_time - open_palm_start
                # Render progress bar on screen
                progress_w = int((elapsed / PALM_HOLD_DURATION) * 200)
                cv2.rectangle(frame, (10, 440), (210, 460), (100, 100, 100), 2)
                cv2.rectangle(frame, (10, 440), (10 + min(progress_w, 200), 460), (0, 255, 0), -1)
                cv2.putText(frame, "Hold Palm to Open App", (10, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                if elapsed >= PALM_HOLD_DURATION and (current_time - last_action_time > ACTION_COOLDOWN + 1.0):
                    subprocess.Popen(["calc.exe"])
                    print("[Action] Opened Application")
                    last_action_time = current_time
                    open_palm_start = None
            else:
                open_palm_start = None

    cv2.imshow("Mobile Camera Windows Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()