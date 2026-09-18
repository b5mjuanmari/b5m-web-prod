#!/usr/bin/env python3
"""
Log sistema orokorra, beste script batzuetan berrerabiltzeko modukoa.

Ezaugarriak:
  - Mezu guztiak log fitxategi batera joaten dira (errore eta abisuak barne).
  - Log fitxategirik ematen ez bada, mezuak terminalera soilik joaten dira.
  - Terminalera soilik sys.stdout.isatty() True bada.
  - Mezu bakoitzaren aurrean data/ordua: YYYYMMDD HH:MM:SS formatuan.
  - Log fitxategia ez da ezabatzen existitzen bada (append modua).
  - Hasiera/Bukaera mezuak automatikoki idazten dira.
  - Python-en DeprecationWarning/FutureWarning abisuak isilarazten dira
    (pyproj, shapely, geopandas, etab.-ek sortutakoak), log-a zikin ez
    dezaten.
"""

import sys
import os
import warnings
from datetime import datetime


# Isilarazi beharreko abisu-motak. Python 3.6-rekin pyproj-ek
# FutureWarning ugari botatzen ditu '+init=' sintaxi zaharkituagatik.
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="pyproj")
warnings.filterwarnings("ignore", category=UserWarning, module="fiona")
warnings.filterwarnings("ignore", category=UserWarning, module="geopandas")


class Log:
    """Log sistema sinplea, fitxategi bakarrera eta terminalera (aukeran)."""

    def __init__(self, log_bidea, script_izena, argumentuak):
        """
        :param log_bidea: log fitxategiaren bidea (None bada, ez da fitxategirik erabiliko)
        :param script_izena: script-aren izena (basename)
        :param argumentuak: script-ari pasatako argumentuak (lista)
        """
        self.log_bidea = log_bidea
        self.script_izena = script_izena
        self.argumentuak = argumentuak
        self._terminalera = sys.stdout.isatty()
        self._fitxategia = None

        if self.log_bidea:
            try:
                self._fitxategia = open(log_bidea, "a", encoding="utf-8")
            except OSError as e:
                print(
                    f"[ERROREA] Ezin izan da log fitxategia ireki: {e}",
                    file=sys.stderr,
                )
                sys.exit(1)

        self._idatzi_hasiera()

    # ------------------------------------------------------------------
    # Barne-metodoak
    # ------------------------------------------------------------------
    def _denbora(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _argumentu_katea(self):
        return " ".join(self.argumentuak)

    def _idatzi_hasiera(self):
        mezua = (
            f"{self._denbora()} - Hasiera - "
            f"{self.script_izena} {self._argumentu_katea()}"
        )
        self._idatzi(mezua)

    def _idatzi_bukaera(self):
        mezua = (
            f"{self._denbora()} - Bukaera - "
            f"{self.script_izena} {self._argumentu_katea()}"
        )
        self._idatzi(mezua)

    def _idatzi(self, mezua):
        if self._fitxategia is not None:
            try:
                self._fitxategia.write(mezua + "\n")
                self._fitxategia.flush()
            except OSError:
                pass

        if self._terminalera:
            print(mezua)

    # ------------------------------------------------------------------
    # API publikoa
    # ------------------------------------------------------------------
    def info(self, mezua):
        self._idatzi(f"{self._denbora()} - INFO - {mezua}")

    def abisua(self, mezua):
        self._idatzi(f"{self._denbora()} - ABISUA - {mezua}")

    def errorea(self, mezua):
        self._idatzi(f"{self._denbora()} - ERROREA - {mezua}")

    def bukaera(self):
        self._idatzi_bukaera()
        if self._fitxategia is not None:
            try:
                self._fitxategia.close()
            except OSError:
                pass

    # ------------------------------------------------------------------
    # Testuinguru-kudeatzailea (with erabiltzeko)
    # ------------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.errorea(f"Salbuespena: {exc_type.__name__}: {exc_val}")
        self.bukaera()
        return False
