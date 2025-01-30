import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os


# Funktion zum Abrufen und Parsen einer Seite
def fetch_page(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Fehler beim Abrufen der URL: {url} - {e}")
        return None

# Verbesserte Modellkategorisierung
def categorize_model(row):
    title = row['Title'].lower()
    manufacturer = row['Manufacturer'].lower()

    if 'audi' in manufacturer:
        if '40' in title:
            return 'A5 40 TFSI'
        elif '45' in title:
            return 'A5 45 TFSI'
        elif '2.0' in title or '2,0' in title:
            return 'A5 2.0'
        elif '3.0' in title or '3,0' in title:
            return 'A5 3.0'
        elif '35' in title:
            return 'A5 35 TFSI'
        else:
            return 'Unbekannt'
    elif 'mercedes' in manufacturer:
        if 'c 200' in title or 'c200' in title:
            return 'C200'
        elif 'c 180' in title or 'c180' in title:
            return 'C180'
        elif 'c 250' in title or 'c250' in title:
            return 'C250'
        elif 'c 220' in title or 'c220' in title:
            return 'C220'
        elif 'c 300' in title or 'c300' in title:
            return 'C300'
        elif 'c 400' in title or 'c400' in title:
            return 'C400'
        elif '43' in title:
            return 'C43'
        elif '63' in title:
            return 'C63'
        else:
            return 'Unbekannt'
    else:
        return 'Unbekannt'

# Funktion zum Scrapen eines Links
def scrape_link(base_url, manufacturer, data, max_pages=20, delay=0.5):
    for page_num in range(1, max_pages + 1):
        print(f"Verarbeite {manufacturer} - Seite {page_num}...")
        url = base_url.format(page_num)
        soup = fetch_page(url)
        if soup is None:
            print(f"Seite {page_num} konnte nicht abgerufen werden. Weiter zur nächsten Seite.")
            continue

        car_listings = soup.find_all('article', {'data-testid': 'list-item'})
        if not car_listings:
            print(f"Keine Fahrzeuge auf Seite {page_num} gefunden. Abbruch.")
            break

        for car in car_listings:
            try:
                car_id = car.get('id', 'Unbekannt')
                title = car.find('a', class_='ListItem_title__ndA4s').text.strip()
                price = car.find('p', class_='Price_price__APlgs').text.strip()
                mileage = car.find('span', {'data-testid': 'VehicleDetails-mileage_road'}).text.strip()
                location = car.find('span', class_='SellerInfo_address__leRMu').text.strip() if car.find('span', class_='SellerInfo_address__leRMu') else "Unbekannt"
                details = car.find('div', class_='VehicleDetailTable_container__XhfV1')
                
                if details:
                    transmission = details.find('span', {'data-testid': 'VehicleDetails-transmission'}).text.strip()
                    year = details.find('span', {'data-testid': 'VehicleDetails-calendar'}).text.strip()
                    fuel_type = details.find('span', {'data-testid': 'VehicleDetails-gas_pump'}).text.strip()
                    horsepower_raw = details.find('span', {'data-testid': 'VehicleDetails-speedometer'}).text.strip()
                    horsepower_match = re.search(r'\((\d+) PS\)', horsepower_raw)
                    horsepower = horsepower_match.group(1) if horsepower_match else "Unbekannt"
                else:
                    transmission = "Nicht verfügbar"
                    year = "Nicht verfügbar"
                    fuel_type = "Nicht verfügbar"
                    horsepower = "Nicht verfügbar"

                data.append({
                    'ID': car_id,
                    'Manufacturer': manufacturer,
                    'Title': title,
                    'Price': price,
                    'Mileage': mileage,
                    'Location': location,
                    'Transmission': transmission,
                    'Year': year,
                    'Fuel': fuel_type,
                    'Horsepower': horsepower
                })
            except AttributeError:
                print("Fehler beim Extrahieren der Daten.")
                continue

        time.sleep(delay)

# Hauptskript
if __name__ == '__main__':
    links = [
        ('Mercedes-Benz', 'https://www.autoscout24.de/lst/mercedes-benz?atype=C&body=2&cat=ma47gr100056&cy=D&damaged_listing=exclude&desc=0&dlv_tail=true&fregfrom=2018&fregto=2023&ocs_listing=include&powertype=kw&priceto=50000&sort=standard&page={}'),
        ('Mercedes-Benz', 'https://www.autoscout24.de/lst/mercedes-benz?atype=C&body=2&cat=ma47gr100056&cy=D&damaged_listing=exclude&desc=0&dlv_tail=true&fregfrom=2015&fregto=2018&ocs_listing=include&powertype=kw&priceto=50000&sort=standard&page={}'),
        #('Audi', 'https://www.autoscout24.de/lst/audi/a5?atype=C&body=2&cy=D&damaged_listing=exclude&desc=0&fregfrom=2014&fregto=2016&ocs_listing=include&powertype=kw&page={}'),
        #('Audi', 'https://www.autoscout24.de/lst/audi/a5?atype=C&body=2&cy=D&damaged_listing=exclude&desc=0&fregfrom=2016&fregto=2023&ocs_listing=include&powertype=kw&page={}')
    ]

    data = []
    for manufacturer, url in links:
        scrape_link(url, manufacturer, data)

    df = pd.DataFrame(data)
    df['Model'] = df.apply(categorize_model, axis=1)
    df_cleaned = df.drop_duplicates(subset='ID', keep='first').copy()

    # Datenbereinigung vor dem Speichern
    df_cleaned['Price'] = df_cleaned['Price'].replace({'€': '', ',': '', ',-': '', '-': '', '\s+': '', '\.': ''}, regex=True)
    df_cleaned['Price'] = pd.to_numeric(df_cleaned['Price'], errors='coerce')
    
    df_cleaned['Mileage'] = df_cleaned['Mileage'].replace({' km': '', '\.': ''}, regex=True)
    df_cleaned['Mileage'] = pd.to_numeric(df_cleaned['Mileage'], errors='coerce')
    
    df_cleaned['Year'] = pd.to_datetime(df_cleaned['Year'], format='%m/%Y', errors='coerce')

    script_dir = os.path.dirname(os.path.abspath(__file__))  # Pfad der .py-Datei
    output_file = os.path.join(script_dir, 'autoscout24_vehicles.csv')

    df_cleaned.to_csv(output_file, index=False, sep=';', encoding='utf-8')
    print(f"Scraping abgeschlossen. Datei gespeichert unter: {output_file}")