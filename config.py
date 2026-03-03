import configparser
from pathlib import Path

script_dir = Path(__file__).parent

config = configparser.ConfigParser()
config.read(script_dir / "config.ini")




