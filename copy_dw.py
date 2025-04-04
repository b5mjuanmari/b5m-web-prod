import cx_Oracle
import pandas as pd
import os
import tarfile
from datetime import datetime
import shutil

# Oracle datu-basearekin konektatzeko parametroak
username = 'b5mweb_nombres'
password = 'web+'
dsn = 'exploracle:1521/bdet'

try:
    connection = cx_Oracle.connect(username, password, dsn)
    print("Oracle datu-basearekin konektatuta!")
except cx_Oracle.DatabaseError as e:
    print(f"Errore bat egon da konektatzerakoan: {e}")
    exit(1)

cursor = connection.cursor()

# Taulak aukeratu
cursor.execute("""
    select table_name
    from user_tables
    where lower(table_name) like 'dw_%'
    order by table_name asc
""")

tables = [row[0] for row in cursor.fetchall()]

if not tables:
    print("Ez dago 'dw_' katearekin hasten diren taulak.")
    exit(1)

# Fitxategien direktorioa
output_dir = "/tmp/dw_exported_tables"
os.makedirs(output_dir, exist_ok=True)
data_dir = "dat"
os.makedirs(data_dir, exist_ok=True)

total_tables = len(tables)
for i, table in enumerate(tables, 1):
    print(f"[{i}/{total_tables}] Esportatzen: {table}")

    # 1. CSV fitxategia esportatu
    query = f'select * from "{table}" order by 1 asc'
    try:
        df = pd.read_sql(query, connection)
        csv_filename = os.path.join(output_dir, f"{table}.csv")
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    except Exception as e:
        print(f"Errorea {table} taula esportatzerakoan: {e}")
        continue

    # 2. DDL esportatu
    try:
        cursor.execute(f"""
            select dbms_metadata.get_ddl('TABLE', :1, :2)
            from dual
        """, [table, username.upper()])

        ddl = cursor.fetchone()[0]
        if isinstance(ddl, cx_Oracle.LOB):
            ddl = ddl.read()

        ddl_filename = os.path.join(output_dir, f"{table}_ddl.sql")
        with open(ddl_filename, 'w', encoding='utf-8') as ddl_file:
            ddl_file.write(ddl)
    except Exception as e:
        print(f"Errorea {table} taularen DDL esportatzerakoan: {e}")

# 3. Fitxategiak konprimatu
timestamp = datetime.now().strftime('%Y%m%d%H%M')
tar_filename = f"{data_dir}/datasets2_{timestamp}.tar.xz"
if os.path.exists(tar_filename):
    os.remove(tar_filename)

try:
    with tarfile.open(tar_filename, 'w:xz') as tar:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                tar.add(file_path, arcname=os.path.relpath(file_path, output_dir))
except Exception as e:
    print(f"Errorea konprimatzeko: {e}")

# Garbitu eta itxi
shutil.rmtree(output_dir)
cursor.close()
connection.close()

print(f"Esportazioa eta konpresioa burutu dira: {tar_filename}")
