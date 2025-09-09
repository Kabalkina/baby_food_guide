import os
import yaml

# Project root is one directory up from this file (app/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

def _load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

_config = _load_config()

# Build absolute paths for data
DATA_PATH = os.path.join(PROJECT_ROOT, _config['DATA_PATH'])
GROUND_TRUTH_PATH = os.path.join(PROJECT_ROOT, _config['GROUND_TRUTH_PATH'])

#GROQ_CLIENT = _config['GROQ_CLIENT']
GROQ_MODEL = _config['GROQ_MODEL']
#QD_CLIENT = _config['QD_CLIENT']
MODEL = _config['MODEL']
EMBEDDING_DIMENSIONALITY = _config['EMBEDDING_DIMENSIONALITY']
COLLECTION_NAME = _config['COLLECTION_NAME']
