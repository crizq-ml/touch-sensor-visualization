# touch-sensor-visualization
> [!NOTE]
> This repository contains a simple visualization of the touch sensor values from the infineon chip, collected using the adb command. 

Can be run two different ways:
1. Interpreting data previously collected & stored in a log file 

    ``cat input_log.txt | python log_parser.py``

2. Run real time using a connected device & adb logcat

    ``adb logcat ... | python log_parser.py``