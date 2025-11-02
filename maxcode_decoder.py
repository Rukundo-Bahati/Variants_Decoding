"""
MaxiCode Decoder using pyzxing
MaxiCode is used primarily by UPS for package tracking and logistics
"""

import cv2
from pyzxing import BarCodeReader
import os
import numpy as np

def decode_maxicode(image_path):
    """Decode MaxiCode from image"""
    
    # Validate file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return None
    
    print("="*70)
    print("MAXICODE DECODER")
    print("="*70)
    print(f"Processing: {image_path}\n")
    
    try:
        # Initialize the barcode reader
        reader = BarCodeReader()
        
        # Load and decode the image
        results = reader.decode(image_path)
        
        if not results:
            print("❌ No MaxiCode detected!")
            print("\nTips:")
            print("  - Ensure the bull's-eye center pattern is visible")
            print("  - Check image quality and resolution")
            print("  - MaxiCode requires good contrast and lighting")
            print("  - Ensure all hexagonal modules are clear")
            return None
        
        # Filter for MaxiCode only
        maxicodes = [result for result in results if 
                    result.get('format') == 'MAXICODE' or 
                    result.get('format') == b'MAXICODE' or
                    str(result.get('format')).upper() == 'MAXICODE']
        
        if not maxicodes:
            print("❌ No MaxiCode detected!")
            print(f"Found {len(results)} other barcode(s), but no MaxiCodes")
            print("\nDetected barcode types:")
            for result in results:
                print(f"  - {result.get('format', 'Unknown')}: {result.get('parsed', 'No data')[:50]}...")
            return None
        
        print(f"✅ Found {len(maxicodes)} MaxiCode(s)\n")
        
        # Load image for annotation
        image = cv2.imread(image_path)
        decoded_data_list = []
        
        for i, maxicode in enumerate(maxicodes, 1):
            # Extract data
            maxicode_data = maxicode.get('parsed', 'No data')
            if isinstance(maxicode_data, bytes):
                maxicode_data = maxicode_data.decode('utf-8', errors='ignore')
            
            maxicode_type = maxicode.get('format', 'Unknown')
            if isinstance(maxicode_type, bytes):
                maxicode_type = maxicode_type.decode('utf-8', errors='ignore')
            
            decoded_data_list.append(maxicode_data)
            
            # Print details
            print(f"📦 MaxiCode #{i}")
            print(f"   Data: {maxicode_data}")
            print(f"   Type: {maxicode_type}")
            print(f"   Data Length: {len(maxicode_data)} characters")
            
            # Parse structured data (UPS format)
            if len(maxicode_data) > 20:
                print(f"\n   📊 MaxiCode Structure:")
                print(f"      Raw Data: {maxicode_data[:50]}...")
                # MaxiCode often contains structured shipping data
                print(f"      (Shipping/Tracking Information)")
            
            print("-" * 70)
            
            # Get bounding box if available
            points = maxicode.get('points')
            if points and len(points) >= 4:
                try:
                    # Handle different point formats
                    if isinstance(points[0], dict):
                        pts = np.array([[int(p['x']), int(p['y'])] for p in points], np.int32)
                    elif isinstance(points[0], (list, tuple)) and len(points[0]) == 2:
                        pts = np.array([[int(p[0]), int(p[1])] for p in points], np.int32)
                    else:
                        # Fallback: draw a simple rectangle in center
                        h, w = image.shape[:2]
                        pts = np.array([[w//4, h//4], [3*w//4, h//4], [3*w//4, 3*h//4], [w//4, 3*h//4]], np.int32)
                    
                    pts = pts.reshape((-1, 1, 2))
                    
                    # Draw polygon outline
                    cv2.polylines(image, [pts], True, (0, 255, 0), 3)
                    
                    # Calculate bounding rectangle for label
                    x, y, w, h = cv2.boundingRect(pts)
                    
                    # Add text label
                    label = f"MAXICODE-{i}"
                    cv2.putText(image, label, (x, y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                except Exception as e:
                    print(f"   Warning: Could not draw bounding box: {e}")
                    # Just add a label in the corner
                    label = f"MAXICODE-{i}"
                    cv2.putText(image, label, (50, 50 + i*30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Save annotated image
        output_path = "maxicode_decoded.png"
        cv2.imwrite(output_path, image)
        print(f"\n💾 Annotated image saved: {output_path}")
        
        # Display
        cv2.imshow("MaxiCode Detection", image)
        print("\n👁️  Press any key to close the window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return decoded_data_list
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Change this to your image path
    image_file = "maxicode.png"
    
    # Decode the MaxiCode
    results = decode_maxicode(image_file)
    
    if results:
        print("\n" + "="*70)
        print("SUMMARY - ALL DECODED DATA")
        print("="*70)
        for i, data in enumerate(results, 1):
            print(f"{i}. {data}")