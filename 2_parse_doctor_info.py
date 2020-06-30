import json
import re

import htmlmin
from bs4 import BeautifulSoup

import utils as utils


def parse_doctor(doctor_soup):
    name_and_url = doctor_soup.find('a')
    name = name_and_url.text.split(',')
    first_name = name[1].strip()
    last_name = name[0].strip()
    details_url = name_and_url.get('href')

    cpso = re.search(r'CPSO#: (\d*)', doctor_soup.text).groups()[0]

    location_phone_fax = doctor_soup.find('h4', text=re.compile("Location of Practice:")).next_sibling.text
    location = re.split(r"Phone:|Fax:", location_phone_fax)[0].strip()
    phone_raw = re.search(r'Phone: *([-\d .()]*)', location_phone_fax)
    phone = ''
    if (phone_raw is not None):
        phone = phone_raw.groups()[0].strip()
    else:
        print('no phone found')

    concerns_raw = doctor_soup.find(text=re.compile("Concerns or additional info:"))
    concerns = []
    if concerns_raw is not None:
        concerns = [x for x in map(lambda x: x.text.strip(), concerns_raw.next_sibling.contents)]

    specializations_raw = doctor_soup.find('h4', text=re.compile(r'Area\(s\) of Specialization:'))
    specializations = []
    if specializations_raw is not None:
        specializations = [x.strip() for x in specializations_raw.next_sibling.text.split(',')]

    return {
        "first_name": first_name,
        "last_name": last_name,
        "details_url": details_url,
        "cpso": cpso,
        "location": location,
        "phone": phone,
        "concerns": concerns,
        "specializations": specializations
    }


def parse_file(file):
    white_space_file = re.sub(r"\s|<br\s*>|<br\s*/>|&nbsp;", " ", file)
    minified_file = htmlmin.minify(white_space_file, remove_empty_space=True, remove_all_empty_space=True) \
        .replace("<strong>", "") \
        .replace("</strong>", "")

    soup = BeautifulSoup(minified_file, 'html.parser')
    doctor_search_results = soup.find('div', class_="doctor-search-results")
    return [parse_doctor(doctor_soup) for doctor_soup in doctor_search_results.children]


doctors = []

for file_number in range(0, 36):
    current_file = utils.get_raw_data_file_path(file_number)
    if current_file.exists():
        doctors.extend(parse_file(current_file.read_text()))

# save file as csv
utils.DOCTORS_OVERVIEW_JSON_FILE.write_text(json.dumps(doctors))

print('completed')
