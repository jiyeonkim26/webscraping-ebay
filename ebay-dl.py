
import argparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import csv

# downloads the browser and runs the html


def download_html_and_run_javascript(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        try:
            page.goto(url, timeout=60000)
            page.wait_for_selector('li.s-card', timeout=10000)
            page.wait_for_timeout(2000)
            return page.content()
        except Exception:
            return None


def parse_itemssold(s):
    '''
    Takes as input a string and returns the number of items sold,
    as specified in the string.

    >>> parse_itemssold('38 sold')
    38
    >>> parse_itemssold('14 watchers')
    0
    >>> parse_itemssold('Almost gone')
    0
    '''
    numbers = ''
    for char in s:
        if char in '1234567890':
            numbers += char
    if 'sold' in s:
        return int(numbers)
    else:
        return 0


def parse_shipping(text):
    '''
    Takes as input strings and returns the price of shipping the
    item in cents, stored as an integer; if the item has free
    shipping, then this value should be 0.

    >>> parse_shipping('+$17.55 delivery')
    17.55
    >>> parse_shipping('Free delivery in 2-4 days')
    0
    >>> parse_shipping('Free delivery')
    0
    '''
    text = text.strip().lower()

    if '+' in text:
        start = text.index('+') + 1  # move past '+'

        # skip non-digit characters (like '$' or spaces)
        while start < len(text) and not (text[start].isdigit() or text[start] == '.'):
            start += 1

        number = ''
        for ch in text[start:]:
            if ch.isdigit() or ch == '.':
                number += ch
            else:
                break

        if number:
            return int(float(number) * 100)

    elif 'free delivery' in text:
        return 0

    return 0

# this if statement says only run the code below when the python file
# is run 'normally' where normally means not in the doctests


if __name__ == '__main__':

    # gets the command line arguments
    parser = argparse.ArgumentParser(description="download information from ebay and convert to JSON.")
    parser.add_argument('search_term')
    parser.add_argument('--num_pages', type=int, default=10)
    parser.add_argument('--json', action='store_true', help='save output as JSON')
    parser.add_argument('--csv', action='store_true', help='save output as CSV')
    args = parser.parse_args()
    print('args.search_term=', args.search_term)

    # list of all items found in all ebay webpages
    items = []

    # loop over the ebay webpages
    for page_number in range(1, args.num_pages + 1):
        # build the url
        url = 'https://www.ebay.com/sch/i.html?_nkw='
        url += args.search_term
        url += '&_sacat=0&_from=R40&_pgn='
        url += str(page_number)
        url += '&rt=nc'
        print('url=', url)

        # download the html
        html = download_html_and_run_javascript(url)

        # process the html
        soup = BeautifulSoup(html, 'html.parser')

        # loop over the items in the page
        tags_items = soup.select('li.s-card')
        print('len(tags_items)=', len(tags_items))

        for tag_item in tags_items:

            name = None
            tag_name = tag_item.select_one('.su-styled-text.primary.default')
            if tag_name is None:
                continue
            if "Shop on eBay" in tag_name.text:
                continue
            name = tag_name.get_text(strip=True)

            status = None
            tags_status = tag_item.select('.s-card__subtitle')
            status = tags_status[-1].get_text(strip=True) if tags_status else None

            price = None
            tags_price = tag_item.select('.s-card__price')
            price = tags_price[0].get_text(strip=True) if tags_price else None

            items_sold = 0
            free_returns = False
            shipping = None

            item_attributes = tag_item.select('.s-card__attribute-row')

            for line in item_attributes:
                line_text = line.text.lower()

                if 'sold' in line_text:
                    items_sold = parse_itemssold(line.text)
                elif 'free returns' in line_text:
                    free_returns = True
                elif 'shipping' in line_text or 'delivery' in line_text:
                    shipping = parse_shipping(line.text)

            item = {
                'name': name,
                'status': status,
                'price': price,
                'items_sold': items_sold,
                'free_returns': free_returns,
                'shipping': shipping
            }

            items.append(item)

    filename = args.search_term.replace(" ", "_")

    # JSON output
    if args.json:
        filename_json = filename + ".json"
        with open(filename_json, "w", encoding='utf-8') as f:
            json.dump(items, f, indent=4)
        print(f"{len(items)} items saved to {filename_json}")

    # CSV output
    if args.csv:
        filename_csv = filename + ".csv"
        with open(filename_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                'name',
                'status',
                'price',
                'items_sold',
                'free_returns',
                'shipping'
            ])
            writer.writeheader()
            writer.writerows(items)

        print(f"{len(items)} items saved to {filename_csv}")

    if not args.json and not args.csv:
        args.json = True
