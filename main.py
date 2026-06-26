from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = FastAPI()

# 画像判定API（仮）
class ImageRequest(BaseModel):
    image_url: str

@app.post("/identify_weapon")
def identify_weapon(req: ImageRequest):
    return {
        "weapon_name": "ロムフェーヤ",
        "status": "success"
    }

# 武器情報取得API（DuckDuckGo検索 → GameWith個別ページ）
@app.get("/weapon_data")
def get_weapon_data(name: str):
    headers = {"User-Agent": "Mozilla/5.0"}

    # 1. DuckDuckGo検索でGameWith武器ページを探す
    query = f"{name} グラブル 武器 site:gamewith.jp"
    search_url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    html = requests.get(search_url, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")

    # 2. 最初のGameWithリンクを取得（uddg= の中に本物のURLが入っている）
    target_url = None
    for a in soup.select("a.result__a"):
        href = a.get("href", "")
        if "uddg=" in href:
            real_url = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("uddg", [""])[0]
            if "gamewith.jp" in real_url and "/article/show/" in real_url:
                target_url = real_url
                break

    if not target_url:
        return {"error": "GameWith page not found from search"}

    # 3. 武器ページを取得
    page = requests.get(target_url, headers=headers).text
    s = BeautifulSoup(page, "html.parser")

    # 4. 武器名
    weapon_name = s.find("h1").text.strip() if s.find("h1") else name

    # 5. 武器画像
    image_tag = s.select_one("div.article__image img")
    image_url = image_tag["src"] if image_tag else None

    # 6. 属性・武器種・レアリティ
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
