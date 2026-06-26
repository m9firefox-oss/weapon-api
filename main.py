from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ImageRequest(BaseModel):
    image_url: str

@app.post("/identify_weapon")
def identify_weapon(req: ImageRequest):
    # 今は仮の固定レスポンス
    return {
        "weapon_name": "ロムフェーヤ",
        "status": "success"
    }

from googlesearch import search
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()

@app.get("/weapon_data")
def get_weapon_data(name: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    query = f"{name} site:gamewith.jp"
    link = None
    try:
        for url in search(query, num_results=5):
            if "gamewith.jp" in url:
                link = url
                break
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

    if not link:
        return {"error": "GameWith page not found"}

    page = requests.get(link, headers=headers).text
    s = BeautifulSoup(page, "html.parser")

    weapon_name = s.find("h1").text.strip() if s.find("h1") else name
    image_url = s.find("img")["src"] if s.find("img") else None

    table = s.find("table")
    if not table:
        return {"error": "Weapon table not found"}

    rows = table.find_all("tr")
    element = rows[0].find_all("td")[1].text.strip()
    weapon_type = rows[1].find_all("td")[1].text.strip()
    rarity = rows[2].find_all("td")[1].text.strip()

    return {
        "weapon_name": weapon_name,
        "image_url": image_url,
        "element": element,
        "weapon_type": weapon_type,
        "rarity": rarity,
        "source_url": link
    }
