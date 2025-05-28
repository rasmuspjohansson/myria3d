#!/usr/bin/env python3
"""
LAS File Analyzer
Analyzes LAS/LAZ files and prints detailed information about point cloud data.
"""

import argparse
import sys
import os
try:
    import laspy
    import numpy as np
except ImportError as e:
    print(f"Required library not found: {e}")
    print("Please install laspy: pip install laspy")
    sys.exit(1)


def get_dims(las_file):
    """
    Get available dimensions from a LAS file or loaded LAS object.
    
    Args:
        las_file: Either a string path to LAS/LAZ file or an already loaded laspy object
        
    Returns:
        list: List of available dimension names in the LAS data
    """
    # Check if it's already a loaded LAS object or a file path
    if isinstance(las_file, str):
        # It's a file path, load it
        try:
            las = laspy.read(las_file)
        except Exception as e:
            print(f"Error loading LAS file '{las_file}': {e}")
            return []
    else:
        # It's already a loaded LAS object
        las = las_file
    
    available_dims = []
    
    # Standard dimensions
    standard_dims = ['x', 'y', 'z', 'intensity', 'return_number', 'number_of_returns',
                    'scan_direction_flag', 'edge_of_flight_line', 'classification',
                    'scan_angle_rank', 'user_data', 'point_source_id']
    
    for dim in standard_dims:
        if hasattr(las, dim):
            available_dims.append(dim)
    
    # Color information
    color_dims = ['red', 'green', 'blue']
    for dim in color_dims:
        if hasattr(las, dim):
            available_dims.append(dim)
            
    # NIR (Near Infrared)
    if hasattr(las, 'nir'):
        available_dims.append('nir')
        
    # GPS time
    if hasattr(las, 'gps_time'):
        available_dims.append('gps_time')
        
    # Wave packet data
    wave_dims = ['wave_packet_descriptor_index', 'byte_offset_to_waveform_data',
                 'waveform_packet_size', 'return_point_waveform_location']
    for dim in wave_dims:
        if hasattr(las, dim):
            available_dims.append(dim)
    
    return available_dims


def analyze_las_file(file_path):
    """
    Analyze a LAS file and print comprehensive information about its contents.
    
    Args:
        file_path (str): Path to the LAS/LAZ file
    """
    try:
        # Open the LAS file
        las = laspy.read(file_path)
        
        print(f"=== LAS File Analysis: {file_path} ===\n")
        
        # Basic file information
        print("📁 FILE INFORMATION:")
        
        # Handle different laspy versions and header attributes
        try:
            version_major = getattr(las.header, 'version_major', getattr(las.header, 'major_version', 'Unknown'))
            version_minor = getattr(las.header, 'version_minor', getattr(las.header, 'minor_version', 'Unknown'))
            print(f"   Format: LAS {version_major}.{version_minor}")
        except:
            print(f"   Format: LAS (version info unavailable)")
        
        try:
            print(f"   Point Data Format: {las.header.point_data_format}")
        except:
            print(f"   Point Data Format: {getattr(las.header, 'point_format', 'Unknown')}")
        
        print(f"   Number of Points: {len(las.points):,}")
        
        try:
            print(f"   File Size: {las.header.file_size:,} bytes")
        except:
            print(f"   File Size: Not available")
        
        # Header information
        print(f"\n📍 SPATIAL INFORMATION:")
        try:
            print(f"   X Range: {las.header.x_min:.3f} to {las.header.x_max:.3f}")
            print(f"   Y Range: {las.header.y_min:.3f} to {las.header.y_max:.3f}")
            print(f"   Z Range: {las.header.z_min:.3f} to {las.header.z_max:.3f}")
        except:
            # Fallback to calculating from point data
            print(f"   X Range: {np.min(las.x):.3f} to {np.max(las.x):.3f}")
            print(f"   Y Range: {np.min(las.y):.3f} to {np.max(las.y):.3f}")
            print(f"   Z Range: {np.min(las.z):.3f} to {np.max(las.z):.3f}")
        
        try:
            x_scale = getattr(las.header, 'x_scale', getattr(las.header, 'scale', [None])[0])
            y_scale = getattr(las.header, 'y_scale', getattr(las.header, 'scale', [None, None])[1] if len(getattr(las.header, 'scale', [])) > 1 else None)
            z_scale = getattr(las.header, 'z_scale', getattr(las.header, 'scale', [None, None, None])[2] if len(getattr(las.header, 'scale', [])) > 2 else None)
            
            if x_scale is not None:
                print(f"   Scale: X={x_scale}, Y={y_scale}, Z={z_scale}")
            
            x_offset = getattr(las.header, 'x_offset', getattr(las.header, 'offset', [None])[0])
            y_offset = getattr(las.header, 'y_offset', getattr(las.header, 'offset', [None, None])[1] if len(getattr(las.header, 'offset', [])) > 1 else None)
            z_offset = getattr(las.header, 'z_offset', getattr(las.header, 'offset', [None, None, None])[2] if len(getattr(las.header, 'offset', [])) > 2 else None)
            
            if x_offset is not None:
                print(f"   Offset: X={x_offset}, Y={y_offset}, Z={z_offset}")
        except:
            print(f"   Scale/Offset: Not available")
        
        # Use the get_dims function to get available dimensions
        available_dims = get_dims(las)
        print(f"\n📊 AVAILABLE POINT DATA:")
        print(f"   Available dimensions: {', '.join(available_dims)}")
        
        # Check for specific data types
        color_dims = ['red', 'green', 'blue']
        has_color = all(hasattr(las, dim) for dim in color_dims)
        
        wave_dims = ['wave_packet_descriptor_index', 'byte_offset_to_waveform_data',
                     'waveform_packet_size', 'return_point_waveform_location']
        has_wave = any(hasattr(las, dim) for dim in wave_dims)
        
        # Detailed statistics for each dimension
        print(f"\n📈 DETAILED STATISTICS:")
        
        def print_stats(name, data, is_integer=False):
            """Print statistics for a data array"""
            if len(data) == 0:
                return
            
            min_val = np.min(data)
            max_val = np.max(data)
            mean_val = np.mean(data)
            std_val = np.std(data)
            
            if is_integer:
                print(f"   {name:25} | Min: {min_val:>10.0f} | Max: {max_val:>10.0f} | Mean: {mean_val:>10.1f} | Std: {std_val:>8.1f}")
            else:
                print(f"   {name:25} | Min: {min_val:>10.3f} | Max: {max_val:>10.3f} | Mean: {mean_val:>10.3f} | Std: {std_val:>8.3f}")
        
        # Coordinate statistics
        print_stats("X", las.x)
        print_stats("Y", las.y)
        print_stats("Z", las.z)
        
        # Intensity
        if hasattr(las, 'intensity'):
            print_stats("Intensity", las.intensity, is_integer=True)
        
        # Return information
        if hasattr(las, 'return_number'):
            print_stats("Return Number", las.return_number, is_integer=True)
            print(f"   {'Return Distribution':<25} | " + 
                  " | ".join([f"Return {i}: {np.sum(las.return_number == i):,}" 
                            for i in np.unique(las.return_number)]))
        
        if hasattr(las, 'number_of_returns'):
            print_stats("Number of Returns", las.number_of_returns, is_integer=True)
        
        # Classification
        if hasattr(las, 'classification'):
            unique_classes = np.unique(las.classification)
            print_stats("Classification", las.classification, is_integer=True)
            
            # Classification breakdown
            class_names = {
                0: "Created/Never Classified", 1: "Unclassified", 2: "Ground",
                3: "Low Vegetation", 4: "Medium Vegetation", 5: "High Vegetation",
                6: "Building", 7: "Low Point", 8: "Reserved", 9: "Water",
                10: "Rail", 11: "Road Surface", 12: "Reserved", 13: "Wire - Guard",
                14: "Wire - Conductor", 15: "Transmission Tower", 16: "Wire Connector",
                17: "Bridge Deck", 18: "High Noise"
            }
            
            print(f"   {'Classification Breakdown':<25} |")
            for cls in unique_classes:
                count = np.sum(las.classification == cls)
                class_name = class_names.get(cls, f"User Defined ({cls})")
                print(f"   {'':<25} | Class {cls:2d}: {count:>8,} points ({class_name})")
        
        # Scan angle
        if hasattr(las, 'scan_angle_rank'):
            print_stats("Scan Angle Rank", las.scan_angle_rank, is_integer=True)
        
        # Color information
        if has_color:
            print_stats("Red", las.red, is_integer=True)
            print_stats("Green", las.green, is_integer=True)
            print_stats("Blue", las.blue, is_integer=True)
        
        # NIR
        if hasattr(las, 'nir'):
            print_stats("NIR (Near Infrared)", las.nir, is_integer=True)
        
        # GPS Time
        if hasattr(las, 'gps_time'):
            print_stats("GPS Time", las.gps_time)
        
        # Point source ID
        if hasattr(las, 'point_source_id'):
            unique_sources = np.unique(las.point_source_id)
            print_stats("Point Source ID", las.point_source_id, is_integer=True)
            if len(unique_sources) <= 20:  # Only show if reasonable number
                print(f"   {'Source IDs':<25} | {', '.join(map(str, unique_sources))}")
        
        # User data
        if hasattr(las, 'user_data'):
            print_stats("User Data", las.user_data, is_integer=True)
        
        # Summary
        print(f"\n✅ SUMMARY:")
        print(f"   • Total Points: {len(las.points):,}")
        print(f"   • Has Color Data: {'Yes' if has_color else 'No'}")
        print(f"   • Has NIR Data: {'Yes' if hasattr(las, 'nir') else 'No'}")
        print(f"   • Has GPS Time: {'Yes' if hasattr(las, 'gps_time') else 'No'}")
        print(f"   • Has Wave Data: {'Yes' if has_wave else 'No'}")
        
        try:
            point_format = getattr(las.header, 'point_data_format', getattr(las.header, 'point_format', 'Unknown'))
            print(f"   • Point Data Format: {point_format}")
        except:
            print(f"   • Point Data Format: Unknown")
        
        if hasattr(las, 'classification'):
            ground_points = np.sum(las.classification == 2)
            vegetation_points = np.sum(np.isin(las.classification, [3, 4, 5]))
            building_points = np.sum(las.classification == 6)
            
            print(f"   • Ground Points: {ground_points:,} ({ground_points/len(las.points)*100:.1f}%)")
            print(f"   • Vegetation Points: {vegetation_points:,} ({vegetation_points/len(las.points)*100:.1f}%)")
            print(f"   • Building Points: {building_points:,} ({building_points/len(las.points)*100:.1f}%)")
        
    except Exception as e:
        print(f"Error analyzing LAS file: {e}")
        return False
    
    return True


def main():
    """Main function to handle command line arguments and run the analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze LAS/LAZ files and print detailed point cloud information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python las_analyzer.py --path_to_las_file data.las
  python las_analyzer.py --path_to_las_file scan.laz
  
  # Using the get_dims function programmatically:
  from las_analyzer import get_dims
  dimensions = get_dims('path/to/file.las')
  print(dimensions)
  
  # Or with already loaded LAS object:
  import laspy
  las = laspy.read('file.las')
  dimensions = get_dims(las)
  print(dimensions)
        """
    )
    
    parser.add_argument(
        '--path_to_las_file',
        required=True,
        help='Path to the LAS or LAZ file to analyze'
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.isfile(args.path_to_las_file):
        print(f"Error: File '{args.path_to_las_file}' not found.")
        sys.exit(1)
    
    # Analyze the file
    success = analyze_las_file(args.path_to_las_file)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
