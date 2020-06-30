from pathlib import Path

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'kw-docs-raw'
DOCTORS_OVERVIEW_JSON_FILE = DATA_DIR / 'doctors-overview.json'


def get_raw_data_file_path(page_num):
    return RAW_DATA_DIR / f'doctors_page_{page_num}.html'

