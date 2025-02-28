import re
import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Set the UPLOAD_FOLDER and OUTPUT_FOLDER in app.config
app.config['UPLOAD_FOLDER'] = os.path.join('docs', 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join('docs', 'output')

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'stl'}

def extract_gcode_data(gcode_path):
    # Read the gcode file content in binary mode
    with open(gcode_path, 'rb') as file:
        gcode_content = file.read()

    # Decode the content to a string while ignoring errors
    gcode_content = gcode_content.decode(errors='ignore')

    # Define the regular expressions for extracting data
    patterns = {
        "filament_used_mm": r"filament used \[mm\]=([0-9.]+)",
        "filament_used_g": r"filament used \[g\]=([0-9.]+)",
        "filament_cost": r"filament cost=([0-9.]+)",
        "filament_used_cm3": r"filament used \[cm3\]=([0-9.]+)",
        "total_filament_used_wipe_tower_g": r"total filament used for wipe tower \[g\]=([0-9.]+)",
        "estimated_printing_time": r"estimated printing time \(normal mode\)=([0-9m\s0-9s]+)",
        "filament_type": r"filament_type=([A-Za-z0-9_]+)"  # Added regex to capture filament type
    }

    extracted_data = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, gcode_content)
        if match:
            value = match.group(1)
            value = value.strip()
            extracted_data[key] = value
        else:
            extracted_data[key] = None

    return extracted_data

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # If no file is selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # If the file type is not allowed
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    
    # Generate a unique filename for the uploaded file
    filename = str(uuid.uuid4()) + '.stl'
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Save the file
    file.save(input_path)

    # Generate a unique G-code output filename
    output_filename = str(uuid.uuid4()) + '.gcode'
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    # Run PrusaSlicer using subprocess with the correct path for Windows
    try:
        # Command to run PrusaSlicer for Windows (use correct path)
        subprocess.run([
            "flatpak", "run", "com.prusa3d.PrusaSlicer",
            "--load", "config.ini",  # Configuration file path (if necessary)
            "--output", output_path,
            "--export-gcode",
            input_path
        ], check=True)

        # Return the G-code file path as a response
        gcode_data = extract_gcode_data(output_path)
        return jsonify(gcode_data), 200
    
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"PrusaSlicer failed: {str(e)}"}), 500

        # Extract the data from the generated G-code file
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)