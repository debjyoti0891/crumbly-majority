import sys
import re
import json
import time

def count_labels(filename):
    label_counts = {}

    with open(filename, 'r') as file:
        lines = file.readlines()

    label_pattern = r'label\s*=\s*"([^"]+)"'

    for line in lines:
        match = re.search(label_pattern, line)
        if match:
            label = match.group(1).strip()
            if ':' in label:
              label = label[:label.find(':')].strip()
            if label in label_counts:
                label_counts[label] += 1
            else:
                label_counts[label] = 1

    return label_counts

def write_to_json(output_filename, label_counts, n, k):
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')

    data = {
        'n': n,
        'k': k,
        'timestamp': current_time,
    }
    data = data | label_counts

    try:
        with open(output_filename, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    existing_data.append(data)

    with open(output_filename, 'w') as file:
        json.dump(existing_data, file, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python count_labels.py <filename> <n> <k> output_file.json")
        sys.exit(1)

    filename = sys.argv[1]
    n = sys.argv[2]
    k = sys.argv[3]

    try:
        n = int(n)
        k = int(k)
    except ValueError:
        print("<n> and <k> must be integers")
        sys.exit(1)

    label_counts = count_labels(filename)
    write_to_json(sys.argv[4], label_counts, n, k)

    print(f"Label counts written to output.json")
