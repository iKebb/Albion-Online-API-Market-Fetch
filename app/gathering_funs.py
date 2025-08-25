import requests
import time
import os
import pandas as pd
from datetime import datetime

def fetch_market_data(tier, items_of_interest, cities, qualities):
  """
  Fetches market data for a list of items from the Albion Online API.

  Parameters:
    items_of_interest (list)        : List of item IDs to fetch (e.g., ["T5_MAIN_CURSEDSTAFF"])
    cities (list)                   : List of cities to check (e.g., ["Thetford", "Caerleon"])
    qualities (list)                : List of qualities to fetch (e.g., [0, 1, 2, 3, 4, 5])
    API_URL (str)                   : Base API URL (e.g., "https://west.albion-online-data.com/api/v2/stats/prices/")

  Returns:
    list                            : List of dictionaries containing market data
    """
  
  fetch_time= datetime.now().strftime("%Y-%m-%d %H")          # Timestamp for the data fetch
  results= []                                                 # Result list to store data
  delay_between_requests= 1.5                                 # Seconds to wait between each request

  for item in items_of_interest:
    for city in cities:
      for quality in qualities:
        try:
          print(f">>> Fetching <{item}> in <{city}> (Q{quality})")

          URL= f"https://west.albion-online-data.com/api/v2/stats/prices/{tier}_{item}?locations={city}&qualities={quality}"
          response= requests.get(URL)

          if response.status_code== 429:
            print("Rate limit hit. Waiting 10 seconds...")
            time.sleep(10)
            response= requests.get(URL)

          if response.status_code== 200:
            data= response.json()
            if data and isinstance(data, list) and len(data)> 0:
              entry= data[0]
              results.append({
                "Item ID"             : item,
                "City"                : city,
                "Quality"             : quality,
                "sell_price_min"      : entry.get("sell_price_min", None),
                "sell_price_min_date" : entry.get("sell_price_min_date", None),
                "sell_price_max"      : entry.get("sell_price_max", None),
                "sell_price_max_date" : entry.get("sell_price_max_date", None),
                "buy_price_min"       : entry.get("buy_price_min", None),
                "buy_price_min_date"  : entry.get("buy_price_min_date", None),
                "buy_price_max"       : entry.get("buy_price_max", None),
                "buy_price_max_date"  : entry.get("buy_price_max_date", None),
                "Timestamp"           : fetch_time
              })
            else:
              results.append({
                "Item ID"             : item,
                "City"                : city,
                "Quality"             : quality,
                "sell_price_min"      : None,
                "sell_price_min_date" : None,
                "sell_price_max"      : None,
                "sell_price_max_date" : None,
                "buy_price_min"       : None,
                "buy_price_min_date"  : None,
                "buy_price_max"       : None,
                "buy_price_max_date"  : None,
                "Timestamp"           : fetch_time
              })
          else:
            print(f"Error fetching {item} in {city} (Q{quality}): {response.status_code}")

          time.sleep(delay_between_requests)

        except Exception as e:
          print(f"Exception for {item} in {city} (Q{quality}): {e}")
          results.append({
            "Item ID"             : item,
            "City"                : city,
            "Quality"             : quality,
            "sell_price_min"      : f"Error: {str(e)}",
            "sell_price_min_date" : None,
            "sell_price_max"      : None,
            "sell_price_max_date" : None,
            "buy_price_min"       : None,
            "buy_price_min_date"  : None,
            "buy_price_max"       : None,
            "buy_price_max_date"  : None,
            "Timestamp"           : fetch_time
          })

  return results



def save_market_data(market_data, item_name):
  """
  Saves market data to a CSV file with timestamped filename.
  Parameters:

    market_data (list|dict)         : Market data to be saved, compatible with pd.DataFrame construction
    item_name (str)                 : Name of the item, used in the output filename

  Returns:
    None                            : Outputs a CSV file to the specified directory and prints confirmation

  Side Effects:
    - Creates 'output' directory if it does not exist
    - Writes a CSV file named '{item_name}_{timestamp}.csv'
    - Prints a sample of 10 rows from the data
    - Prints confirmation message with output path

  Example:
    save_market_data(market_data, "cursed_staff")
    # Output: Market data saved to output/cursed_staff_2025-04-05_10-30-22.csv
  """

  output_dir= "output"
  today= datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  column_order= [
    "Item ID", "City", "Quality",
    "sell_price_min", "sell_price_min_date",
    "sell_price_max", "sell_price_max_date",
    "buy_price_min", "buy_price_min_date",
    "buy_price_max", "buy_price_max_date",
    "Timestamp"
  ]

  df= pd.DataFrame(market_data)
  df= df[column_order]

  print(df.sample(10))

  os.makedirs(output_dir, exist_ok=True)
  output_file= os.path.join(output_dir, f"{item_name}_{today}.csv")
  df.to_csv(output_file, index=False)

  print(f"Market data saved to {output_file}")