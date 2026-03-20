# eBay Webscraping

The `ebay-dl.py` file scrapes data from eBay and creates a .json file as the default output. If specified in the command line with the argument `--csv` and `--json`, the code will output both a .csv file and .json file with a list of the following keys:
- `name` will contain the name of the item
- `status` will contain a string stating whether the item is "Brand New", "Refurbished", "Pre-owned", etc.
- `price` will contain the price of the item in dollars. Price will be stored as strings with dollar signs shown as this is more readable than cents stored as integers. 
- `items_sold` will contain the number of items sold (as an integer)
- `free_returns` will contain a boolean value of 'true' or 'false' for whether the item has free returns
- `shipping`will contain the price of shipping the item in cents, stored as an integer; if the item has free shipping, then this value is 0

To run the `ebay-dl.py` file, first enter the following lines in your terminal:
```
$ cd webscraping-ebay
$ pip3 install argparse requests playwright bs4
$ playwright install
```
Then, execute the code with your search term:
```
$ python3 ebay-dl.py '<search term>' --csv --json
```

Find the CSCI040 project instructions here: https://github.com/mikeizbicki/cmc-csci040/tree/2026spring/project_02_webscraping
