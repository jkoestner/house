"""
Zillow parser.

Parses the Zillow website
"""
import pandas as pd
import requests
from lxml import html
from ast import literal_eval
import re


def parse_url(url):
    """Parse the Zillow website for house listings.

    Parameters
    ----------
    url : str
        search string to search for

        example
        'https://www.zillow.com/charlottesville-va/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A1%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-78.79497156542969%2C%22east%22%3A-78.27998743457032%2C%22south%22%3A37.83147426157776%2C%22north%22%3A38.22253224678756%7D%2C%22savedSearchEnrollmentId%22%3A%22X1-SS4gv79i7zcd910000000000_4ixy2%22%2C%22mapZoom%22%3A11%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A30840%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22price%22%3A%7B%22max%22%3A500000%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22sch%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22sort%22%3A%7B%22value%22%3A%22mostrecentchange%22%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D'

    Returns
    -------
    properties_list : DataFrame
        dataframe of properties from Zillow
    """
    properties_list = pd.DataFrame()
    url_error = 0
    i = 1

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.8",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    }

    url = re.sub(r"currentPage%22%3A\d+", r"currentPage%22%3A" + str(i), url)

    response = requests.get(url, headers=headers)
    print(response.status_code)
    parser = html.fromstring(response.text)
    search_results = parser.xpath("//div[@id='grid-search-results']//article")
    if not search_results:
        print("no results and captcha")
        print(parser[1][0][0][0][0])
    page = parser.xpath("//div[@class='search-pagination']//text()")
    page_index = page.index(" of ")
    last_page = int(page[page_index + 1])

    while url_error < 1 and i <= last_page:

        for properties in search_results:
            try:
                latitude = literal_eval(properties.xpath("..//script//text()")[0])[
                    "geo"
                ]["latitude"]
                longitude = literal_eval(properties.xpath("..//script//text()")[0])[
                    "geo"
                ]["longitude"]
            except:
                latitude = None
                longitude = None

            raw_address = properties.xpath(
                ".//address[@class='list-card-addr']//text()"
            )
            address = "".join(raw_address).strip()
            raw_price = properties.xpath(".//div[@class='list-card-price']//text()")
            price = "".join(raw_price).strip()
            try:
                price = float(re.sub("[^\d\.]", "", price))
            except:
                price = None

            raw_info = properties.xpath(
                ".//div[@class='list-card-variable-text list-card-img-overlay']//text()"
            )
            info = "".join(raw_info).strip()
            raw_broker = properties.xpath(".//div[@class='list-card-truncate']//text()")
            broker = "".join(raw_broker).strip()
            details = properties.xpath(".//ul[@class='list-card-details']//text()")
            if len(details) >= 7:
                bed = details[0]
                bath = details[3]
                sqft = details[6]
                typ = details[9]
                try:
                    sqft = float(sqft.replace(",", ""))
                except:
                    sqft = 0

            else:
                bed = None
                bath = None
                sqft = None
            raw_property_url = properties.xpath(
                ".//a[contains(@class,'list-card-link list-card-link-top-margin list-card-img')]/@href"
            )
            property_url = "".join(raw_property_url).strip()
            raw_is_forsale = properties.xpath('.//div[@class="list-card-type"]//text()')
            is_forsale = "".join(raw_is_forsale).strip()
            if sqft == 0 or sqft is None or price is None:
                price_per_sqft = None
            else:
                price_per_sqft = price / sqft

            properties = {
                "address": address,
                "price": price,
                "info": info,
                "broker": broker,
                "bed": bed,
                "bath": bath,
                "sqft": sqft,
                "url": property_url,
                "sale": is_forsale,
                "latitude": latitude,
                "longitude": longitude,
                "price_per_sqft": price_per_sqft,
                "type": typ,
            }
            properties_list = properties_list.append(properties, ignore_index=True)

        i = i + 1
        url = re.sub(r"currentPage%22%3A\d+", r"currentPage%22%3A" + str(i), url)

        try:
            response = requests.get(url, headers=headers)
            print(response.status_code)
            parser = html.fromstring(response.text)
            search_results = parser.xpath("//div[@id='grid-search-results']//article")
            if search_results == []:
                url_error = 1
        except:
            url_error = 1
            pass

    return properties_list


def parse_url_details(url):
    """Parse the Zillow website for house listings.

    Parameters
    ----------
    url : str
        search string to search for

        example
        'https://www.zillow.com/homedetails/598-Pebblecreek-Ct-Charlottesville-VA-22901/79021376_zpid/'

    Returns
    -------
    detail_df : DataFrame
        DataFrame of property details
    """
    detail_df = pd.DataFrame()
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.8",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    }

    response = requests.get(url, headers=headers)
    print(response.status_code)
    parser = html.fromstring(response.text)
    search_results = parser.xpath(
        "//div[@class='ds-home-facts-and-features reso-facts-features sheety-facts-features']//ul"
    )
    if not search_results:
        print("no results and captcha")
        print(parser[1][0][0][0][0])

    detail = {"url": url}
    for result in search_results:
        temp = result.xpath(".//span[starts-with(@class, Text)]//text()")
        temp_dict = dict(zip(temp[::2], temp[1::2]))
        detail.update(temp_dict)

    detail_df = detail_df.append(detail, ignore_index=True)

    return detail_df
