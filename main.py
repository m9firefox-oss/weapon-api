from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# ① 画像判定API用のモデル（残す）
class ImageRequest(BaseModel):
    image_url: str

# ② 画像判定API（残す）
@app.post("/identify_weapon")
def identify_weapon(req: ImageRequest):
    return {
        "weapon_name": "ロムフェーヤ",
        "status": "success"
    }

# ③ GameWith スクレイピングAPI（完全版）
@app.get("/weapon_data")
def get_weapon_data(name: str):
    headers = {"User-Agent": "Mozilla/5.0"}

    # 1. GameWith の武器一覧ページを取得
    list_url = "https://gamewith.jp/granbluefantasy/article/list/weapon"
    list_html = requests.get(list_url, headers=headers).text
    list_soup = BeautifulSoup(list_html, "html.parser")

    # 2. 全武器リンクを取得（現行 GameWith 構造に対応）
    weapon_links = list_soup.select("a.card__link")
    target_url = None

    for a in weapon_links:
        # 武器名は .card__title に入っている
        title_tag = a.select_one(".card__title")
        if not title_tag:
            continue

        weapon_name = title_tag.text.strip()

        # 部分一致で検索
        if name in weapon_name:
            target_url = "https://gamewith.jp" + a["href"]
            break

    if not target_url:
        return {"error": "Weapon not found in list"}

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
