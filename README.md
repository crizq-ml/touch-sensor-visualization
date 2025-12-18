# 👆 Nexus Touch Analytics

A high-performance, real-time visualization suite for Android MotionEvents. This tool parses raw logs from the Infineon touch chip and renders multi-touch coordinate paths with temporal fading and coordinate-based gradients.



## ✨ Features
* **Real-Time Playback:** Re-watch movements at their original capture speed using the "Play" button.
* **Dual-Touch Tracking:** Supports simultaneous plotting for Pointer 0 (Purple) and Pointer 1 (Green).
* **Seek & Inspect:** A timeline slider allows you to scrub back through history. Moving the slider automatically switches the app from "Live" to "Inspect" mode.
* **Smart Filenaming:** CSVs and PNGs are automatically suggested with filenames based on the exact start time of the session.
* **Syntax Highlighting:** Raw logs in the terminal are color-coded (Purple for `x[0]`, Green for `x[1]`, Blue for `action`) for instant debugging.

## 🛠 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/crizq-ml/touch-sensor-visualization.git
cd touch-sensor-visualization
```

2. **Install Dependencies:**
Use the provided requirements file to install all necessary libraries (`matplotlib`, `seaborn`, `pandas`, and `numpy`).
```bash
pip install -r requirements.txt
```

## 🚀 Usage (Two-Terminal Workflow)

For the best real-time experience on Windows, run data collection and visualization in separate terminals to avoid ADB pipe buffering issues.

### Terminal 1: Data Collection
Connect your device and stream sensor logs to a local file:
```bash
adb logcat -c && adb logcat -v brief -s MicroXRInputService:* > live_data.txt
```

### Terminal 2: Visualization
Run the Python suite:
```bash
python log_parser.py
```

## ⚙️ Configuration
* **X/Y MAX:** Adjust coordinates (default 1600x306) in the top bar to scale the plot grid instantly.
* **▶ PLAY / ⏸ PAUSE:** Replay the current session in real-time.
* **📁 EXPORT CSV / 📷 SAVE PNG:** Saves session data with a default timestamped filename (e.g., `TouchLog_20251218-145127.csv`).

## ❓ Troubleshooting
**Graph isn't updating:**
Ensure the slider is pushed to the far right. If you move it back to look at history, the "Live" follow mode is disabled. To re-enable it, simply slide back to the end or click the CLEAR button.
**Permission Error**
Do not worry about this error, it just happens because the adb logcat in the other terminal locks the txt file so the python script can't modify it.