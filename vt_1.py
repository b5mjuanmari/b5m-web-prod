import geopandas as gpd

input_shp = "/home9/BTAGV2025/BTA_CUBIERT_TERRESTRE_A_5000.shp"
gdf = gpd.read_file(input_shp)

# LEGENDA_1 eremu balio guztiak ikusi
print("LEGENDA_1 balio bakarrak:")
for v in sorted(gdf["LEGENDA_1"].unique()):
    r = repr(v)
    print("  " + r)
