import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# ======================================================================
# 1. SYSTEM SETTINGS
# ======================================================================
WEBCAM_INDEX = 0  # 0 for built-in webcam (try 1 if using Iriun Webcam)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.01
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Sensitivity & Boundary Settings
MARGIN = 90             # Frame margin box for corner-to-corner screen reach
SMOOTHING = 0.10        # Lower value = smoother cursor & cleaner drawing
prev_x, prev_y = 0, 0

# Gesture Pinch Thresholds (Pixel distances)
PINCH_START = 28        # Distance to START a click/drag (Index or Ring)
PINCH_RELEASE = 40      # Distance to RELEASE a click/drag
RIGHT_CLICK_DIST = 26   # Distance for Right-Click (Middle + Thumb)
FIST_DIST = 45          # Minimum distance for closed fist

# Debounce Counters & Timers
right_click_frames = 0
fist_frames = 0
last_action_time = 0
ACTION_COOLDOWN = 1.2

# Drag State Tracking
is_dragging = False
active_drag_finger = None  # Tracks which finger started the drag ('index' or 'ring')

# ======================================================================
# 2. MEDIAPIPE INITIALIZATION
# ======================================================================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)

print(f"[*] Starting Webcam (Device Index: {WEBCAM_INDEX})...")
cap = cv2.VideoCapture(WEBCAM_INDEX)

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
        print("[!] Camera frame not available. Retrying...")
        time.sleep(0.5)
        cap = cv2.VideoCapture(WEBCAM_INDEX)
        continue

    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 1)  # Mirror video feed
    h, w, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    current_time = time.time()

    # Draw region box
    cv2.rectangle(frame, (MARGIN, MARGIN), (w - MARGIN, h - MARGIN), (255, 255, 0), 2)
    cv2.putText(frame, "Laptop Webcam Air-Mouse", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            # Key positions (Fingertip landmarks)
            thumb_tip = np.array([lm[4].x * w, lm[4].y * h])
            index_tip = np.array([lm[8].x * w, lm[8].y * h])
            middle_tip = np.array([lm[12].x * w, lm[12].y * h])
            ring_tip = np.array([lm[16].x * w, lm[16].y * h]) # Ring fingertip (Landmark 16)

            # Coordinate mapping using Index Finger position
            x_mapped = np.interp(index_tip[0], [MARGIN, w - MARGIN], [0, SCREEN_WIDTH])
            y_mapped = np.interp(index_tip[1], [MARGIN, h - MARGIN], [0, SCREEN_HEIGHT])

            # Exponential Cursor Smoothing
            curr_x = prev_x + (x_mapped - prev_x) * SMOOTHING
            curr_y = prev_y + (y_mapped - prev_y) * SMOOTHING
            prev_x, prev_y = curr_x, curr_y

            # Move cursor continuously
            pyautogui.moveTo(curr_x, curr_y)

            extended_count = count_extended_fingers(lm)
            
            # Distance calculations
            pinch_index = np.linalg.norm(index_tip - thumb_tip)
            pinch_middle = np.linalg.norm(middle_tip - thumb_tip)
            pinch_ring = np.linalg.norm(ring_tip - thumb_tip)

            # ----------------------------------------------------------
            # ACTION 1 & 2: LEFT CLICK/DRAW (Index) & DRAG/DROP (Ring)
            # ----------------------------------------------------------
            if not is_dragging:
                # Prioritize Index Pinch (Left Click / Draw)
                if pinch_index < PINCH_START:
                    pyautogui.mouseDown()
                    is_dragging = True
                    active_drag_finger = 'index'
                    print("[Action] Left Click / Drawing Started (Index Pinch)")
                
                # Check Ring Pinch (Drag and Drop)
                elif pinch_ring < PINCH_START:
                    pyautogui.mouseDown()
                    is_dragging = True
                    active_drag_finger = 'ring'
                    print("[Action] Drag & Drop Started (Ring Pinch)")

            else:
                # If we are currently holding the mouse down, check for release 
                # based on the specific finger that started the action.
                if active_drag_finger == 'index':
                    cv2.putText(frame, "LEFT CLICK / DRAWING", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    if pinch_index > PINCH_RELEASE:
                        pyautogui.mouseUp()
                        is_dragging = False
                        active_drag_finger = None
                        print("[Action] Left Click / Drawing Released")
                
                elif active_drag_finger == 'ring':
                    cv2.putText(frame, "DRAGGING & DROPPING", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    if pinch_ring > PINCH_RELEASE:
                        pyautogui.mouseUp()
                        is_dragging = False
                        active_drag_finger = None
                        print("[Action] Drag & Drop Released")

            # ----------------------------------------------------------
            # ACTION 3: RIGHT CLICK (Middle + Thumb)
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
            # ACTION 4: CLOSE WINDOW (Fist Gesture)
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

    cv2.imshow("Laptop Webcam Windows Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
#code credited by KR