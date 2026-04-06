import requests
import os

URL = "https://raw.githubusercontent.com/yannie28/Global-Superstore/master/Global_Superstore(CSV).csv"
FILENAME = "Superstore.csv"

def download_data():
    if os.path.exists(FILENAME):
        print(f"{FILENAME} already exists. Skipping download.")
        return

    print(f"Downloading data from {URL}...")
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Check for http errors
        
        with open(FILENAME, 'wb') as file:
            file.write(response.content)
        
        print("Download complete.")
    except Exception as e:
        print(f"Error downloading data: {e}")

if __name__ == "__main__":
    download_data()
