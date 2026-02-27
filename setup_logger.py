import logging
import os
from datetime import datetime


def setup_logger(name):
    """Configure un logger propre pour votre script"""
    # Créer le dossier logs
    os.makedirs('logs', exist_ok=True)

    # Nom du fichier avec date
    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f'logs/{name}_{date}.log'

    # Créer le logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Fichier : tous les détails
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s'
    ))

    # Console : messages importants seulement
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(levelname)-8s | %(message)s'))

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

