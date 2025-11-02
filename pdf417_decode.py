import cv2
import numpy as np
import subprocess
import os

# Paths to required files
javase_jar = "javase-3.5.0.jar"
core_jar = "core-3.5.0.jar"
jcommander_jar = "jcommander-1.82.jar"

barcode_image = "id.png"

# Validate required files
for file in [javase_jar, core_jar, jcommander_jar, barcode_image]:
    if not os.path.exists(file):
        print(f"Error: {file} not found!")
        exit(1)

# Docker command to detect the barcode and get its position
docker_command = [
    "docker", "run", "--rm",
    "-v", f"{os.getcwd()}:/app",
    "openjdk:17",
    "java", "-cp",
    f"/app/{javase_jar}:/app/{core_jar}:/app/{jcommander_jar}",
    "com.google.zxing.client.j2se.CommandLineRunner",
    f"/app/{barcode_image}"
]

try:
    # Run the Docker command to get the decoding and position
    result = subprocess.run(docker_command, capture_output=True, text=True, check=True)
    output = result.stdout.strip()
    print("Decoded Output:")
    print(output)
except subprocess.CalledProcessError as e:
    print("Error during decoding:")
    print(e.stderr)
    exit(1)

# Parse the ZXing output for barcode position
points = []
for line in output.splitlines():
    if line.startswith("  Point"):
        parts = line.split(":")[1].strip().replace("(", "").replace(")", "").split(",")
        points.append((int(float(parts[0])), int(float(parts[1]))))

# If points are found, draw a bounding box or polygon
if len(points) >= 2:
    # Load the image with OpenCV
    image = cv2.imread(barcode_image)
    if image is None:
        print("Error: Unable to read the image!")
        exit(1)

    if len(points) >= 4:
        # Draw a polygon connecting the points
        points_array = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        print(f"Drawing polygon with points: {points}")
        cv2.polylines(image, [points_array], isClosed=True, color=(0, 255, 0), thickness=2)
    else:
        # For 2 points (like UPC_A), create a bounding rectangle
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        # Add some padding for better visibility
        padding = 10
        cv2.rectangle(image, (x_min - padding, y_min - padding), 
                     (x_max + padding, y_max + padding), (0, 255, 0), 2)
        print(f"Drawing rectangle from ({x_min - padding}, {y_min - padding}) to ({x_max + padding}, {y_max + padding})")

    # Save and display the annotated image
    annotated_image_path = "annotated_barcode.png"
    cv2.imwrite(annotated_image_path, image)
    print(f"Annotated image saved as {annotated_image_path}")

    # Display the image
    cv2.imshow("Detected Barcode", image)
    print("Press any key to close the window.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No bounding box points detected.")