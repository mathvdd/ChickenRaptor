import os
from rpt_config import validate_file_path
import pandas as pd
import subprocess
from io import StringIO
import pypdf
from rpt_config import validate_date
import logging
import hashlib

def access2pd(db_path, column_names, table_name="T_Contrats"):

    if os.name == "posix":
        raw = subprocess.check_output(
            ["mdb-export", db_path, table_name]
        )

        text = raw.decode("utf-8", errors="replace")  #OLE columns are not decoded properly
        df = pd.read_csv(StringIO(text))

        df = df[[
            "Nom",
            "Prenom",
            "RegistreNational",
            "EMail",
            "DateIn",
            "DateOut",
            "Id",
            "Division"
            ]]
    elif os.name == "nt":
        import pyodbc

        conn = pyodbc.connect(
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            rf"DBQ={db_path};"
        )

        try:
            df = pd.read_sql(f"SELECT Nom, Prenom, RegistreNational, EMail, DateIn, DateOut, Id, Division FROM [{table_name}]", conn)
        except Exception as e:
            logging.debug(e)
            logging.exception("Could not execute query to access database")
            raise

        finally:
            conn.close()

    df["Barcode"] = "C" + df["Id"].astype(str) + df["Division"].astype(str)
    df["DateIn"] = pd.to_datetime(df["DateIn"], errors="coerce", format="%m/%d/%y %H:%M:%S",)
    df["DateOut"] = pd.to_datetime(df["DateOut"], errors="coerce", format="%m/%d/%y %H:%M:%S",)
    df = df[["Nom", "Prenom", "RegistreNational", "EMail", "DateIn", "DateOut", "Barcode"]].sort_values("DateIn", ascending=False)
    df["DateIn"] = df["DateIn"].dt.strftime("%d/%m/%Y")
    df["DateOut"] = df["DateOut"].dt.strftime("%d/%m/%Y")

    return df


def xlsx2pd(db_path, column_names):
    tab = pd.read_excel(db_path)
    # tab[column_names["colonne_date_in"]] = pd.to_datetime(self.tab[self.column_names["colonne_date_in"]]).dt.strftime("%d/%m/%Y")
    tab[column_names["colonne_date_in"]] = pd.to_datetime(tab[column_names["colonne_date_in"]], errors = "coerce")
    tab = tab.sort_values(column_names["colonne_date_in"], ascending=False)
    tab[column_names["colonne_date_in"]] = tab[column_names["colonne_date_in"]].dt.strftime("%d/%m/%Y")

    tab[column_names["colonne_date_out"]] = pd.to_datetime(tab[column_names["colonne_date_out"]], errors = "coerce")
    tab = tab.sort_values(column_names["colonne_date_out"], ascending=False)
    tab[column_names["colonne_date_out"]] = tab[column_names["colonne_date_out"]].dt.strftime("%d/%m/%Y")
    
    tab[column_names["colonne_registre_national"]] = tab[column_names["colonne_registre_national"]].astype(str)

    return tab



class DbData:

    def __init__(self, db_path : str, column_names : dict, import_method):
        self.column_names = column_names
        self.tab = import_method(db_path, column_names)

    def return_from_barcode(self, barcode : str) -> dict:
        res = self.tab.loc[self.tab[self.column_names["colonne_barcode"]] == barcode]
        
        if len(res) != 1:
            raise ValueError(
                f"Expected exactly one occurence for the contract {barcode}, found {len(res)}:\n{res}"
            )
            
        return res.iloc[0].to_dict()
            
    def return_from_RN(self, RN : int) -> dict:
        res = self.tab.loc[self.tab[self.column_names["colonne_registre_national"]] == str(RN)]
        
        if len(res) == 0:
            raise ValueError(
                f"Did not find a match in the database for {RN}"
            )
        # elif len(res) != 1:
        #     nunique_cols = [
        #         self.column_names["colonne_registre_national"],
        #         self.column_names["colonne_mail"], 
        #         self.column_names["colonne_nom"], 
        #         self.column_names["colonne_prenom"]
        #         ]
        #     if (len(res[nunique_cols].drop_duplicates()) != 1):
        #         logging.warning(
        #             f"Duplicates not matching in the table, taking more recent entry"
        #         )
            
        return res.iloc[0].to_dict()


class NRExtractor:

    def __init__(self, pdf_path:str):
        self.pdf_path = pdf_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def extract(self, get_hash=False) -> dict:
        res = {
            "RN":None,
            "name": None,
            "date_in":None,
            "date_out":None
            }

        with open(self.pdf_path, "rb") as fp:
            reader = pypdf.PdfReader(fp)
            text = reader.pages[0].extract_text()
            
            if get_hash:
                hasher = hashlib.sha256()
                for chunk in iter(lambda: fp.read(8192), b""):
                    hasher.update(chunk)
                res["hash"] = hasher.hexdigest()

        for line in text.split("\n"):

            if line.startswith("TRAVAILLEUR"):
                res["RN"] = int(line[13:34].replace(" ",""))
                res["name"] = line[35:]
            elif line.startswith("WERKNEMER"):
                res["RN"] = int(line[11:32].replace(" ",""))
                res["name"] = line[33:]

            elif line.startswith("Date de début de l'occupation"):
                date = line[31:48].replace(" ","")
                validate_date(date)
                res["date_in"] = date
            elif line.startswith("Begindatum tewerkstelling"):
                date = line[27:45].replace(" ","")
                validate_date(date)
                res["date_in"] = date

            elif line.startswith("Date de fin de l'occupation"):
                date = line[29:46].replace(" ","")
                validate_date(date)
                res["date_out"] = date
            elif line.startswith("Einddatum tewerkstelling"):
                date = line[26:44].replace(" ","")
                validate_date(date)
                res["date_out"] = date



            if not (None in res.values()):
                return res

        raise ValueError(f"Could not extract info from {self.pdf_path}: {res}")

    def extract_NR_pypdf(self) -> int:
        reader = pypdf.PdfReader(self.pdf_path)
        text = reader.pages[0].extract_text()

        found = False
        
        for line in text.split("\n"):
            if line.startswith("TRAVAILLEUR"):
                found = True
                break

        if not found:
            raise Exception("No NISS found in pdf {self.pdf_path}")

        return int(line[13:34].replace(" ",""))


def info_from_RN(xlsx_data: DbData, file : str) -> dict:
    with NRExtractor(file) as ext:
        pdf_info = ext.extract()
    pdict = xlsx_data.return_from_RN(pdf_info["RN"])
    
    for item in [xlsx_data.column_names['colonne_mail'], xlsx_data.column_names['colonne_nom'], xlsx_data.column_names['colonne_prenom']]:
        if item not in pdict.keys():
            raise ValueError(f"Parameter '{item}' not found in the database")

    return pdict | pdf_info

def info_from_barcode(xlsx_data: DbData, file : str) -> dict:
    barcode = os.path.splitext(os.path.basename(file))[0]
    pdict = xlsx_data.return_from_barcode(barcode)
    
    for item in [xlsx_data.column_names['colonne_mail'], xlsx_data.column_names['colonne_prenom'], xlsx_data.column_names['colonne_date_in']]:
        if item not in pdict.keys():
            raise ValueError(f"Parameter '{item}' not found in the database")

    return pdict
