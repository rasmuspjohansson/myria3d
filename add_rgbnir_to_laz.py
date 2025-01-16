import argparse
import json
import subprocess
import os

def run_pdal_pipeline(laz_file, raster, output_laz):
    """
    Function to add RGB and Infrared data to LiDAR point cloud using PDAL.
    """
    pipeline = {
        "pipeline": [
            {
                "type": "readers.las",
                "filename": laz_file,
                "override_srs": "EPSG:25832"
            },
            {
                "type": "filters.colorization",
                "raster": raster,
                "dimensions": "Red:1:1.0, Green:2:1.0, Blue:3:1.0, Infrared:4:1.0"
            },
            {
                "type": "filters.reprojection",
                "in_srs": "EPSG:25832",
                "out_srs": "EPSG:7416"
            },
            {
                "type": "writers.las",
                "filename": output_laz,
                "minor_version": 4,
                "dataformat_id": 8
            }
        ]
    }

    # Save the pipeline to a temporary JSON file
    pipeline_file = "pipeline.json"
    with open(pipeline_file, "w") as f:
        json.dump(pipeline, f, indent=4)

    try:
        # Run the PDAL pipeline
        subprocess.run(["pdal", "pipeline", pipeline_file], check=True)
        print(f"Processing completed. Output saved to {output_laz}")
    except subprocess.CalledProcessError as e:
        print("Error running PDAL pipeline:", e)
    finally:
        # Clean up the temporary pipeline file
        if os.path.exists(pipeline_file):
            os.remove(pipeline_file)


def main():
    parser = argparse.ArgumentParser(description="Add RGB and Infrared data to LiDAR point cloud using PDAL.")
    parser.add_argument("--laz_file", required=True, help="Path to the input LAZ file.")
    parser.add_argument("--raster", required=True, help="Path to the raster file.")
    parser.add_argument("--output_laz", required=True, help="Path to save the output LAZ file.")

    args = parser.parse_args()

    run_pdal_pipeline(args.laz_file, args.raster, args.output_laz)

if __name__ == "__main__":
    main()
