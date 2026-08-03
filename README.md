# 👆 AirTouch Menu — Interactive Touchless Kiosk Interface

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
- 🤏 **Select Area / Drag:** Pinch index finger and thumb, then move across screen.
- 🖕 **Right Click:** Pinch middle finger and thumb together.
- ✊ **Close Active Window:** Close hand into a fist (`Alt + F4`).
- 🖐️ **Launch Application:** Show open palm to launch configured app (Notepad/Browser).

---
