import geopandas as gpd
import pandas as pd
import time
import os
import subprocess
import tempfile
import shutil

# Aldagaiak: fitxategiak
input_shp  = "/home9/BTAGV2025/BTA_CUBIERT_TERRESTRE_A_5000.shp"
output_shp = "./dat/vt_landcover_ej1.shp"

# Aldagaiak: eremuak eta mapeatzea
category_field = "LEGENDA_1"
output_field   = "type"

mapping = {
    "Baso zuhaiztia": "Forest",
    "Belardia":       "Meadow",
    "Larrea":         "Meadow",
    "Suebakiak":      "Meadow",
    "Sastraka":       "Scrub",
}

# Irakurri Shapefile
print("Irakurtzen...")
t0 = time.time()
gdf = gpd.read_file(input_shp)
print(f"  Irakurrita: {len(gdf)} poligono ({time.time() - t0:.1f}s)")

# Filtratu mapeatutako kategoriak bakarrik
print("Filtratzen...")
t1 = time.time()
gdf_filtered = gdf[gdf[category_field].isin(mapping.keys())].copy()
print(f"  Hautatu: {len(gdf_filtered)} poligono ({time.time() - t1:.1f}s)")

# Sortu type eremua mapeatzea erabilita
print("Mapeatzen...")
t2 = time.time()
gdf_filtered[output_field] = gdf_filtered[category_field].map(mapping)
print(f"  Mapeatuta ({time.time() - t2:.1f}s)")

# Disolbaketa type eremuan oinarrituta
print("Disolbatzen...")
t3 = time.time()
dissolved = gdf_filtered[[output_field, "geometry"]].dissolve(by=output_field, as_index=False)
print(f"  Disolbatuta: {len(dissolved)} poligono ({time.time() - t3:.1f}s)")

# Aldi baterako direktorioa eta Shapefile
tmp_dir = tempfile.mkdtemp()
tmp_shp = os.path.join(tmp_dir, "dissolved.shp")
dissolved.to_file(tmp_shp)

# output_shp ezabatu badago
base = os.path.splitext(output_shp)[0]
for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
    f = base + ext
    if os.path.exists(f):
        os.remove(f)
        print(f"  Ezabatuta: {f}")

# GRASS script-a idatzi
grass_script = os.path.join(tmp_dir, "vclean.sh")
grassdata   = os.path.join(tmp_dir, "grassdata")
output_shp_abs = os.path.abspath(output_shp)
tmp_shp_abs    = os.path.abspath(tmp_shp)

with open(grass_script, "w") as f:
    f.write(f"""#!/bin/bash
# Location sortu Shapefile-aren CRS-etik
grass74 -c "{tmp_shp_abs}" "{grassdata}/loc" -e

# GRASS komandoak exekutatu location berrian
grass74 "{grassdata}/loc/PERMANENT" --exec bash << 'EOF'
v.import input="{tmp_shp_abs}" output=dissolved --overwrite
v.clean input=dissolved output=cleaned tool=break,rmdupl,rmline,rmdangle,rmbridge,bpol,prune threshold=0,0,0,0,0,0,0.1 --overwrite
v.out.ogr input=cleaned output="{output_shp_abs}" format=ESRI_Shapefile --overwrite
EOF
""")

os.chmod(grass_script, 0o755)

# Exekutatu
print("v.clean exekutatzen...")
t4 = time.time()
result = subprocess.run(
    ["bash", grass_script],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    universal_newlines=True
)

if result.returncode == 0:
    print(f"  v.clean eginda ({time.time() - t4:.1f}s)")
else:
    print("  v.clean errorea:")
    print(result.stdout)
    print(result.stderr)

print(f"\nDenbora guztira: {time.time() - t0:.1f}s")

# Aldi baterako fitxategiak ezabatu
shutil.rmtree(tmp_dir)
