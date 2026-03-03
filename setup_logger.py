import logging
import os
from datetime import datetime, time
from pathlib import Path
from config import config

def setup_logger(name):
    """Configure un logger propre pour votre script"""
    # Créer le dossier logs
    script_dir = Path(__file__).parent
    log_dir = os.path.join(script_dir, config['PATH']['log_dir'])
    os.makedirs(log_dir, exist_ok=True)

    purge_old_logs(log_dir)

    # Nom du fichier avec date
    date = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = (f'{log_dir}/{name}_{date}.log')

    # Créer le logger
    logger = logging.getLogger(name)
    log_level = config["SETTINGS"]["log_level"]
    logger.setLevel(getattr(logging, log_level.upper()))

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


def purge_old_logs(log_dir):
    """Supprime les fichiers .log de plus de X jours."""
    days = config['SETTINGS']['nb_days_purge_log']
    limit = time.time() - (days * 86400)  # 86400 = secondes par jour

    for log_file in Path(log_dir).glob("*.log"):
        if log_file.stat().st_mtime < limit:
            log_file.unlink()
            print(f"Supprimé : {log_file.name}")

