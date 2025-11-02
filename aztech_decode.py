"""
Aztec Code Decoder using pyzxing
Aztec codes are 2D barcodes used in transport, ticketing, and identification
"""

import cv2
from pyzxing import BarCodeReader
import os
import numpy as np

def decode_aztec_code(image_path):
    """Decode Aztec code from image"""
    
    # Validate file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return None
    
    print("="*70)
    print("AZTEC CODE DECODER")
    print("="*70)
    print(f"Processing: {image_path}\n")
    
    try:
        # Initialize the barcode reader
        reader = BarCodeReader()
        
        # Load and decode the image
        results = reader.decode(image_path)
        
        if not results:
            print("❌ No Aztec code detected!")
            print("\nTips:")
            print("  - Ensure the bulls-eye center is clearly visible")
            print("  - Check if the image has good contrast")
            print("  - Try improving image quality/resolution")
            print("  - Ensure proper lighting and focus")
            return None
        
        # Filter for Aztec codes only
        aztec_codes = [result for result in results if 
                      result.get('format') == 'AZTEC' or 
                      result.get('format') == b'AZTEC' or
                      str(result.get('format')).upper() == 'AZTEC']
        
        if not aztec_codes:
            print("❌ No Aztec code detected!")
            print(f"Found {len(results)} other barcode(s), but no Aztec codes")
            print("\nDetected barcode types:")
            for result in results:
                print(f"  - {result.get('format', 'Unknown')}: {result.get('parsed', 'No data')[:50]}...")
            return None
        
        print(f"✅ Found {len(aztec_codes)} Aztec code(s)\n")
        
        # Load image for annotation
        image = cv2.imread(image_path)
        decoded_data_list = []
        
        for i, aztec in enumerate(aztec_codes, 1):
            # Extract data
            aztec_data = aztec.get('parsed', 'No data')
            if isinstance(aztec_data, bytes):
                aztec_data = aztec_data.decode('utf-8', errors='ignore')
            
            aztec_type = aztec.get('format', 'Unknown')
            if isinstance(aztec_type, bytes):
                aztec_type = aztec_type.decode('utf-8', errors='ignore')
            
            decoded_data_list.append(aztec_data)
            
            # Print details
            print(f"🎯 Aztec Code #{i}")
            print(f"   Data: {aztec_data}")
            print(f"   Type: {aztec_type}")
            print(f"   Data Length: {len(aztec_data)} characters")
            
            # Detect content type
            if aztec_data.startswith('http://') or aztec_data.startswith('https://'):
                print(f"   Content Type: 🌐 URL")
            elif '@' in aztec_data and '.' in aztec_data:
                print(f"   Content Type: 📧 Email/Contact")
            elif aztec_data.isdigit():
                print(f"   Content Type: 🔢 Numeric ID")
            else:
                print(f"   Content Type: 📝 Text/Data")
            
            print("-" * 70)
            
            # Get bounding box if available
            points = aztec.get('points')
            if points and len(points) >= 4:
                # Convert points to numpy array
                pts = np.array([[int(p['x']), int(p['y'])] for p in points], np.int32)
                pts = pts.reshape((-1, 1, 2))
                
                # Draw polygon outline
                cv2.polylines(image, [pts], True, (0, 255, 0), 3)
                
                # Calculate bounding rectangle for label
                x, y, w, h = cv2.boundingRect(pts)
                
                # Add text label
                label = f"AZTEC-{i}"
                cv2.putText(image, label, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Save annotated image
        output_path = "aztec_code_decoded.png"
        cv2.imwrite(output_path, image)
        print(f"\n💾 Annotated image saved: {output_path}")
        
        # Display
        cv2.imshow("Aztec Code Detection", image)
        print("\n👁️  Press any key to close the window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return decoded_data_list
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Change this to your image path
    image_file = "aztech.png"
    
    # Decode the Aztec code
    results = decode_aztec_code(image_file)
    
    if results:
        print("\n" + "="*70)
        print("SUMMARY - ALL DECODED DATA")
        print("="*70)
        for i, data in enumerate(results, 1):
            print(f"{i}. {data}")