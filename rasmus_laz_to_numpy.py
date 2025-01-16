import argparse
import laspy
import numpy as np

def read_laz_file(laz_input):
    # Open the .laz file
    las = laspy.read(laz_input)
    
    # Create a dictionary to store the extracted data
    data = {
        'points': [],
        'rgb': [],
        'infrared': [],
        'classification': []
    }
    
    # Extract x, y, z coordinates
    points = np.vstack((las.x, las.y, las.z)).T
    data['points'] = points.tolist()
    
    # Extract RGB values if they exist
    if hasattr(las, 'red') and hasattr(las, 'green') and hasattr(las, 'blue'):
        rgb = np.vstack((las.red, las.green, las.blue)).T
        data['rgb'] = rgb.tolist()
    
    # Extract infrared values if they exist
    if hasattr(las, 'infrared'):
        infrared = las.infrared
        data['infrared'] = infrared.tolist()

    # Extract classification values
    classification = las.classification
    data['classification'] = classification.tolist()
    
    return data

def main():
    # Argument parser for the laz_input file
    parser = argparse.ArgumentParser(description="Read and process a .laz file")
    parser.add_argument('--laz_input', type=str, required=True, help="Path to the .laz input file")
    args = parser.parse_args()

    # Read the .laz file and get the data
    data = read_laz_file(args.laz_input)

    # Print the data dictionary
    print("Extracted Data:")
    print(data)

if __name__ == '__main__':
    main()
