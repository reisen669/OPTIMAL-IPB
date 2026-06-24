"""Download missing 0.3 and 0.1 m/px imagery for mys_lat3388N_lon10299E."""
# E1 CanopyRS (hugobaudchon/CanopyRS): no pretrained weights found on GitHub Releases as of 2026-06-24.
# Current version uses SAM 3 (Meta, gated HuggingFace model) — requires huggingface-cli login and access approval.
# Environment blockers: requires Linux (Ubuntu 22.04), Python 3.10, CUDA 12.6 — incompatible with Windows/Python 3.12/CPU.
# Installation docs: https://hugobaudchon.github.io/CanopyRS/getting-started/installation/
# GitHub Releases: https://github.com/hugobaudchon/CanopyRS/releases (10 releases, 2022-2023, source archives only)
# E1 CanopyRS Status: BLOCKED — Phase 6 E1 empirical testing skipped.
import os
os.environ['PROJ_DATA'] = r'C:\Users\suily\miniconda3\envs\qgis_gdal_env\Library\share\proj'
from osgeo import gdal
gdal.UseExceptions()

ULX = 11464086.564073
ULY = 377242.052866
LRX = 11464728.435127
LRY = 376763.883391

OUTPUT_DIR = r'C:\Users\suily\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\optimal-ipb\sample_data_qgis\mys_lat3388N_lon10299E'

WMS_TEMPLATE = """\
<GDAL_WMS>
  <Service name="TMS">
    <ServerUrl>https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${{z}}/${{y}}/${{x}}</ServerUrl>
  </Service>
  <DataWindow>
    <UpperLeftX>-20037508.34</UpperLeftX>
    <UpperLeftY>20037508.34</UpperLeftY>
    <LowerRightX>20037508.34</LowerRightX>
    <LowerRightY>-20037508.34</LowerRightY>
    <TileLevel>{zoom}</TileLevel>
    <TileCountX>1</TileCountX>
    <TileCountY>1</TileCountY>
    <YOrigin>top</YOrigin>
  </DataWindow>
  <Projection>EPSG:3857</Projection>
  <BlockSizeX>256</BlockSizeX>
  <BlockSizeY>256</BlockSizeY>
  <BandsCount>3</BandsCount>
  <MaxConnections>5</MaxConnections>
  <Cache/>
</GDAL_WMS>"""

# Only download missing files
TARGETS = [
    (0.3, 19, 'imagery_0.3mpx.tif', 18),
    (0.1, 20, 'imagery_0.1mpx.tif', 19),
]

for target_res, zoom, filename, fallback_zoom in TARGETS:
    out_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(f'[skip] {filename} already exists ({os.path.getsize(out_path)/1e6:.1f} MB)')
        continue

    print(f'\n--- Downloading {filename} (target: {target_res} m/px, zoom: Z={zoom}) ---')
    for attempt_zoom in ([zoom] + ([fallback_zoom] if fallback_zoom else [])):
        wms_xml = WMS_TEMPLATE.format(zoom=attempt_zoom)
        wms_file = os.path.join(OUTPUT_DIR, f'_tmp_z{attempt_zoom}.xml')
        with open(wms_file, 'w') as f:
            f.write(wms_xml)
        try:
            warp_opts = gdal.WarpOptions(
                outputBounds=(ULX, LRY, LRX, ULY),
                outputBoundsSRS='EPSG:3857',
                dstSRS='EPSG:3857',
                xRes=target_res, yRes=target_res,
                resampleAlg='cubic',
                creationOptions=['COMPRESS=LZW', 'TILED=YES', 'BLOCKXSIZE=256', 'BLOCKYSIZE=256'],
                format='GTiff', multithread=True,
            )
            ds = gdal.Warp(out_path, wms_file, options=warp_opts)
            if ds is not None:
                w, h = ds.RasterXSize, ds.RasterYSize
                actual_res = abs(ds.GetGeoTransform()[1])
                ds = None
                sz = os.path.getsize(out_path) / 1e6
                if attempt_zoom != zoom:
                    new_name = filename.replace('.tif', f'_fallback_Z{attempt_zoom}.tif')
                    os.rename(out_path, os.path.join(OUTPUT_DIR, new_name))
                    print(f'  [OK] {new_name}  {w}x{h}px  GSD={actual_res:.4f}m  {sz:.1f}MB  [FALLBACK Z={attempt_zoom}]')
                else:
                    print(f'  [OK] {filename}  {w}x{h}px  GSD={actual_res:.4f}m  {sz:.1f}MB')
                break
            else:
                print(f'  [!] Z={attempt_zoom} returned None, trying fallback...')
        except Exception as e:
            print(f'  [X] Z={attempt_zoom} failed: {e}')
        finally:
            if os.path.exists(wms_file):
                os.remove(wms_file)

print('\nDone.')
