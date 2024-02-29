from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import datetime
import time
import os
import zipfile
from io import StringIO
import re
import sys
import pandas as pd

download_path = os.path.join('/', 'Users', 'brandonkaplan', 'Desktop', 'FINTECH533','basic_web_scrape')

query_years = list(
    range(
        datetime.date.today().year - 1,
        datetime.date.today().year - 4,
        -1
    )
)

chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory": download_path}
chromeOptions.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chromeOptions)

driver.get("https://cdr.ffiec.gov/public/PWS/DownloadBulkData.aspx")
driver.find_element(By.CSS_SELECTOR, '#ListBox1 > option:nth-child(2)').click()

year_selection = "//option[text()='{}']"
filename_template = "FFIEC CDR Call Bulk Subset of Schedules {}.zip"

for query_year in query_years:
    driver.find_element(
        By.XPATH,
        value=year_selection.format(query_year)
    ).click()
    driver.find_element(By.TAG_NAME, value='body').send_keys(Keys.PAGE_UP)
    time.sleep(0.5)
    driver.find_element(
        By.XPATH,
        "//input[@value='Download']"
    ).click()
    driver.find_element(By.TAG_NAME, value='body').send_keys(Keys.PAGE_DOWN)
    time.sleep(0.5)

    start_time = datetime.datetime.now()
    timeout = 25
    while not os.path.isfile(filename_template.format(query_year)):
        print(
            "Waiting for " + \
            filename_template.format(query_year) + \
            " to download"
        )
        time.sleep(1)
        if (datetime.datetime.now() - start_time).seconds > timeout:
            break

    with zipfile.ZipFile(filename_template.format(query_year), 'r') as zip_ref:
        zip_ref.extractall(os.getcwd())

driver.quit()

extracted_call_files = [
    filename for filename in os.listdir(
        os.getcwd()) if filename.startswith("FFIEC CDR Call Subset ")
]

call_data_dict = {}

for call_file in sorted(extracted_call_files):

    f = open(call_file, "r")
    call_file_lines = f.readlines()
    f.close()

    split_str = "Submission Updated On"

    call_file_lines[0] = re.split(split_str, call_file_lines[0])[0] + \
           split_str + \
           re.split("\t{12}", call_file_lines[1])[1]

    del call_file_lines[1]

    call_data_df = pd.read_csv(
        StringIO(re.sub("\t\n", "\n", "".join(call_file_lines))),
        sep="\t",
        dtype={'AUDIT INDICATOR': str}
    )

    call_data_year = re.split(
        "\(", re.split("Schedules ", call_file)[1]
    )[0]

    if re.search("(1 of 2)", call_file) is None:
        if re.search("(2 of 2)", call_file) is None:
            print("strange filename detected:")
            print(call_file)
            sys.exit(1)
        else:
            call_data_dict[call_data_year] = call_data_dict[
                call_data_year
            ].merge(
                call_data_df,
                how='inner',
                on= ["Reporting Period End Date", "IDRSSD"]
            )

    else:
        call_data_dict[call_data_year] = call_data_df

full_call_data = pd.concat(call_data_dict)

full_call_data.to_csv("scraped_call_data.csv", index=False)