import os
import csv

# Direktorioa zehaztu
directorio = "csv"  # Zure CSV fitxategien direktorioa hemen jarri

# Direktorioan dauden CSV fitxategien zerrenda lortu
csv_files = [f for f in os.listdir(directorio) if f.endswith('.csv')]

# Goiburuaren zutabeak definitu
header = ['field', 'fieldname_eu', 'fieldname_es', 'fieldname_en']

# CSV fitxategi bakoitzari goiburua gehitu
for csv_file in csv_files:
    file_path = os.path.join(directorio, csv_file)

    # Datuak irakurri
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    # Goiburua gehitu eta fitxategia berridatzi
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"Goiburua gehitu da: {csv_file}")

print("Prozesua amaitu da. CSV fitxategi guztiei goiburua gehitu zaie.")
