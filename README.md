# 👆 AirTouch Menu — Interactive Touchless Menu

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Hands-orange.svg)](https://google.github.io/mediapipe/)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

> A touchless, computer-vision-based kiosk menu system built using Python, OpenCV, and Google MediaPipe. Designed to reduce surface-borne cross-contamination in public environments such as restaurants, airports, and ATMs.

---

## 📸 Key Features

* 🎯 **Air-Cursor Tracking:** Real-time 21-point hand-landmark tracking mapped to screen coordinates using standard RGB webcams.
* ⏱️ **Dwell-Time Clicking:** Hover over menu items for a customizable duration (e.g., 1.2s) to trigger seamless "touchless" selections.
* 🤌 **Pinch Gesture Support:** Instant selection using dynamic Index-to-Thumb pinch distance calculation.
* ⚡ **Exponential Jitter Reduction:** Built-in low-pass smoothing algorithms to prevent cursor shaky motion.
* 🛒 **Dynamic Order Cart & QR Checkout:** Real-time visual order summary with instant mock receipt feedback.

---

## 💻 OS Control Gestures

This project allows direct control of OS mouse and window management:

- ☝️ **Move Pointer:** Move index finger within active camera box boundary.
- 🤏 **Select Area / Drag:** Pinch pinky finger and thumb, then move across screen.
- 👆 **Right Click:** Pinch middle finger and thumb together.
- 🤏 **Left Click** Pinch index and thumb finger together.
- ✊ **Close Active Window:** Close hand into a fist (`Alt + F4`).


---

## 📱 Mobile Camera as Windows Controller

This mode turns your smartphone into a wireless hand-tracking camera to control the Windows environment.

### Setup Instructions
1. Install **IP Webcam** or **DroidCam** from Google Play / App Store.
2. Connect your mobile device and Windows PC to the same Wi-Fi network.
3. Start video server on the mobile app and copy your IP URL (e.g., `http://192.168.1.5:8080/video`).
4. Update `MOBILE_CAM_URL` in `mobile_windows_controller.py`.
5. Run the controller script:
   ```bash
   python tim.py

---
