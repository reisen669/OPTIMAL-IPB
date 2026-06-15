#!/usr/bin/env python3
"""
Analyze GeoTIFF files and generate extent files with metadata.

This script processes GeoTIFF files in sample_data_qgis/ and generates
extent files containing CRS, dimensions, lat/lon extents, GSD, and coverage area.
"""

import os
import sys

# Set PROJ data directory for coordinate transformations
os.environ['PROJ_DATA'] = r'C:\Users\suily\miniconda3\envs\qgis_gdal_env\Library\share\proj'

from osgeo import gdal, osr

gdal.UseExceptions()


def analyze_geotiff(tif_path, output_txt=None):
    """
    Analyze a GeoTIFF and generate an extent file.

    Args:
        tif_path: Path to GeoTIFF file
        output_txt: Path to output text file (default: same dir, <name>_extent.txt)

    Returns:
        Path to generated extent file
    """
    ds = gdal.Open(tif_path)
    if ds is None:
        raise ValueError(f"Cannot open {tif_path}")

    # Get raster properties
    width = ds.RasterXSize
    height = ds.RasterYSize
    bands = ds.RasterCount
    gt = ds.GetGeoTransform()

    # Pixel resolution (may be negative for Y)
    pixel_x = abs(gt[1])
    pixel_y = abs(gt[5])

    # Coverage in native CRS units
    coverage_w = width * pixel_x
    coverage_h = height * pixel_y
    total_area = coverage_w * coverage_h

    # CRS info
    srs = osr.SpatialReference(ds.GetProjection())
    crs_name = srs.GetName() if srs.IsProjected() else "Geographic"
    epsg = srs.GetAttrValue("AUTHORITY", 1) if srs.GetAuthorityCode(None) else "Unknown"

    # Corner coordinates in native CRS
    ulx = gt[0]
    uly = gt[3]
    lrx = ulx + width * gt[1]
    lry = uly + height * gt[5]

    # Transform to WGS84 (EPSG:4326)
    source_srs = osr.SpatialReference(ds.GetProjection())
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(source_srs, target_srs)

    def to_latlon(x, y):
        lat, lon, _ = transform.TransformPoint(x, y)
        return lat, lon

    ul_lat, ul_lon = to_latlon(ulx, uly)
    ur_lat, ur_lon = to_latlon(lrx, uly)
    lr_lat, lr_lon = to_latlon(lrx, lry)
    ll_lat, ll_lon = to_latlon(ulx, lry)

    north = max(ul_lat, ur_lat)
    south = min(ll_lat, lr_lat)
    west = min(ul_lon, ll_lon)
    east = max(ur_lon, lr_lon)

    # Band info
    datatype = ds.GetRasterBand(1).DataType
    datatype_name = gdal.GetDataTypeName(datatype)

    # Layer name (filename without extension)
    layer_name = os.path.splitext(os.path.basename(tif_path))[0]

    # Output file path
    if output_txt is None:
        output_txt = os.path.join(os.path.dirname(tif_path), f"{layer_name}_extent.txt")

    # Write extent file
    with open(output_txt, 'w') as f:
        f.write(f"Layer: {layer_name}\n")
        f.write(f"File:  {os.path.basename(tif_path)}\n")
        f.write(f"CRS:   EPSG:{epsg} ({crs_name})\n")
        f.write("\n")
        f.write("--- Lat/Lon Extents (WGS84 / EPSG:4326) ---\n")
        f.write("\n")
        f.write("Bounding box:\n")
        f.write(f"  North (max lat):  {north:.8f}\n")
        f.write(f"  South (min lat):  {south:.8f}\n")
        f.write(f"  West  (min lon):  {west:.8f}\n")
        f.write(f"  East  (max lon):  {east:.8f}\n")
        f.write("\n")
        f.write("Corners:\n")
        f.write(f"  Upper-Left  (UL):  lat  {ul_lat:.8f},  lon {ul_lon:.8f}\n")
        f.write(f"  Upper-Right (UR):  lat  {ur_lat:.8f},  lon {ur_lon:.8f}\n")
        f.write(f"  Lower-Right (LR):  lat  {lr_lat:.8f},  lon {lr_lon:.8f}\n")
        f.write(f"  Lower-Left  (LL):  lat  {ll_lat:.8f},  lon {ll_lon:.8f}\n")
        f.write("\n")
        f.write("--- Raster Properties ---\n")
        f.write("\n")
        f.write(f"Dimensions:       {width} x {height} pixels\n")
        f.write(f"Pixel resolution: {pixel_x:.4f} m (X) x {pixel_y:.4f} m (Y)")
        if pixel_x < 1.0:
            f.write(f"  (~{pixel_x:.1f} m GSD)")
        f.write("\n")
        f.write(f"Coverage:         {coverage_w:.2f} m (W) x {coverage_h:.2f} m (H)\n")
        f.write(f"Total area:       {total_area:,.0f} m²  ({total_area/10000:.4f} ha)\n")
        f.write(f"Bands:            {bands} (RGB, {datatype_name})\n")

    ds = None
    return output_txt


# Process all GeoTIFFs
if __name__ == "__main__":
    base_dir = r'C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb\sample_data_qgis'

    tif_files = [
        os.path.join(base_dir, 'canvas_0.5mpx.tif'),
        os.path.join(base_dir, 'canvas_1mpx.tif'),
        os.path.join(base_dir, 'sample.tif'),
        os.path.join(base_dir, 'mys_lat3388N_lon10299E', 'imagery_1.0mpx.tif'),
        os.path.join(base_dir, 'mys_lat3388N_lon10299E', 'imagery_0.5mpx.tif'),
        os.path.join(base_dir, 'mys_lat3388N_lon10299E', 'imagery_0.3mpx.tif'),
        os.path.join(base_dir, 'mys_lat3388N_lon10299E', 'imagery_0.1mpx.tif'),
    ]

    print("Analyzing GeoTIFF files...")
    print()

    for tif in tif_files:
        if os.path.exists(tif):
            print(f"Processing: {os.path.basename(tif)}")
            out = analyze_geotiff(tif)
            print(f"  Created: {os.path.basename(out)}")
        else:
            print(f"Skipping: {os.path.basename(tif)} (not found)")

    print()
    print("Done. All extent files created.")
