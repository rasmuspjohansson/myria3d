import argparse
import numpy as np
import laspy
from pyproj import CRS
import os

def generate_random_values(num_points=1000, include_infrared=False, include_confidence=False):
    """
    Generate random values for point cloud properties.
    :param num_points: Number of points to generate.
    :param include_infrared: Whether to include Infrared values.
    :param include_confidence: Whether to include Confidence values.
    :return: A dictionary containing the random values for x, y, z, RGB, Infrared, Classification, and Confidence.
    """
    # Generate random coordinates within a 10m² area
    x_coords = np.random.uniform(0, 10, num_points)
    y_coords = np.random.uniform(0, 10, num_points)
    z_coords = np.random.uniform(0, 5, num_points)  # Elevation values within 5 meters

    # Generate random RGB values
    red = np.random.randint(0, 256, num_points)
    green = np.random.randint(0, 256, num_points)
    blue = np.random.randint(0, 256, num_points)

    # Generate random Classification values
    classification = np.random.choice([2, 6, 9], num_points)  # Example classifications

    # Include optional values
    values = {
        "x": x_coords,
        "y": y_coords,
        "z": z_coords,
        "red": red,
        "green": green,
        "blue": blue,
        "classification": classification,
    }
    if include_infrared:
        values["infrared"] = np.random.randint(0, 256, num_points)
    if include_confidence:
        values["confidence"] = np.random.choice([2, 6, 9], num_points)

    return values

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
    las.x = values["x"]
    las.y = values["y"]
    las.z = values["z"]
    las.red = values["red"]
    las.green = values["green"]
    las.blue = values["blue"]
    las.classification = values["classification"]

    # Include optional properties
    if "infrared" in values:
        las.nir = values["infrared"]
    if "confidence" in values:
        las["confidence"] = values["confidence"]

    # Write the .laz file with compression
    las.write(laz_file_path, do_compress=True)
    print(f"Point cloud successfully written to {laz_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a synthetic point cloud and save it as a .laz file.")
    parser.add_argument("--laz_path", type=str, required=True, help="Path to save the output .laz file.")
    parser.add_argument("--epsg", type=int, default=7416, help="EPSG code for the CRS (default: 7416).")
    parser.add_argument("--num_points", type=int, default=1000, help="Number of points to generate (default: 1000).")
    parser.add_argument("--Infrared", action="store_true", help="Include Infrared channel (requires point_format=8).")
    parser.add_argument("--confidence", action="store_true", help="Include Confidence levels as an extra property.")

    args = parser.parse_args()

    # Ensure the output directory exists
    output_dir = os.path.dirname(args.laz_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Determine point format based on flags
    point_format = 8  # Using point format 8 by default to support Infrared and Classification
    include_confidence = args.confidence

    # Generate random point cloud values
    random_values = generate_random_values(
        num_points=args.num_points,
        include_infrared=args.Infrared,
        include_confidence=include_confidence,
    )

    # Create the .laz file
    create_laz_file(
        laz_file_path=args.laz_path,
        values=random_values,
        epsg_value=args.epsg,
        point_format=point_format,
        include_confidence=include_confidence,
    )
