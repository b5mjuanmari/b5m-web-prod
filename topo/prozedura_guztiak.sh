#!/bin/bash
#scriptak exekutatzeko  putty-in lidar1 konektatu (lidar:mobile1) eta cd SCRIPTS bertan exekutatu "python3 0*" idatziz
#hauxe exekutatzeko ./prozedura_guztiak.sh (bestela ez du topatzen)
python3 00_hasiera.py
python3 01_Aurkintzen_prozedura.py #hau derrigorrezkoa da p-dev2 osatzeko
python3 02_Gailurren_prozedura.py
python3 03_Mendateen_prozedura.py
python3 04_Mendien_prozedura.py
python3 05_Lepoen_prozedura.py
python3 06_Lurmuturren_prozedura.py
python3 07_Badien_prozedura.py
python3 08_Hondartzen_prozedura.py
python3 09_Urtegien_prozedura.py
python3 10_Estatikoen_prozedura.py

exit 0
