# function to turn points loaded via pdal into a pyg Data object, with additional channels
import numpy as np
from torch_geometric.data import Data

COLORS_NORMALIZATION_MAX_VALUE = 255.0 * 256.0
RETURN_NUMBER_NORMALIZATION_MAX_VALUE = 7.0


def lidar_hd_pre_transform(points, colours):
    """Turn pdal points into torch-geometric Data object.

    Builds a composite (average) color channel on the fly. Calculate NDVI on the fly.

    Args:
        points (dict): PDAL-formatted dictionary of arrays.
        colours (list): List of color feature names to include.

    Returns:
        Data: the point cloud formatted for later deep learning training.
    """
    # Positions and base features
    pos = np.asarray([points["X"], points["Y"], points["Z"]], dtype=np.float32).transpose()

    # normalization
    occluded_points = points["ReturnNumber"] > 1

    points["ReturnNumber"] = points["ReturnNumber"] / RETURN_NUMBER_NORMALIZATION_MAX_VALUE
    points["NumberOfReturns"] = points["NumberOfReturns"] / RETURN_NUMBER_NORMALIZATION_MAX_VALUE

    for color in [color for color in colours if color != "ndvi"]:
        assert points[color].max() <= COLORS_NORMALIZATION_MAX_VALUE
        points[color][:] = points[color] / COLORS_NORMALIZATION_MAX_VALUE
        points[color][occluded_points] = 0.0

    # Optional: RGB average
    if all(c in colours for c in ["Red", "Green", "Blue"]):
        rgb_avg = (
            np.asarray([points["Red"], points["Green"], points["Blue"]], dtype=np.float32)
            .transpose()
            .mean(axis=1)
        )
    else:
        rgb_avg = None

    # Optional: NDVI
    if "ndvi" in colours:
        ndvi = (points["Infrared"] - points["Red"]) / (points["Infrared"] + points["Red"] + 1e-6)
    else:
        ndvi = None

    # Stack features
    feature_list = [
        points[name] for name in [
            "Intensity",
            "ReturnNumber",
            "NumberOfReturns"
        ]
    ]

    x_features_names = ["Intensity", "ReturnNumber", "NumberOfReturns"]

    for name in colours:
        if name in points.dtype.names:
            feature_list.append(points[name])
            x_features_names.append(name)

    if rgb_avg is not None:
        feature_list.append(rgb_avg)
        x_features_names.append("rgb_avg")

    if ndvi is not None:
        feature_list.append(ndvi)
        x_features_names.append("ndvi")

    x = np.stack(feature_list, axis=0).transpose()
    y = points["Classification"]

    data = Data(pos=pos, x=x, y=y, x_features_names=x_features_names)

    return data
