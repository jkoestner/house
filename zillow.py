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
        1: "https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22mapBounds%22%3A%7B%22west%22%3A-77.64705753271484%2C%22east%22%3A-77.38956546728515%2C%22south%22%3A37.47601162113677%2C%22north%22%3A37.67274311749038%7D%2C%22mapZoom%22%3A12%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%7D%2C%22isListVisible%22%3Atrue%2C%22usersSearchTerm%22%3Anull%2C%22customRegionId%22%3A%22e22635f6fdX1-CR15oguga8khw1q_v24ah%22%7D"
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

    for i in range(5):

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, sdch, br",
            "accept-language": "en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        }
        url_page = (
            "https://www.zillow.com/homes/for_sale/2_p/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A"
            + str(i)
            + "%7D%2C%22mapBounds%22%3A%7B%22west%22%3A-78.41232395117187%2C%22east%22%3A-77.38235568945312%2C%22south%22%3A37.240232467662786%2C%22north%22%3A38.026521911858445%7D%2C%22customRegionId%22%3A%22e22635f6fdX1-CR15oguga8khw1q_v24ah%22%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%7D%2C%22isListVisible%22%3Atrue%7D"
        )
        response = requests.get(url_page, headers=headers)
        print(response.status_code)
        parser = html.fromstring(response.text)
        search_results = parser.xpath("//div[@id='grid-search-results']//article")

        for properties in search_results:
            raw_address = properties.xpath(
                ".//address[@class='list-card-addr']//text()"
            )
            raw_price = properties.xpath(".//div[@class='list-card-price']//text()")
            raw_info = properties.xpath(
                ".//div[@class='list-card-variable-text list-card-img-overlay']//text()"
            )
            raw_broker_name = properties.xpath(
                ".//div[@class='list-card-truncate']//text()"
            )
            raw_url = properties.xpath(
                ".//a[contains(@class,'list-card-link list-card-link-top-margin list-card-img')]/@href"
            )
            # raw_details = properties.xpath(".//h4//text()")
            raw_is_forsale = properties.xpath('.//div[@class="list-card-type"]//text()')
            address = " ".join(" ".join(raw_address).split()) if raw_address else None
            price = "".join(raw_price).strip() if raw_price else None
            info = "".join(raw_info) if raw_price else None
            broker = "".join(raw_broker_name).strip() if raw_broker_name else None
            # details = ' '.join(' '.join(raw_details).split()).replace(u"\xb7",',')
            property_url = "".join(raw_url) if raw_url else None
            is_forsale = "".join(raw_is_forsale) if raw_is_forsale else None
            properties = {
                "address": address,
                "price": price,
                "info": info,
                "broker": broker,
                "url": property_url,
                "sale": is_forsale,
            }
            properties_list = properties_list.append(properties, ignore_index=True)

    return properties_list
