import geopandas as gpd
from shapely.geometry import box
from shapely.strtree import STRtree
import pandas as pd
import numpy as np
import os

# =====================================================
# KONFIGURAZIOA
# =====================================================

DISTANCIAS = [1000, 800, 600, 400, 200, 0]

PORCENTAJES = {
    6: 0.01,
    5: 0.03,
    4: 0.12,
    3: 0.24
}

# =====================================================
# KAPAK KARGATU (Shapefile / GeoPackage)
# =====================================================

shp_karpeta = "/home5/SHP/Tiles"
shp_karpeta_out = "/home9/SHP/tiles_saiakera/jm"

topo_path = "r_oronimia_p-dev-jm_04.shp"
barrios_path = "r_barrios_p.shp"
oronimia_path = "r_oronimia.shp"

toponimia_shape = os.path.join(shp_karpeta_out, topo_path)
barrios_shape = os.path.join(shp_karpeta, barrios_path)
oronimia_shape = os.path.join(shp_karpeta, oronimia_path)

print("Kapak kargatzen...")
print(f"Toponimia: {toponimia_shape}")
print(f"Barrios: {barrios_shape}")
print(f"Oronimia: {oronimia_shape}")

if not os.path.exists(toponimia_shape):
    print(f"ERROZEA: {toponimia_shape} ez da existitzen")
    exit(1)
if not os.path.exists(barrios_shape):
    print(f"ERROZEA: {barrios_shape} ez da existitzen")
    exit(1)
if not os.path.exists(oronimia_shape):
    print(f"ERROZEA: {oronimia_shape} ez da existitzen")
    exit(1)

topo = gpd.read_file(toponimia_shape)
barrios = gpd.read_file(barrios_shape)
oronimia = gpd.read_file(oronimia_shape)

print(f"Topo: {len(topo)} elementu")
print(f"Barrios: {len(barrios)} elementu")
print(f"Oronimia: {len(oronimia)} elementu")

# =====================================================
# INDIZE ESPAZIALA (STRtree)
# =====================================================

print("Indize espaziala sortzen...")

# Barrioen geometriak zerrenda batean
barrios_geom = list(barrios.geometry.values)
# Barrioen indizeak (STRtree-rentzat)
barrios_idx = STRtree(barrios_geom)

# =====================================================
# DICCIONARIO IDUT -> SUPERFIZIE
# =====================================================

print("Superfizieak kargatzen...")

sup_dict = {}

for idx, row in oronimia.iterrows():
    idut = row.get("IDUT")
    if idut is not None and pd.notna(idut):
        sup_dict[idut] = row.geometry.area

print(f"Superfizieak kargatuta: {len(sup_dict)}")

# =====================================================
# ROTULAR_C EREMUA GEHITU
# =====================================================

print("ROTULAR_C eremua gehitzen...")

topo['ROTULAR_C'] = None

# =====================================================
# PASO 1: PESO 2 HIRI-INGURUNERA
# =====================================================

print("\n=== PASO 1: PESO 2 (Hiri-ingurunea) ===")

candidatos = []
peso2_count = 0

for idx, row in topo.iterrows():
    geom = row.geometry

    # 250m-ko bufferra eta bounding box
    buffer_geom = geom.buffer(250)
    bbox = box(*buffer_geom.bounds)

    # Barrioak bilatu bounding box-ean
    # 🔧 ZUZENKETA: query(bbox)-k geometriak itzultzen ditu, indizeak ez
    posibles = barrios_idx.query(bbox)

    vecinos = 0

    # 🔧 ZUZENKETA: posibles lista geometriak dira, ez indizeak
    for barrio_geom in posibles:
        if geom.distance(barrio_geom) <= 250:
            vecinos += 1
            if vecinos > 1:
                break

    if vecinos > 1:
        topo.loc[idx, 'ROTULAR_C'] = 2
        peso2_count += 1
    else:
        superficie = sup_dict.get(row.get("IDUT"), 0)
        candidatos.append({
            "idx": idx,
            "geom": geom,
            "sup": superficie
        })

print(f"Peso 2 asignatuta: {peso2_count} elementuri")

# =====================================================
# ORDENATU SUPERFIZIEAREN ARABERA
# =====================================================

candidatos.sort(key=lambda x: x["sup"], reverse=True)
n = len(candidatos)

print(f"\nCandidatoak geratzen dira: {n}")

objetivos = {}
for peso, pct in PORCENTAJES.items():
    objetivos[peso] = round(n * pct)
    print(f"Peso {peso}: {objetivos[peso]} elementu ({pct*100:.0f}%)")

# =====================================================
# FUNZIOA: HAUTAKETA ESPAZIATUA
# =====================================================

def seleccionar_para_peso(candidatos, asignados_global, objetivo, peso):
    seleccionados = []

    for distancia_min in DISTANCIAS:
        if len(seleccionados) >= objetivo:
            break

        print(f"Peso {peso} - Distantzia {distancia_min}m - {len(seleccionados)}/{objetivo}")

        for elem in candidatos:
            if elem["idx"] in asignados_global:
                continue

            valido = True

            for sel in seleccionados:
                if elem["geom"].distance(sel["geom"]) < distancia_min:
                    valido = False
                    break

            if not valido:
                continue

            # Asignatu
            topo.loc[elem["idx"], 'ROTULAR_C'] = peso
            seleccionados.append(elem)
            asignados_global.add(elem["idx"])

            if len(seleccionados) >= objetivo:
                break

    return seleccionados

# =====================================================
# PASO 2: PESO 6, 5, 4, 3
# =====================================================

print("\n=== PASO 2: Peso altuak ===")

asignados = set()

for peso in [6, 5, 4, 3]:
    seleccionados = seleccionar_para_peso(
        candidatos,
        asignados,
        objetivos[peso],
        peso
    )
    print(f"Peso {peso} asignatuta: {len(seleccionados)} elementuri")

# =====================================================
# PASO 3: GAINERAKOAK -> PESO 2
# =====================================================

print("\n=== PASO 3: Gainerakoak PESO 2 ===")

resto_count = 0

for idx, row in topo.iterrows():
    if pd.isna(row['ROTULAR_C']):
        topo.loc[idx, 'ROTULAR_C'] = 2
        resto_count += 1

print(f"Peso 2 asignatuta: {resto_count} elementuri (gainerakoak)")

# =====================================================
# EMAITZAK GORDE
# =====================================================

print("\n=== Emaitzak gordetzen... ===")

# Shapefile gisa gorde (irteera karpeta berean)
output_path = os.path.join(shp_karpeta_out, "r_oronimia_p-dev-jm_04_emaitza.shp")
topo.to_file(output_path)
print(f"Shapefile gordeta: {output_path}")

# CSV gisa ere gorde
csv_path = os.path.join(shp_karpeta_out, "emaitzak.csv")
topo[['ROTULAR_C']].to_csv(csv_path)
print(f"CSV gordeta: {csv_path}")

# =====================================================
# LABURPENA
# =====================================================

print("\n===== RESUMEN FINALA =====")

conteo = topo['ROTULAR_C'].value_counts().sort_index()

for peso, count in conteo.items():
    print(f"Peso {int(peso)}: {count}")

total = len(topo)
print(f"\nTotal: {total} elementu")

asignados_total = topo['ROTULAR_C'].notna().sum()
print(f"Asignatuta: {asignados_total} / {total}")

print("\nProzesua amaitu da.")
