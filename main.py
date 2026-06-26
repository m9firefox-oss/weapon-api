from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI()

# CORS（Bubble からアクセスするために必要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要なら Bubble の URL に絞ってもOK
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JSON の読み込み
JSON_PATH = os.path.join(os.path.dirname(__file__), "weapon_ssr.json")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    WEAPON_DATA = json.load(f)


@app.get("/")
def root():
    return {"status": "ok", "message": "GBF Weapon API (SSR + 特殊SSR)"}


@app.get("/weapon_data")
def get_weapon_data(name: str):
    """
    武器名を受け取り、SSR + 特殊SSR の JSON から該当データを返す
    """
    if name in WEAPON_DATA:
        return {
            "status": "success",
            "weapon_name": name,
            "data": WEAPON_DATA[name]
        }
    else:
        raise HTTPException(status_code=404, detail="Weapon not found")


@app.get("/search")
def search_weapon(keyword: str):
    """
    部分一致検索（Bubble で便利）
    """
    results = {
        name: data
        for name, data in WEAPON_DATA.items()
        if keyword in name
    }

    return {
        "status": "success",
        "count": len(results),
        "results": results
    }
