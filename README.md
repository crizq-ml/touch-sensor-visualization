# 👆 Nexus Touch Analytics

A high-performance, real-time visualization suite for Android MotionEvents. This tool parses raw logs from the Infineon touch chip and renders multi-touch coordinate paths with temporal fading and coordinate-based gradients.

The app can operate real time or using saved data.

> [!TIP]
> **Newest feature includes a dashboard to launch the plotting GUI and data collection from one panel!**
> 
> To run this feature, see "Installation (post-shortcut)" below 


## ✨ Features
* **Real-Time Playback:** Re-watch movements at their original capture speed using the "Play" button.
* **Dual-Touch Tracking:** Supports simultaneous plotting for Pointer 0 (Purple) and Pointer 1 (Green).
* **Seek & Inspect:** A timeline slider allows you to scrub back through history. Moving the slider automatically switches the app from "Live" to "Inspect" mode.
* **Smart Filenaming:** CSVs and PNGs are automatically suggested with filenames based on the exact start time of the session.
* **Syntax Highlighting:** Raw logs in the terminal are color-coded (Purple for `x[0]`, Green for `x[1]`, Blue for `action`) for instant debugging.

## 🛠 Installation (post-shortcut)

1. **Download the folder** from https://github.com/crizq-ml/touch-sensor-visualization.git

2. **Unzip the file**

3. **Open the file called controller.ps1 & copy its contents**

4. **Create a new file in the same folder called mycontroller.ps1 and paste the contents there**

5. **Run the controller1.ps1 using powershell by:**
    a. opening a terminal within the downloaded folder & running `./mycontroller.ps1`
    b. right click `mycontroller.ps1` and select `run using Windows Powershell`

    > [!WARNING]
    > DO NOT RUN controller.ps1 it will cause a CORTEX XDR ALERT
    > This is because github is not a "trusted" source & that is how we are sharing this program, I am working with IT to resolve this issue

** If you would like:**
You can create a shortcut that runs the controller app

1. **Right click on `mycontroller.ps1` & select Create shortcut**

2. **Right click `mycontroller - Shortcut` & select properties**

3. **Change the target to include `%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe -WindowStyle hidden -ExecutionPolicy Bypass -File ` before the filename**
    
    eg: `C:\Users\lab\Downloads\touch-sensor-visualization-main\mycontroller.ps1` 
    
    turns into 
    
    `%SystemRoot%\system32\WindowsPowerShell\v1.0\powershell.exe -WindowStyle hidden -ExecutionPolicy Bypass -File "C:\Users\lab\Downloads\touch-sensor-visualization-main\mycontroller.ps1"`

4. **Double click on the shortcut called "Controller App"**

## 🛠 Installation (pre-shortcut)

1. **Clone the repository:**
```bash
git clone https://github.com/crizq-ml/touch-sensor-visualization.git
cd touch-sensor-visualization
```

2. **Install Dependencies:**
Use the provided requirements file to install all necessary libraries (`matplotlib`, `seaborn`, `pandas`, and `numpy`).
```bash
py -m pip install -r requirements.txt
```

## 🚀 Usage

### Real-time data logging
For the best real-time experience on Windows, run data collection and visualization in separate terminals to avoid ADB pipe buffering issues.

#### Terminal 1: Data Collection
Connect your device and stream sensor logs to a local file:
```bash
adb logcat -s MicroXrInputService:* > live_data.txt
```

#### Terminal 2: Visualization
Run the Python suite:
```bash
$env:PYTHONUNBUFFERED=1; py .\log_parser.py
```

> [!WARNING]
> Make sure that both terminals are executed from the same file path OR that the file the data is saved to in terminal one is in the same path as the python visualization file

### Data visualization from a logfile
This is a one terminal operation, all that is needed is pre-recorded data in a .txt file 

### Pre-recorded data requirements
Collect data using `adb logcat -s MicroXrInputService:*`
Store it into a .txt file
Save said text file in the **same** location as the visualizer

### How to run the script
Open a terminal and run `cat your_file_name.txt | ./log_parser.py`

> [!NOTE]
> Make sure that the terminal is executed from the same file path OR that the file the data is saved to AND the file you are calling in the terminal is in the same path as the python visualization file 


## ⚙️ Configuration
* **X/Y MAX:** Adjust coordinates (default 1600x306) in the top bar to scale the plot grid instantly.
* **▶ PLAY / ⏸ PAUSE:** Replay the current session in real-time.
* **📁 EXPORT CSV / 📷 SAVE PNG:** Saves session data with a default timestamped filename (e.g., `TouchLog_20251218-145127.csv`).

## ❓ Troubleshooting
**Graph isn't updating:**
Ensure the slider is pushed to the far right. If you move it back to look at history, the "Live" follow mode is disabled. To re-enable it, simply slide back to the end or click the CLEAR button.
**Permission Error**
Do not worry about this error, it just happens because the adb logcat in the other terminal locks the txt file so the python script can't modify it.
**Crashing error**
You must close the app using Ctrl + C in the terminal used to open the python app rather than using the lose button in the top right. If you do not, the terminal will freeze. If this happens, just delete the terminal and open a new one.
