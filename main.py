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
