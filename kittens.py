from bs4 import BeautifulSoup
import requests
import re
from pprint import pprint
import time
from pushbullet import Pushbullet

searchUrl = "https://www.gumtree.com/search?search_category=cats&search_location=Edinburgh&q=kitten&distance=30&min_price=&max_price=75"

kittens = {}
pb = Pushbullet("API Key", "Encryption Key");

class Kitten():
    _listing = None
    _article = None
    adId = -1
    real = False
    url = ""
    title = ""
    body = ""
    price = ""

    def __init__(self, listing):
        self._listing = listing
        self.adId = int(re.match("ad\-(\d+)", self._listing["data-q"]).group(1))
        self.url = self._listing.find("a", class_="listing-link")["href"]
        self.url = "https://www.gumtree.com/" + self.url

        self._article = BeautifulSoup(requests.get(self.url).text)
        self.title = self._article.find("h1", id="ad-title").text.strip()
        self.body = self._article.find("p", class_="ad-description").text.strip()
        self.price = self._article.find("strong", class_="ad-price").text.strip()

    def isReal(self):
        return self.uid > 0

def alert(kitten):
    title = "New kitten: {} {}".format(kitten.title, kitten.price)
    body = "{}\n{}\n{}".format(kitten.url, kitten.title, kitten.body)
    pb.push_link(title, kitten.url)
    pass

def fetchKittens():
    r  = requests.get(searchUrl)
    data = r.text
    soup = BeautifulSoup(data)
    if soup.find("ul", class_="pagination") : 
        print("Pagination present - too many kittens")

    for article in  soup.find_all("article", class_="listing-maxi"):
        try:
            kitten = Kitten(article)
            if kitten.adId not in kittens:
                print("NEW KITTEN", kitten.adId, kitten.url)
                print(kitten.title + "\n" + kitten.body)
                kittens[kitten.adId] = kitten
                alert(kitten)
            else:
                print("Repeat kitten", kitten.adId)
        except (KeyError, IndexError):
            continue

if __name__=="__main__":
    while True:
        print("Fetching...")
        fetchKittens()
        pprint(kittens)
        time.sleep(5*60)

