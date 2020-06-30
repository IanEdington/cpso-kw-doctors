import csv
import json

import utils

"""
improvements:
-
"""

# import json convert to csv
with utils.DOCTORS_OVERVIEW_JSON_FILE.open() as json_file:
    doctors = json.load(json_file)

with utils.DOCTORS_OVERVIEW_CSV_FILE.open('w', newline='') as csv_file:
    fieldnames = ["first_name", "last_name", "details_url", "cpso", "location", "phone", "concerns",
                  "specializations"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for doctor in doctors:
        writer.writerow(doctor)
