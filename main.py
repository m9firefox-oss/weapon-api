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

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI

app = FastAPI()

@app.get("/weapon_data")
def get_weapon_data(name: str):
    headers = {"User-Agent": "Mozilla/5.0"}

    # GameWith の内部検索
    search_url = f"https://gamewith.jp/search?q={name}"
    search_html = requests.get(search_url, headers=headers).text
    search_soup = BeautifulSoup(search_html, "html.parser")

    # 検索結果の最初のカードリンクを取得
    first_link = search_soup.select_one("a.card__link")
    if not first_link:
        return {"error": "GameWith page not found"}

    link = "https://gamewith.jp" + first_link["href"]

    # 武器ページを取得
    page = requests.get(link, headers=headers).text
    s = BeautifulSoup(page, "html.parser")

    # 武器名
    weapon_name = s.find("h1").text.strip() if s.find("h1") else name

    # 武器画像
    image_tag = s.select_one("div.article__image img")
    image_url = image_tag["src"] if image_tag else None

    # 属性・武器種・レアリティ
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
