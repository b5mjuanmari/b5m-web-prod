"""
blokeak_irakurri_klasifikatu.py

Script honek CSV fitxategi bat irakurtzen du eta blokeetan antolatutako datuak pantailaratzen ditu,
bloke bakoitza bere motaren arabera bereiziz.

Funtzionalitatea:
    - CSV fitxategia irakurri eta datuak memorian gorde.
    - Bloke bakoitza bere motaren arabera bereizi eta inprimatu.
    - Blokeen arteko trantsizioak detektatu eta inprimatzea kontrolatu.

Parametroak:
    csv_fitxategia (str): Irakurri nahi den CSV fitxategiaren bidea.
    motak (list): Blokeen motak definitzen duten stringen zerrenda.

Adibide erabilera:
    >>> mota = ["GFA_DST_CP_LAND", "GFA_DST_CP_URBAN", "GFA_DST_CP_ZONING"]
    >>> irakurri_blokeak("csv/GFA_DSET_CP.csv", mota)
"""

import csv

def irakurri_blokeak(csv_fitxategia, motak):
    # CSV fitxategia irakurri
    with open(csv_fitxategia, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # lehenengo errenkada saltatu (header)

        # CSV lerro guztiak memorian gorde
        lerroak = list(reader)

    # Blokeak bilatu eta inprimatu
    for mota in motak:
        print(f"\n=== {mota} ===")
        inprimatu = False
        for lerro in lerroak:
            if lerro[0] == mota:
                inprimatu = True
            elif lerro[0] in motak and lerro[0] != mota and inprimatu:
                # hurrengo blokean gaude, gelditu
                break

            if inprimatu:
                print(",".join(lerro))


# Adibidez erabilera:
mota = ["GFA_DST_CP_LAND", "GFA_DST_CP_URBAN", "GFA_DST_CP_ZONING"]
irakurri_blokeak("csv/GFA_DSET_CP.csv", mota)
