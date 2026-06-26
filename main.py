from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI()

class ImageRequest(BaseModel):
    image_url: str

@app.post("/identify_weapon")
def identify_weapon(req: ImageRequest):
    return {
        "weapon_name": "ロムフェーヤ",
        "status": "success"
    }

@app.get("/weapon_data")
def get_weapon_data(name: str):
    headers = {"User-Agent": "Mozilla/5.0"}

    # ★ 正しい武器一覧ページ（あなたのタブのURL）
    list_url = "https://xn--bck3aza1a2if6kra4ee0hf.gamewith.jp/article/show/74390"
    list_html = requests.get(list_url, headers=headers).text
    list_soup = BeautifulSoup(list_html, "html.parser")

    # ★ 正しいセレクタ（現行 GameWith 構造）
    weapon_links = list_soup.select("div.a-link a")
    target_url = None

    for a in weapon_links:
        title_tag = a.select_one(".a-link__text")
        if not title_tag:
            continue

        weapon_name = title_tag.text.strip()

        if name in weapon_name:
            target_url = "https://xn--bck3aza1a2if6kra4ee0hf.gamewith.jp" + a["href"]
            break

    if not target_url:
        return {"error": "Weapon not found in list"}

    # 武器ページを取得
    page = requests.get(target_url, headers=headers).text
    s = BeautifulSoup(page, "html.parser")

    weapon_name = s.find("h1").text.strip() if s.find("h1") else name

    image_tag = s.select_one("div.article__image img")
    image_url = image_tag["src"] if image_tag else None

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
        "source_url": target_url
    }
