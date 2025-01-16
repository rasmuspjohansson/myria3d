import argparse
import laspy
import numpy as np
from pyproj import CRS

# Function to read a .laz file and extract point data
def read_laz_file(laz_input):
    # Open the .laz file
    las = laspy.read(laz_input)

    # Create a dictionary to store the extracted data
    data = {
        'points': [],
        'rgb': [],
        'infrared': []
    }

    # Extract x, y, z coordinates
    points = np.vstack((las.x, las.y, las.z)).T
    data['points'] = points.tolist()

    # Extract RGB values if they exist
    if hasattr(las, 'red') and hasattr(las, 'green') and hasattr(las, 'blue'):
        rgb = np.vstack((las.red, las.green, las.blue)).T
        data['rgb'] = rgb.tolist()

    # Extract infrared values if they exist
    if hasattr(las, 'nir'):
        infrared = las.nir
        data['infrared'] = infrared.tolist()
    else:
        print("#####no infrared!###########")


    # Extract infrared values if they exist
    if hasattr(las, 'confidence'):
        input("input has confidence!!!!!!")
        confidence = las.confidence
        data['confidence'] = confidence.tolist()
    else:
        print("#####no confidence!###########")

    # Extract classification values
    classification = las.classification
    data['classification'] = classification.tolist()

    return data

# Function to write a .laz file with the provided point cloud data
def create_laz_file(laz_file_path, values, epsg_value, point_format=8, version="1.4", include_confidence=False):
    """
    Create a .laz file with the given values and configuration.
    :param laz_file_path: Path to save the .laz file.
    :param values: Dictionary containing the point cloud properties.
    :param epsg_value: EPSG code for the CRS.
    :param point_format: Point format for the LAS file.
    :param version: LAS version for the file.
    :param include_confidence: Whether to include Confidence values.
    """
    # Create a Laspy header
    header = laspy.LasHeader(point_format=point_format, version=version)
    header.offsets = [0, 0, 0]
    header.scales = [0.01, 0.01, 0.01]

    # Set CRS using pyproj
    crs = CRS.from_epsg(epsg_value)
    header.add_crs(crs)

    # Add confidence as an extra dimension if required
    if include_confidence:
        header.add_extra_dim(
            laspy.ExtraBytesParams(name="confidence", type=np.uint8, description="Confidence levels")
        )


    # Create a Laspy file with the provided values
    las = laspy.LasData(header)
    las.x = np.array([point[0] for point in values["points"]])
    las.y = np.array([point[1] for point in values["points"]])
    las.z = np.array([point[2] for point in values["points"]])
    
    if "rgb" in values:
        las.red = np.array([rgb[0] for rgb in values["rgb"]])
        las.green = np.array([rgb[1] for rgb in values["rgb"]])
        las.blue = np.array([rgb[2] for rgb in values["rgb"]])


    if include_confidence:
        las.confidence = np.array(values["confidence"])

    # Include optional properties
    if "infrared" in values and len(values["infrared"])>0:
        print(values["infrared"])
        las.nir = np.array(values["infrared"])
        print(np.array(values["infrared"]))
        print("writing infrared values to new .laz")

    if "confidence" in values:
        print("overwritign the classification values with the confidence vlaues")
        las.classification = np.array(values["confidence"])
    else:
        las.classification = np.array(values["classification"])


    # Write the .laz file with compression
    las.write(laz_file_path, do_compress=True)
    print(f"Point cloud successfully written to {laz_file_path}")

def main():
    # Argument parser for input and output .laz file paths
    parser = argparse.ArgumentParser(description="Process and write .laz files")
    parser.add_argument('--input_laz', type=str, required=True, help="Path to the input .laz file")
    parser.add_argument('--output_laz', type=str, required=True, help="Path to save the output .laz file")
    parser.add_argument("--epsg", type=int, default=7416, help="EPSG code for the CRS (default: 7416).")
    args = parser.parse_args()

    # Read data from the input .laz file
    values = read_laz_file(args.input_laz)

    # Create the output .laz file using the read data
    create_laz_file(args.output_laz, values, epsg_value=args.epsg)

if __name__ == '__main__':
    main()
