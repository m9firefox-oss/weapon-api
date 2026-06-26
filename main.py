from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import os

app = FastAPI()

INDEX_FILE = "weapon_index.json"

# -----------------------------
# 画像判定API（仮）
# -----------------------------
class ImageRequest(BaseModel):
    image_url: str

@app.post("/identify_weapon")
def identify_weapon(req: ImageRequest):
    return {
        "weapon_name": "ロムフェーヤ",
        "status": "success"
    }

# -----------------------------
# 辞書生成API（SR+SSR 全武器）
# -----------------------------
@app.get("/build_weapon_index")
def build_weapon_index():
    headers = {"User-Agent": "Mozilla/5.0"}

    # SR+SSR 全武器を網羅する武器種キーワード
    keywords = ["剣", "槍", "斧", "杖", "短剣", "弓", "銃", "格闘", "楽器", "刀"]

    index = {}

    for kw in keywords:
        search_url = (
            "https://xn--bck3aza1a2if6kra4ee0hf.gamewith.jp/search?keyword="
            + urllib.parse.quote(kw)
        )
        html = requests.get(search_url, headers=headers).text
        soup = BeautifulSoup(html, "html.parser")

        for a in soup.select("a"):
            href = a.get("href", "")
            if "/article/show/" in href and "granbluefantasy" in href:
                name = a.text.strip()
                article_id = href.split("/")[-1]
                index[name] = article_id

    # JSON に保存
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return {"status": "success", "count": len(index)}

# -----------------------------
# 辞書読み込み
# -----------------------------
def load_index():
    if not os.path.exists(INDEX_FILE):
        return {}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# -----------------------------
# 武器情報取得API
# -----------------------------
@app.get("/weapon_data")
def get_weapon_data(name: str):
    headers = {"User-Agent": "Mozilla/5.0"}

    index = load_index()
    if name not in index:
        return {"error": "Weapon not found in index"}

    article_id = index[name]
    target_url = (
        f"https://xn--bck3aza1a2if6kra4ee0hf.gamewith.jp/article/show/{article_id}"
    )

    # 武器ページを取得
    page = requests.get(target_url, headers=headers).text
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
        "source_url": target_url
    }
