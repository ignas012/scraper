import requests
from bs4 import BeautifulSoup
import pandas as pd

class Scraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.data = {
            "Skelbimo pavadinimas": [],
            "Rajonas": [],
            "Kambarių skaičius": [],
            "Nuomos kaina": [],
            "Plotas": [],
            "Metai": []
        }

    def fetch_page(self, page_nr):
        try:
            url = self.base_url.format(page_nr)
            response = requests.get(url)
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def scrape_page(self, soup):
        titles = soup.findAll('h2', class_='title-list')
        if not titles:
            return False

        for title in titles:
            link = title.find('a')
            splited_text = link['title'].split(", ")
            self.data["Skelbimo pavadinimas"].append(splited_text[0])
            self.data["Rajonas"].append(splited_text[1])

        prices = soup.findAll('div', class_='price')
        for price in prices:
            strong = price.find('strong')
            price_text = strong.text.strip().replace(" ", "")
            self.data["Nuomos kaina"].append(price_text)

        infos = soup.findAll('div', class_='param-list')
        for info in infos:
            buto_plotas = info.find('span', title='Buto plotas (kv. m)').text.strip().replace("m²", "")
            self.data["Plotas"].append(buto_plotas)
            kamb = info.find('span', title='Kambarių skaičius').text.strip().replace("kamb.", "")
            self.data["Kambarių skaičius"].append(kamb)
            stat_metai = info.find('span', title='Statybos metai').text.strip()[:4].replace("m.", "0000")
            self.data["Metai"].append(stat_metai)

        return True

    def scrape(self):
        page_nr = 1
        while True:
            soup = self.fetch_page(page_nr)
            if soup is None or not self.scrape_page(soup):
                break
            page_nr += 1
        return pd.DataFrame(self.data)


base_url = "https://domoplius.lt/skelbimai/butai?action_type=3&address_1=461&page_nr={}&slist=157656838"
scraper = Scraper(base_url)
df = scraper.scrape()
df.to_csv('Output.csv', index=False)
