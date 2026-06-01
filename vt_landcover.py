import geopandas as gpd
import pandas as pd
import time
import os

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

# Gorde type eta geometria bakarrik
gdf_out = gdf_filtered[[output_field, "geometry"]]

# Ezabatu output_shp badago
base = os.path.splitext(output_shp)[0]
for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]:
    f = base + ext
    if os.path.exists(f):
        os.remove(f)
        print(f"  Ezabatuta: {f}")

# Gorde Shapefile
print("Gordetzen...")
t3 = time.time()
gdf_out.to_file(output_shp)
print(f"  Gordeta: {output_shp} ({time.time() - t3:.1f}s)")

print(f"\nBanaketa:\n{gdf_out[output_field].value_counts().to_string()}")
print(f"\nDenbora guztira: {time.time() - t0:.1f}s")
