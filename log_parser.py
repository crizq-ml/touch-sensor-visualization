import sys
import re

def parse_motion_event(line):
    """
    Parses a single log line to extract MotionEvent key-value pairs.
    It returns a dictionary containing the extracted values.
    """
    # Regex to capture the MotionEvent block and then the key-value pairs within it.
    # It looks for: key=value, key[index]=value, or key=VALUE (with no index)
    # The first group captures the entire MotionEvent block.
    motion_event_match = re.search(r'MotionEvent \{ (.*) \}', line)

    if not motion_event_match:
        return None, None # Not a relevant line

    # Extract the metadata before the MotionEvent block
    try:
        # e.g., "12-04 11:11:12.680 1258 2013 D MicroXrInputService: #inputFilter - filterInputEvent: "
        parts = line.split(':', 1)
        if len(parts) > 1:
            header_parts = parts[0].split()
            timestamp = f"{header_parts[0]} {header_parts[1]}"
        else:
            timestamp = "N/A"
    except IndexError:
        timestamp = "N/A"

    data_string = motion_event_match.group(1)
    # Regex for key-value pairs. It handles:
    # 1. key=value (e.g., action=ACTION_MOVE)
    # 2. key[index]=value (e.g., x[0]=635.0)
    # 3. key[index]=value,key[index]=value, ... (multiple pointer data)
    kv_pairs = re.findall(r'(\w+)(?:\[(\d+)\])?=(.+?)(?:, |$)', data_string)

    event_data = {'timestamp': timestamp}
    pointer_data = {} # To hold x[0], y[0], etc.

    for key, index, value in kv_pairs:
        # Clean up the value by removing trailing commas and whitespace
        value = value.strip().rstrip(',')

        if index:
            # Handle indexed values (like x[0], y[1])
            if key not in pointer_data:
                pointer_data[key] = {}
            pointer_data[key][int(index)] = value
        else:
            # Handle non-indexed values (like action, pointerCount, eventTime)
            event_data[key] = value

    # Flatten pointer data into the main dict for simple output
    # This assumes consistent indices across x, y, toolType, etc.
    if pointer_data:
        max_pointers = max(len(d) for d in pointer_data.values()) if pointer_data else 0
        
        for i in range(max_pointers):
            for key, values in pointer_data.items():
                if i in values:
                    event_data[f"{key}_{i}"] = values[i]

    return event_data, motion_event_match.group(0)

def main():
    """
    Reads from standard input in real-time and processes log lines.
    """
    print("📋 Starting real-time log parser. Pipe your log data into this script.")
    print("Press Ctrl+C to stop.")
    
    # Process lines as they come in from standard input
    for line in sys.stdin:
        # Check for and skip separator lines like '--------- beginning of main'
        if line.strip().startswith('---'):
            print("\n" + "="*50)
            print("Skipping Log Section Separator")
            print("="*50 + "\n")
            continue

        extracted_data, original_event_block = parse_motion_event(line)

        if extracted_data:
            print("\n✨ Event Parsed Successfully:")
            print(f"  Timestamp: {extracted_data.get('timestamp')}")
            # Display all extracted key-value pairs (now stored as variables in the dict)
            for key, value in extracted_data.items():
                if key != 'timestamp': # Already printed timestamp
                    print(f"  - **{key}**: {value}")

            # Example of how you might use a specific 'variable' (key)
            action = extracted_data.get('action', 'N/A')
            x_coord_0 = extracted_data.get('x_0', 'N/A')

            print(f"\n[SUMMARY] Action: {action}, X-Coordinate (Pointer 0): {x_coord_0}")
            print("-" * 30)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nParser stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)