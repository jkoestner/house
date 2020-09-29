"""
Zillow parser.

Parses the Zillow website
"""
import pandas as pd
import requests
from lxml import html


def parse(zipcode, filter=None, fav=None):
    """Parse the Zillow website for house listings.

    Parameters
    ----------
    zipcode : int
        zipcode to be searched
    filter : {newest, cheapest} or None
        type of results that should be returned.
            newest: returns the most recent results
            cheapest: returns the lowest price results
            None: returns the results with no set order
    fav : int
        value of provided search result in favorites

    Returns
    -------
    properties_list : DataFrame
        list of properties from Zillow
    """
    favs = {
        1: "https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22mapBounds%22%3A%7B%22west%22%3A-77.6"
        + "4705753271484%2C%22east%22%3A-77.38956546728515%2C%22south%22%3A37.47601162113677%2C%22north%22%3A37"
        + ".67274311749038%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%"
        + "3A%7B%22value%22%3A%22globalrelevanceex%22%7D%7D%2C%22isListVisible%22%3Atrue%2C%22usersSearchTerm%22%3Anul"
        + "l%2C%22customRegionId%22%3A%22e22635f6fdX1-CR15oguga8khw1q_v24ah%22%7D"
    }

    if fav is not None:
        url = favs[fav]

    else:
        if filter == "newest":
            url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/days_sort".format(
                zipcode
            )
        elif filter == "cheapest":
            url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/pricea_sort/".format(
                zipcode
            )
        else:
            url = "https://www.zillow.com/homes/for_sale/{0}_rb/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy".format(
                zipcode
            )

    properties_list = pd.DataFrame()
    url_error = 0
    i = 1

    while url_error < 1:

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.8",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        }
        url_page = (
            "https://www.zillow.com/homes/for_sale/2_p/?searchQueryState=%7B%22"
            + "mapBounds%22%3A%7B%22west%22%3A-77.67296870807589%2C%22east%22%3"
            + "A-77.4154766426462%2C%22south%22%3A37.49591372350485%2C%22north%22"
            + "%3A37.69259270012567%7D%2C%22customRegionId%22%3A%22e22635f6fdX1-"
            + "CR15oguga8khw1q_v24ah%22%2C%22isMapVisible%22%3Atrue%2C%22filterS"
            + "tate%22%3A%7B%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A"
            + "12%2C%22pagination%22%3A%7B%22currentPage%22%3A"
            + str(i)
            + "%7D%7D"
        )
        response = requests.get(url_page, headers=headers)
        print(response.status_code)
        parser = html.fromstring(response.text)
        search_results = parser.xpath("//div[@id='grid-search-results']//article")

        for properties in search_results:
            raw_address = properties.xpath(
                ".//address[@class='list-card-addr']//text()"
            )
            address = "".join(raw_address).strip()
            raw_price = properties.xpath(".//div[@class='list-card-price']//text()")
            price = "".join(raw_price).strip()
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
            }
            properties_list = properties_list.append(properties, ignore_index=True)

        i = i + 1
        url_page = (
            "https://www.zillow.com/homes/for_sale/2_p/?searchQueryState=%7B%22"
            + "mapBounds%22%3A%7B%22west%22%3A-77.67296870807589%2C%22east%22%3"
            + "A-77.4154766426462%2C%22south%22%3A37.49591372350485%2C%22north%22"
            + "%3A37.69259270012567%7D%2C%22customRegionId%22%3A%22e22635f6fdX1-"
            + "CR15oguga8khw1q_v24ah%22%2C%22isMapVisible%22%3Atrue%2C%22filterS"
            + "tate%22%3A%7B%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A"
            + "12%2C%22pagination%22%3A%7B%22currentPage%22%3A"
            + str(i)
            + "%7D%7D"
        )
        try:
            response = requests.get(url_page, headers=headers)
            parser = html.fromstring(response.text)
            search_results = parser.xpath("//div[@id='grid-search-results']//article")
            if search_results == []:
                url_error = 1
        except:
            url_error = 1
            pass

    return properties_list
