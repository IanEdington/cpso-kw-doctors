from pathlib import Path

from deepdiff import DeepHash

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'kw-docs-raw'
DOCTORS_OVERVIEW_JSON_FILE = DATA_DIR / 'doctors-overview.json'
DOCTORS_OVERVIEW_CSV_FILE = DATA_DIR / 'doctors-overview.csv'
DOCTOR_LOCATION_DATA_DIR = DATA_DIR / 'location-data'


def get_hash_of_obj(hashable_description):
    return DeepHash(hashable_description)[hashable_description]


def get_raw_data_file_path(page_num):
    return RAW_DATA_DIR / f'doctors_page_{page_num}.html'


def get_location_data_file(address):
    return DOCTOR_LOCATION_DATA_DIR / f'location_{get_hash_of_obj(address)}.json'
