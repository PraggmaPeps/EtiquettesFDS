#!/usr/bin/env python3
"""
VERSION SIMPLE - Lire Excel et créer un dictionnaire
"""
import sys

import pandas as pd


def excel_to_dict(fichier_excel, feuille=0):
    """
    Version simple et directe

    Args:
        fichier_excel: Chemin vers le fichier Excel
        feuille: Index (0, 1, 2...) ou nom de la feuille

    Returns:
        dict: {cle_sans_espaces: valeur}
    """

    # Lire le fichier Excel
    df = pd.read_excel(fichier_excel, sheet_name=feuille)

    # Créer le dictionnaire
    dictionnaire = {}

    # Parcourir chaque ligne
    for index, row in df.iterrows():
        # Colonne 0 = clé
        cle = row.iloc[0]

        # Ignorer si vide
        if pd.isna(cle) or str(cle).strip() == '':
            continue

        # Nettoyer la clé (enlever espaces)
        cle_clean = str(cle).replace(' ', '')

        # Colonne 1 = valeur
        valeur = row.iloc[1]

        # Convertir NaN en None
        if pd.isna(valeur):
            valeur = None

        # Ajouter au dictionnaire
        dictionnaire[cle_clean] = valeur

    return dictionnaire



# ============================================
# VERSION AVEC NETTOYAGE AVANCÉ
# ============================================

def excel_to_dict_avance(fichier_excel, feuille=0,
                         nettoyer_cle=True, nettoyer_valeur=True):
    """
    Version avec options de nettoyage

    Args:
        nettoyer_cle: Enlever espaces de la clé
        nettoyer_valeur: Enlever espaces début/fin de la valeur
    """

    df = pd.read_excel(fichier_excel, sheet_name=feuille)
    dictionnaire = {}

    for index, row in df.iterrows():
        cle = row.iloc[0]

        # Ignorer lignes vides
        if pd.isna(cle) or str(cle).strip() == '':
            continue

        # Nettoyer la clé
        cle = str(cle)
        if nettoyer_cle:
            cle = cle.replace(' ', '').replace('\n', '').replace('\t', '')

        # Récupérer la valeur
        valeur = row.iloc[1]

        if pd.isna(valeur):
            valeur = None
        elif isinstance(valeur, str) and nettoyer_valeur:
            valeur = valeur.strip()

        dictionnaire[cle] = valeur

    return dictionnaire


# ============================================
# VERSION POUR PLUSIEURS COLONNES
# ============================================

def excel_to_dict_multi_colonnes(fichier_excel, feuille=0,
                                 col_cle=0, col_valeur=1):
    """
    Version flexible pour choisir les colonnes

    Args:
        col_cle: Index de la colonne clé (0, 1, 2...)
        col_valeur: Index de la colonne valeur
    """

    df = pd.read_excel(fichier_excel, sheet_name=feuille)
    dictionnaire = {}

    for index, row in df.iterrows():
        cle = row.iloc[col_cle]

        if pd.isna(cle) or str(cle).strip() == '':
            continue

        cle_clean = str(cle).replace(' ', '')
        valeur = row.iloc[col_valeur]

        if pd.isna(valeur):
            valeur = None

        dictionnaire[cle_clean] = valeur

    return dictionnaire


# ============================================
# VERSION AVEC NOMS DE COLONNES
# ============================================

def excel_to_dict_par_nom(fichier_excel, feuille=0,
                          nom_col_cle='Code', nom_col_valeur='Description'):
    """
    Version utilisant les noms de colonnes
    """

    df = pd.read_excel(fichier_excel, sheet_name=feuille)
    dictionnaire = {}

    for index, row in df.iterrows():
        cle = row[nom_col_cle]

        if pd.isna(cle) or str(cle).strip() == '':
            continue

        cle_clean = str(cle).replace(' ', '')
        valeur = row[nom_col_valeur]

        if pd.isna(valeur):
            valeur = None

        dictionnaire[cle_clean] = valeur

    return dictionnaire


# ============================================
# EXEMPLE COMPLET POUR FDS
# ============================================

def charger_pictogrammes_fds(fichier_excel="pictogrammes_ghs.xlsx"):
    """
    Charger les descriptions des pictogrammes GHS depuis Excel

    Format attendu du fichier Excel:
    Colonne A: Code (GHS01, GHS02, etc.)
    Colonne B: Description (Explosif, Inflammable, etc.)
    """

    return excel_to_dict(fichier_excel)


# ============================================
# EXEMPLES D'UTILISATION
# ============================================

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <chemin_xls>")
        sys.exit(1)

    chemin_xls = sys.argv[1]
    # Exemple 1: Usage basique
    mon_dict = excel_to_dict(chemin_xls)
    print(mon_dict)

