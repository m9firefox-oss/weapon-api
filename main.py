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

@app.get("/weapon_data")
def get_weapon_data(name: str):
    headers = {"User-Agent": "Mozilla/5.0"}

    # Google検索でGameWithの武器ページを探す
    query = f"{name} site:gamewith.jp"
    link = None
    for url in search(query, num_results=5):
        if "gamewith.jp" in url:
            link = url
            break

    if not link:
        return {"error": "GameWith page not found"}

    # GameWithページを取得
    page = requests.get(link, headers=headers).text
    s = BeautifulSoup(page, "html.parser")

    # 武器名
    weapon_name = s.find("h1").text.strip()

    # 武器画像（最初の画像）
    image_url = s.find("img")["src"]

    # 属性・武器種・レアリティ（最初の表）
    table = s.find("table")
    rows = table.find_all("tr")
    element = rows[0].find_all("td")[1].text.strip()
    weapon_type = rows[1].find_all("td")[1].text.strip()
    rarity = rows[2].find_all("td")[1].text.strip()

    # 奥義
    ougi_section = s.find("h2", string="奥義")
    ougi_name = ougi_section.find_next("td").text.strip()
    ougi_desc = ougi_section.find_next("p").text.strip()

    # スキル
    skills = []
    skill_headers = s.find_all("h3", string=lambda x: x and "スキル" in x)
    for h in skill_headers:
        name = h.text.strip()
        desc = h.find_next("p").text.strip()
        skills.append({"name": name, "description": desc})

    return {
        "weapon_name": weapon_name,
        "image_url": image_url,
        "element": element,
        "weapon_type": weapon_type,
        "rarity": rarity,
        "ougi": {
            "name": ougi_name,
            "description": ougi_desc
        },
        "skills": skills,
        "source_url": link
    }
