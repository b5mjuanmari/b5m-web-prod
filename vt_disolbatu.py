import geopandas as gpd
import pandas as pd
import time
import os
from shapely.ops import unary_union

# Aldagaiak
input_gpkg = "./dat/vt_landcover_ej.gpkg"
output_gpkg = "./dat/vt_landcover_ej_dis5.gpkg"
min_area = 10000  # m2

# Jatorrizko geruzaren izena lortu (GPKG fitxategiaren izena atzizki gabe)
input_layer = os.path.splitext(os.path.basename(input_gpkg))[0]
output_layer = os.path.splitext(os.path.basename(output_gpkg))[0]

print(f"Jatorrizko geruza: {input_layer}")
print(f"Irteerako geruza: {output_layer}")

# Irakurri GPKG
print("Irakurtzen...")
t0 = time.time()
gdf = gpd.read_file(input_gpkg, layer=input_layer)
print(f"  Irakurrita: {len(gdf)} poligono ({time.time() - t0:.1f}s)")

# Poligono bakunak lortu (uharteak bereizteko)
print("Uharteak aztertzen...")
t3 = time.time()
exploded = gdf.explode(index_parts=False).reset_index(drop=True)
exploded["area_m2"] = exploded.geometry.area

# Uharte txikiak eta nagusiak bereizi
mask_txiki = exploded["area_m2"] < min_area
uharteak = exploded[mask_txiki].copy()
nagusiak = exploded[~mask_txiki].copy().reset_index(drop=True)
uharte_kopurua = len(uharteak)
print(f"  Fusionatu beharreko uharte txikiak: {uharte_kopurua}")
print(f"  Poligono nagusiak: {len(nagusiak)}")

# Spatial join ukimenak aurkitzeko
print("Spatial join egiten...")
ukipenak = gpd.sjoin(
    uharteak[['geometry']].reset_index(drop=True),
    nagusiak[['geometry', 'type_eu']],
    how='inner',
    op='intersects'
)
print(f"  {len(ukipenak)} ukimen erlazio aurkitu dira")

# Uharte bakoitzari zein nagusirekin fusionatu erabaki (ukitu luzeenaren arabera)
print("Ukitu luzenak kalkulatzen...")
uharteak['parent_idx'] = None
prozesatutakoak = 0

for uharte_idx in uharteak.index:
    prozesatutakoak += 1
    if prozesatutakoak % 1000 == 0:
        print(f"  {prozesatutakoak}/{uharte_kopurua} uharte prozesatuta ({time.time() - t3:.1f}s)")

    # Aurkitu uharte honekin ukitzen duten nagusiak
    ukipenak_uharte = ukipenak[ukipenak.index_right == uharte_idx]

    if len(ukipenak_uharte) == 0:
        # Ez badu inorekin ukitzen, aurkitu gertuena
        uharte_geom = uharteak.loc[uharte_idx, 'geometry']
        distantziak = nagusiak.geometry.distance(uharte_geom)
        hurbilena = distantziak.idxmin()
        uharteak.at[uharte_idx, 'parent_idx'] = hurbilena
        uharteak.at[uharte_idx, 'type_eu'] = nagusiak.loc[hurbilena, 'type_eu']
    else:
        # Kalkulatu ukitu luzeena
        uharte_geom = uharteak.loc[uharte_idx, 'geometry']
        max_length = 0
        best_idx = None

        for _, row in ukipenak_uharte.iterrows():
            # Lortu nagusiaren index-a (zutabe ezberdina izan daiteke)
            if 'index_right' in row.index:
                nagusi_idx = row['index_right']
            else:
                nagusi_idx = row.name

            # Ziurtatu nagusi_idx existitzen dela nagusiak-en
            if nagusi_idx in nagusiak.index:
                nagusi_geom = nagusiak.loc[nagusi_idx, 'geometry']
                ukitu_luzera = nagusi_geom.intersection(uharte_geom).length
                if ukitu_luzera > max_length:
                    max_length = ukitu_luzera
                    best_idx = nagusi_idx

        if best_idx is not None and best_idx in nagusiak.index:
            uharteak.at[uharte_idx, 'parent_idx'] = best_idx
            uharteak.at[uharte_idx, 'type_eu'] = nagusiak.loc[best_idx, 'type_eu']

print(f"  Uharteak esleituta ({time.time() - t3:.1f}s)")

# Egiaztatu zenbat uharte geratu diren esleitu gabe
esleitu_gabeak = uharteak[uharteak['parent_idx'].isna()]
if len(esleitu_gabeak) > 0:
    print(f"  ABISUA: {len(esleitu_gabeak)} uharte esleitu gabe geratu dira")

# Fusionatu uharteak nagusiekin
print("Fusionatzen...")
t4 = time.time()

# Kopiatu nagusiak emaitza GeoDataFrame batera
emaitza = nagusiak.copy()

# Kendu esleitu gabeko uharteak (ezin dira fusionatu)
uharteak_fusionatzeko = uharteak[uharteak['parent_idx'].notna()].copy()

# Taldekatu uharteak gurasoaren arabera
if len(uharteak_fusionatzeko) > 0:
    uharteak_por_guraso = uharteak_fusionatzeko.groupby('parent_idx')

    # Guraso bakoitzeko, fusionatu bere uharte guztiak
    fusionatutakoak = 0
    for parent_idx, group in uharteak_por_guraso:
        fusionatutakoak += 1
        if fusionatutakoak % 100 == 0:
            print(f"  {fusionatutakoak}/{len(uharteak_por_guraso)} guraso fusionatzen...")

        # Aurkitu gurasoaren geometria
        if parent_idx in emaitza.index:
            guraso_geom = emaitza.loc[parent_idx, 'geometry']

            # Bildu uharte guztien geometriak
            uharte_geometriak = group.geometry.tolist()

            # Fusionatu gurasoa eta uharteak (batu geometriak)
            geometria_berria = unary_union([guraso_geom] + uharte_geometriak)

            # Eguneratu geometria
            emaitza.at[parent_idx, 'geometry'] = geometria_berria

print(f"  Fusionatuta ({time.time() - t4:.1f}s)")

print(f"  Emaitza: {len(emaitza)} poligono (hasieran {len(nagusiak)} nagusi + {uharte_kopurua} uharte = {len(emaitza)} after fusion)")

# Gorde emaitza
print("Gordetzen...")
t5 = time.time()
emaitza.to_file(output_gpkg, driver="GPKG", layer=output_layer)
print(f"  Gordeta '{output_layer}' geruzan ({time.time() - t5:.1f}s)")

print(f"\nDenbora guztira: {time.time() - t0:.1f}s")
print(f"Fusionatutako uharte txikiak: {len(uharteak_fusionatzeko)}")
print(f"Esleitu gabeko uharteak (ezabatuta): {len(esleitu_gabeak)}")
print(f"Azken poligono kopurua: {len(emaitza)}")
