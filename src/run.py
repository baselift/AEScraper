import scraper as s

HEADERS = {
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Chromium";v="128", "Not)A;Brand";v="24", "Microsoft Edge";v="128"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,en-CA;q=0.8",
        "Accept": "application/json"
    }

running = True
while running:
    search_query = input("Enter query: ")
    gender_query = input(f"Do you want to query both genders with search term {search_query}? (Y/N): ")
    if gender_query.upper().strip() == "Y":
        s.ae_scrape(search_query, ("Men", "Women"), HEADERS)
    elif gender_query.upper().strip() == "N":
        s.ae_scrape(search_query, ("Men",), HEADERS)
    else:
        print("Invalid response")
    cont_entering = input("Do you want to continue? (Y/N): ")
    if cont_entering.upper().strip() == "N":
        running = False