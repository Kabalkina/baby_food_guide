import os
import yaml
import pandas as pd

# Path to config.yaml 
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

def _load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

_config = _load_config()

DATA_PATH = _config['DATA_PATH']
GROQ_CLIENT = _config['GROQ_CLIENT']
QD_CLIENT = _config['QD_CLIENT']
MODEL = _config['MODEL']
EMBEDDING_DIMENSIONALITY = _config['EMBEDDING_DIMENSIONALITY']
COLLECTION_NAME = _config['COLLECTION_NAME']