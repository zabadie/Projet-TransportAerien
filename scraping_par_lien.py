import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time

# Convertir une date au format timestamp (en ms)
def date_to_timestamp(date):
    return int(datetime.strptime(date, "%Y-%m-%d").timestamp() * 1000)

# Récupérer les vols d'une page donnée
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
    details = []
    base_url = "https://www.avionio.com"

    for row in soup.select("tr.tt-row"):
        try:
            heure = row.select_one("td.tt-d").text.strip()
            destination = row.select_one("td.tt-ap").text.strip()
            compagnie = row.select_one("td.tt-al").text.strip()
            statut = row.select_one("td.tt-s").text.strip()
            href = row.select_one("td.tt-f a")["href"]


            final_details = ""

            # Ajout des details par vol : terminal arrivee, depart...
            td = row.find("td", class_="tt-f")
            a_tag = td.find("a")

            if a_tag and a_tag.has_attr("href"):
                href = ""
                href = a_tag["href"]
                full_href = base_url + href
                #print(f"Acces à {href}")

                detail_vols = requests.get(full_href)
                detail_soup = BeautifulSoup(detail_vols.text, "html.parser")
                
                card_details = detail_soup.find_all("div", class_ = "card details")
                full_detail_text = []

                if card_details:
                    for card in card_details:
                        detail_parts = []

                        #Extraire les noms d aeroport
                        card_section_card_header = card.find_all("div", class_="card-section card-header")
                        for div in card_section_card_header:
                            h2_tag = div.find("h2", class_="h1")
                            if h2_tag:
                                h2_text = h2_tag.get_text(strip=True)
                                full_detail_text.append(h2_text)

                        p_tag = div.find("p")
                        if p_tag:
                            p_text = p_tag.get_text(strip=True)
                            full_detail_text.append(p_text)

                        # Extraction de tous les textes des <p> dans les card-section de card-body
                        card_body = card.find("div", class_="card-body")
                        if card_body:
                            sections = card_body.find_all("div", class_="card-section")
                            for section in sections:
                                detail_parts += [p.get_text(strip=True) for p in section.find_all("p")]
                        
                        # Extraction de tous les <p class = "h1 no-margin"> dans les card-section et card-footer
                        card_footers = card.find_all("div", class_="card-section card-footer")
                        for footer in card_footers :
                            detail_parts += [p.get_text(strip=True) for p in footer.find_all("p", class_="h1 no-margin")]
                        
                        full_detail_text += detail_parts
                        final_details = ','.join(full_detail_text)
                        details.append(final_details)
            vols.append({
                "heure": heure,
                "destination": destination,
                "compagnie": compagnie,
                "statut": statut,
                "lien":href
            })

        


        except:
            continue
    return vols, details

# Variables
start_date = datetime(2025, 1, 2)
end_date = datetime.today()
base_url = "https://www.avionio.com/fr/airport/ory/departures?ts={timestamp}&page=-2"

# Liste finale
all_flights = []
all_details = []

# Scraping par jour
current_date = start_date
while current_date <= end_date:
    #print(f"Scraping {current_date.strftime('%Y-%m-%d')} ...")
    timestamp = date_to_timestamp(current_date.strftime("%Y-%m-%d"))
    url = base_url.format(timestamp=timestamp)
    flights, details = get_flights(url)

    all_flights.extend(flights)
    all_details.extend(details)

    time.sleep(1)
    current_date += timedelta(days=1)

# Export CSV
df = pd.DataFrame(all_flights)
df_details = pd.DataFrame(all_details, columns=["aéroport départ,Horaire text,heure initiale départ,date initiale départ,statut,heure finale départ,date finale départ,terminal départ,portail départ,enregistrement départ,aéroport arrivée,Arrivée texte,heure initiale arrivée,date initiale arrivée,statut,heure finale arrivée,date finale arrivée,terminal arrivée,portail arrivée,enregistrement arrivée"])

df.to_csv("vols_ory.csv", index=False, encoding="utf-8")
df_details.to_csv("vols_ory_details.csv", index=False, encoding="utf-8")

