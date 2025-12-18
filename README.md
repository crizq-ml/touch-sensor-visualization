# 👆 Nexus Touch Analytics

A high-performance, real-time visualization suite for Android MotionEvents. This tool parses raw logs from the Infineon touch chip and renders multi-touch coordinate paths with temporal fading and coordinate-based gradients.

## ✨ Features
* **Dual-Touch Tracking:** Supports simultaneous plotting for Pointer 0 (Purple) and Pointer 1 (Green).
* **Temporal Fading:** Older touch points fade out automatically, providing a clear "trail" of motion.
* **Adjustable Interface:** Features a draggable vertical divider (PanedWindow) to resize the graph and terminal areas on the fly.
* **Syntax Highlighting:** A "Rainbow Terminal" that color-codes every variable in the live log stream for instant readability.
* **Responsive Pro UI:** Modern "Soft Card" aesthetic with rounded corners, large high-contrast input fields, and smooth hover effects.

## 🛠 Installation

1. **Install Dependencies:**
   ```bash
   git clone [https://github.com/crizq-ml/touch-sensor-visualization.git](https://github.com/crizq-ml/touch-sensor-visualization.git)
   cd touch-sensor-visualization
   ```
2. **Clone the repository:**
   ```bash
   pip install -r requirements.txt
   ```
    *(Required libraries: `matplotlib`, `seaborn`, `pandas`, and `numpy`)*

## 🚀 Usage

### 1. Interpreting Stored Logs
To visualize data previously collected and stored in a `.txt` file:
```bash
cat input_log.txt | python log_parser.py
```

### 2. Real-Time Visualization (ADB)
To run live using a connected Android device.

> [!IMPORTANT]
> We use the -u flag to force Python into unbuffered mode. Without this, the GUI may hang or data may appear in delayed "bursts" due to ADB's internal piping buffers.

```bash
adb logcat -s MicroXRInputService:* | python -u log_parser.py
```

## ⚙️ Configuration
* **X/Y MAX:** Adjust the entry fields in the top bar to match the resolution of your touch sensor (defaults to 1600x306). The plot axis scales instantly as you change these values.
* **🗑️ Clear:** Flushes all stored event data and wipes the terminal screen.
* **📁 Export CSV:** Saves all collected touch data into a structured CSV for external analysis.
* **📷 Save PNG:** Captures a high-resolution snapshot of the current plot.

## ❓ Troubleshooting
**GUI is not opening / Data is "stuck":**
This is typically caused by ADB "Block Buffering." If the data isn't moving, clear the log buffer and force a brief format:
```bash
adb logcat -c && adb logcat -v brief -s MicroXRInputService:* | python -u log_parser.py
```
