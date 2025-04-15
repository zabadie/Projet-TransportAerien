import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time

# Convertir une date au format timestamp (en ms)
def date_to_timestamp(date):
    return int(datetime.strptime(date, "%Y-%m-%d").timestamp() * 1000)

# Récupérer les vols d'une page donnée
def get_flights(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    vols = []

    for row in soup.select("tr.tt-row"):
        try:
            heure = row.select_one("td.tt-d").text.strip()
            destination = row.select_one("td.tt-ap").text.strip()
            compagnie = row.select_one("td.tt-al").text.strip()
            statut = row.select_one("td.tt-s").text.strip()
            vols.append({
                "heure": heure,
                "destination": destination,
                "compagnie": compagnie,
                "statut": statut
            })
        except:
            continue
    return vols


# Variables
start_date = datetime(2025, 1, 2)
end_date = datetime.today()
base_url = "https://www.avionio.com/fr/airport/ory/departures?ts={timestamp}&page=-2"

# Liste finale
all_flights = []

# Scraping par jour
current_date = start_date
while current_date <= end_date:
    print(f"Scraping {current_date.strftime('%Y-%m-%d')} ...")
    timestamp = date_to_timestamp(current_date.strftime("%Y-%m-%d"))
    url = base_url.format(timestamp=timestamp)
    flights = get_flights(url)
    all_flights.extend(flights)
    time.sleep(1)
    current_date += timedelta(days=1)

# Export CSV
df = pd.DataFrame(all_flights)
df.to_csv("vols_ory.csv", index=False, encoding="utf-8")
print("✅ Export terminé dans vols_ory.csv")
