import json
from math import ceil

import httpx
from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from scrape_parser import log_data

"""
Scaper steps:
1. Grab authentication (if needed)
2. Query the api with the correct headers or scrape manually :(
3. Grab the desired data from the api response (if in step 2 we used the api)
4. Store the data 
"""


# rate has to be equal or below 200, default is 60 because the website does it at 60
def ae_scrape(query, gender_s: tuple, headers: dict, retrival_rate=60):
    options = webdriver.EdgeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Edge(options=options)

    driver.get("https://www.ae.com/ca/en/content/help/return-policy")
    # once this element is loaded, the local storage should be populated
    WebDriverWait(driver, timeout=12, poll_frequency=2).until(
        any_text_present_in_element((By.XPATH, "//span[contains(@class, '_overlay-element_1u520t')]")))
    token = driver.execute_script("return JSON.parse(localStorage.getItem('aeotoken'))['access_token'];")
    headers["x-access-token"] = token
    headers["aeSite"] = "AEO_CA"
    headers["aeLang"] = "en_CA"

    api_query_url = f"https://www.ae.com/ugp-api/cstr/v1/search?query={query}&resultsPerPage={retrival_rate}"
    req = httpx.get(api_query_url, headers=headers)
    response = json.loads(req.text)
    if response["data"]["attributes"]["totalNumResults"] > 0:
        search_results_by_gender = response["data"]["attributes"]["filters"][1]["options"]
        matched_gender_s = [res["value"] for res in search_results_by_gender for g in gender_s if g == res["value"]]
        for gender in gender_s:
            if gender not in matched_gender_s:
                print(f"No results found for gender {gender}")
    else:
        print("No results found")
        return

    try:
        for gender in matched_gender_s:
            item_results = []
            unique_items = set()
            search_results = \
                search_results_by_gender[0 if gender == "Women" or len(search_results_by_gender) == 1 else 1]["count"]
            num_of_requests = ceil(search_results / retrival_rate)
            for i in range(1, num_of_requests + 1):
                api_query_url = f"https://www.ae.com/ugp-api/cstr/v1/search?query={query}&gender={gender}&resultsPerPage={retrival_rate}"
                if i > 1:
                    api_query_url = f"https://www.ae.com/ugp-api/cstr/v1/search?query={query}&gender={gender}&resultsPerPage={retrival_rate}&page={i}"
                response = json.loads(httpx.get(api_query_url, headers=headers).text)
                for item in response["included"]:
                    item_name = item["attributes"]["displayName"]
                    if item_name not in unique_items:
                        item_results.append(build_profile(item["attributes"]))
                        unique_items.add(item_name)
            print(f"Done extracting from api for gender {gender}")
            log_data(item_results, gender, query)
            print(f"Done logging")
    finally:
        driver.close()


def any_text_present_in_element(locator):
    def _predicate(driver):
        try:
            element_text = driver.find_element(*locator).text
            return len(element_text) > 0
        except StaleElementReferenceException:
            return False

    return _predicate


def build_profile(item_attr: dict) -> dict:
    # build item description
    item_name = item_attr["displayName"]
    regular_price = item_attr["prices"]["maxListPrice"]
    sale_price = item_attr["prices"]["maxSalePrice"]
    item_link = item_attr["productUrl"]

    des = {
        "item_name": item_name,
        "price": {
            "regular_price": "{:.2f}".format(regular_price),
            "sale_price": None if regular_price == sale_price else "{:.2f}".format(sale_price)
        },
        "item_link": "https://www.ae.com/ca/en" + item_link
    }
    return des
