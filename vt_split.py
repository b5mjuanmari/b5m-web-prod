import geopandas as gpd
from shapely.geometry import box

#SRC = "./dat/vt_landcover_SIOSEAR.gpkg"
SRC = "./dat/SIOSEAR_20_2.gpkg"
#DST = "./dat/vt_landcover_SIOSEAR_split.gpkg"
DST = "./dat/SIOSEAR_20_2_split.gpkg"
LAYER = "vt_landcover_SIOSEAR"
STEP = 5000

gdf = gpd.read_file(SRC, layer=LAYER)

# Geometria baliogabeak konpondu (Shapely 1.7-n ez dago make_valid)
inv = ~gdf.geometry.is_valid
gdf.loc[inv, "geometry"] = gdf.loc[inv, "geometry"].buffer(0)

# 5 km-ko sarea, 5000ren multiploetara lerrokatua
minx, miny, maxx, maxy = gdf.total_bounds
x0, y0 = int(minx // STEP) * STEP, int(miny // STEP) * STEP
cells = [box(x, y, x + STEP, y + STEP)
         for x in range(x0, int(maxx) + STEP, STEP)
         for y in range(y0, int(maxy) + STEP, STEP)]
grid = gpd.GeoDataFrame(geometry=cells, crs=gdf.crs)
grid_sindex = grid.sindex

rows = []
for i, (geom, typ) in enumerate(zip(gdf.geometry, gdf["type"])):
    if geom is None or geom.is_empty:
        continue
    for ci in grid_sindex.query(geom, predicate="intersects") \
            if hasattr(grid_sindex, "query") and False else \
            list(grid_sindex.intersection(geom.bounds)):
        piece = geom.intersection(grid.geometry.iloc[ci])
        if piece.is_empty:
            continue
        # GeometryCollection-etatik poligonoak bakarrik hartu
        parts = getattr(piece, "geoms", [piece])
        for p in parts:
            if p.geom_type in ("Polygon", "MultiPolygon") and p.area > 0:
                rows.append({"type": typ, "geometry": p})
    if i % 10000 == 0:
        print(i, len(rows))

out = gpd.GeoDataFrame(rows, crs=gdf.crs)
out = out.explode().reset_index(drop=True)   # MultiPolygon -> Polygon
out.to_file(DST, layer=LAYER, driver="GPKG")
