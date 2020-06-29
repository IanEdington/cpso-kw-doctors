import json
import os
import re
import time
from pathlib import Path
from random import randint

import requests
from bs4 import BeautifulSoup

url_search = "https://doctors.cpso.on.ca/?search=general"
url_paging = "https://doctors.cpso.on.ca/Doctor-Search-Results?type=name&term="

abs_file_path = Path(os.path.abspath(__file__))
project_dir = abs_file_path.parent
data_dir = project_dir / 'data' / 'kw-docs-raw'
manifest_file = data_dir / 'manifest.json'

headers_12 = {
  "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
  "accept-language": "en-US,en;q=0.9",
  "cache-control": "max-age=0",
  "content-type": "application/x-www-form-urlencoded",
  "sec-fetch-dest": "document",
  "sec-fetch-mode": "navigate",
  "sec-fetch-site": "same-origin",
  "sec-fetch-user": "?1",
  "upgrade-insecure-requests": "1"
}


def get_page_file_name(page_num):
    return data_dir / f'doctors_page_{page_num}.html'


def save_search_page(current_page_num, content):
    Path(get_page_file_name(current_page_num)).write_bytes(content)


def save_already_saved_pages(already_saved_pages):
    Path(manifest_file).write_text(json.dumps({
        "already_saved_pages": already_saved_pages
    }))


def crawl_cpso():
    # create data dir if doesn't already exist
    data_dir.mkdir(parents=True, exist_ok=True)

    # get existing saved pages
    # - format: [True, True, False]
    #   - where the array is the length of pages -1
    #   - index is the page number -1
    #   - value is if the page has been successfully saved
    already_saved_pages = None
    if manifest_file.exists():
        with manifest_file.open() as f:
            already_saved_pages = json.load(f)["already_saved_pages"]

    # get HTML to generate POST data
    with requests.Session() as session:
        r_search_page = session.get(url_search)
        soup_search_page = BeautifulSoup(r_search_page.content, 'html.parser')

        form_prefix = "p$lt$ctl01$pageplaceholder$p$lt$ctl02$CPSO_AllDoctorsSearch$"
        search_payload = {
            "__CMSCsrfToken": soup_search_page.find("input", id="__CMSCsrfToken")['value'],
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": soup_search_page.find("input", id="__VIEWSTATE")['value'],
            "lng": "en-CA",
            "__VIEWSTATEGENERATOR": soup_search_page.find("input", id="__VIEWSTATEGENERATOR")['value'],
            "searchType": "general",
            form_prefix + "advancedState": "closed",
            form_prefix + "ConcernsState": "closed",
            form_prefix + "txtLastNameQuick": "",
            form_prefix + "txtCPSONumber": "",
            form_prefix + "chkActiveDoctors": "on",
            form_prefix + "txtCPSONumberGeneral": "",
            form_prefix + "txtLastName": "",
            form_prefix + "ddCity": "1515",
            form_prefix + "txtPostalCode": "",
            form_prefix + "grpGender": "",
            form_prefix + "grpDocType": "rdoDocTypeFamly",
            form_prefix + "ddHospitalCity": "",
            form_prefix + "ddHospitalName": "-1",
            form_prefix + "ddLanguage": "08",
            form_prefix + "chkPracticeRestrictions": "on",
            form_prefix + "chkPendingHearings": "on",
            form_prefix + "chkPastHearings": "on",
            form_prefix + "chkHospitalNotices": "on",
            form_prefix + "chkConcerns": "on",
            form_prefix + "chkNotices": "on",
            form_prefix + "txtExtraInfo": "",
            form_prefix + "btnSubmit1": "Submit",
        }

        # get the first page of results
        current_page_index = 0

        randomly_wait()
        session.post(url_search, data=search_payload)
        r_first_page = session.get(url_paging)

        # get the range of pages:
        soup_first_page = BeautifulSoup(r_first_page.content, 'html.parser')
        last_page_index = int(soup_first_page.find('a', id=re.compile("lnbLastPage")).contents[1]) - 1

        # create the already saved pages array
        if already_saved_pages is None:
            already_saved_pages = [False] * last_page_index
            save_already_saved_pages(already_saved_pages)
        if len(already_saved_pages) != last_page_index:
            raise Exception('side of file is now different')

        if not already_saved_pages[current_page_index]:
            save_search_page(current_page_index, r_first_page.content)
            already_saved_pages[current_page_index] = True
            save_already_saved_pages(already_saved_pages)

        current_page_index += 1

        # Loop through remaining pages
        soup_current = soup_first_page
        while current_page_index <= last_page_index:
            if already_saved_pages[current_page_index]:
                current_page_index += 1
                continue

            payload_paging = {
                "__CMSCsrfToken": soup_current.find("input", id="__CMSCsrfToken")['value'],
                "__VIEWSTATE": soup_current.find("input", id="__VIEWSTATE")['value'],
                "__VIEWSTATEGENERATOR": soup_current.find("input", id="__VIEWSTATEGENERATOR")['value'],
                "__EVENTTARGET": f"p$lt$ctl01$pageplaceholder$p$lt$ctl03$CPSO_DoctorSearchResults$rptPages$ctl0{current_page_index}$lnbPage",
                "lng": 'en-CA',
                "p$lt$ctl04$pageplaceholder$p$lt$ctl03$CPSO_DoctorSearchResults$hdnCurrentPage": current_page_index
            }
            randomly_wait()
            r_current = session.post(url_paging, data=payload_paging)
            if r_current.status_code != 200:
                Path("./error.html").write_bytes(r_current.content)
                raise Exception("error with getting page")
            soup_current = BeautifulSoup(r_current.content, 'html.parser')

            save_search_page(current_page_index, r_current.content)
            already_saved_pages[current_page_index] = True
            save_already_saved_pages(already_saved_pages)

            # TODO: check if next index need to hit the "next group"
            # switch to the next group
            # payload_paging[
            #     '__EVENTTARGET'] = 'p$lt$ctl04$pageplaceholder$p$lt$ctl03$CPSO_DoctorSearchResults$lnbNextGroup'
            # randomly_wait()
            # r = session.post(url_paging, data=payload_paging)
            # soup = BeautifulSoup(r.content, 'html.parser')

        print('script completed')



def randomly_wait():
    time.sleep(randint(1, 3))


crawl_cpso()
