# excel_utils.py
import os
import sys
import openpyxl
import logging


from copy import copy


def get_column_index(ws, column_name, exit_now = False,header_row=1):
    """
    Retourne l'index (0-based) de la colonne correspondant à column_name,
    ou -1 si non trouvé.

    :param exit_now:
    :param ws: feuille openpyxl (Worksheet)
    :param column_name: nom de la colonne à chercher
    :param header_row: numéro de la ligne d'entête (défaut: 1)
    :return: index (0-based) ou -1 si non trouvé
    """
    for col, cell in enumerate(ws[header_row]):
        if cell.value == column_name:
            return col
    if exit_now:
        logger.error(f"Col {column_name} not found")
        sys.exit(1)
    return -1

