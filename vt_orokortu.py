import geopandas as gpd
from shapely.validation import make_valid
from shapely.geometry import MultiPolygon, Polygon, GeometryCollection
import warnings
import time

warnings.filterwarnings('ignore', 'GeoSeries.notna', UserWarning)

INPUT_GPKG = "/home5/SHP/Tiles/vt_landuse_vegetation.gpkg"
#INPUT_GPKG = "./dat/LQ.gpkg"
OUTPUT_GPKG = "./dat/vt_landuse_vegetation_z11.gpkg"
#OUTPUT_GPKG = "./dat/vt_landuse_vegetation_LQ_z11.gpkg"

def poligonoak_atera(geom):
    """GeometryCollection batetik poligonoak soilik atera."""
    if geom is None:
        return None
    if isinstance(geom, (Polygon, MultiPolygon)):
        return geom
    if isinstance(geom, GeometryCollection):
        poliak = [g for g in geom.geoms if isinstance(g, (Polygon, MultiPolygon))]
        if not poliak:
            return None
        if len(poliak) == 1:
            return poliak[0]
        return MultiPolygon([
            p for geom in poliak
            for p in (geom.geoms if isinstance(geom, MultiPolygon) else [geom])
        ])
    return None

print("Kargatzen...")
t0 = time.time()
gdf = gpd.read_file(INPUT_GPKG)
total_jatorrizkoa = len(gdf)
print(f"  {total_jatorrizkoa} poligono kargatu ({time.time()-t0:.1f}s)")

# --- 1. GEOMETRIAK KONPONDU ---
print("Geometriak konpontzen...")
gdf.geometry = gdf.geometry.apply(
    lambda g: make_valid(g) if g is not None and not g.is_valid else g
)
gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notna()]

# --- 2. DISSOLVE ---
#print("Dissolve egiten...")
#gdf_dissolved = gdf.dissolve(by="type").reset_index()
#print(f"  Dissolve ostean: {len(gdf_dissolved)} kategoria")
#print(f"  Geometry motak:\n{gdf_dissolved.geometry.geom_type.to_string()}")

# --- 3. GeometryCollection → MultiPolygon ---
print("GeometryCollection konpontzen...")
#gdf_dissolved.geometry = gdf_dissolved.geometry.apply(poligonoak_atera)
gdf.geometry = gdf.geometry.apply(poligonoak_atera)
#gdf_dissolved = gdf_dissolved[~gdf_dissolved.geometry.is_empty & gdf_dissolved.geometry.notna()]
gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notna()]
#print(f"  Geometry motak konpondu ostean:\n{gdf_dissolved.geometry.geom_type.to_string()}")
print(f"  Geometry motak konpondu ostean:\n{gdf.geometry.geom_type.to_string()}")

# --- 4. SIMPLIFIKATU ---
print("Simplifikatzen (50m)...")
#gdf_dissolved.geometry = gdf_dissolved.geometry.simplify(
gdf.geometry = gdf.geometry.simplify(
    tolerance=50,
    preserve_topology=True
)

# --- 5. GEOMETRIA HUTSAK KENDU ---
#gdf_dissolved.geometry = gdf_dissolved.geometry.apply(
gdf.geometry = gdf.geometry.apply(
    lambda g: make_valid(g) if g is not None and not g.is_valid else g
)
#gdf_dissolved = gdf_dissolved[~gdf_dissolved.geometry.is_empty & gdf_dissolved.geometry.notna()]
gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notna()]
#print(f"  Simplifikazio ostean: {len(gdf_dissolved)} kategoria")
print(f"  Simplifikazio ostean: {len(gdf)} kategoria")

# --- 6. GPKG GORDE ---
print("Gordetzen...")
#gdf_dissolved.to_file(OUTPUT_GPKG, driver="GPKG")
gdf.to_file(OUTPUT_GPKG, driver="GPKG")

print(f"\nOSOTUTA ({time.time()-t0:.1f}s)")
print(f"  Jatorrizkoa: {total_jatorrizkoa} poligono")
#print(f"  Orokortua:   {len(gdf_dissolved)} kategoria")
print(f"  Orokortua:   {len(gdf)} kategoria")
#print(gdf_dissolved[["type"]].assign(geom_type=gdf_dissolved.geometry.geom_type))
print(gdf[["type"]].assign(geom_type=gdf.geometry.geom_type))
