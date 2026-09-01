import os
import time
import uuid
import jwt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ← 新增这行导入
from fastapi.responses import JSONResponse

app = FastAPI()

# ============================================================
# 1. 配置部分
# ============================================================
APP_ID = "117678574575449276425"
PUBLIC_KEY_FINGERPRINT = "KNqBWtwhBvGPcP2r9_W0jw6e5eDuD9Uk0GKg1s7Fm24"

# 从环境变量读取私钥
PRIVATE_KEY = os.environ.get("COZE_PRIVATE_KEY")
if not PRIVATE_KEY:
    raise Exception("环境变量 COZE_PRIVATE_KEY 未设置！请检查 Render 配置。")

# ============================================================
# 2. CORS 中间件配置 ← 你问的这段代码，需要加在这里
# ============================================================
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 3. 核心函数：生成 JWT
# ============================================================
def generate_user_jwt(user_unique_id: str) -> str:
    headers = {
        "alg": "RS256",
        "typ": "JWT",
        "kid": PUBLIC_KEY_FINGERPRINT
    }
    payload = {
        "iss": APP_ID,
        "aud": "api.coze.cn",
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,
        "jti": str(uuid.uuid4()),
        "session_name": user_unique_id
    }
    encoded_jwt = jwt.encode(payload, PRIVATE_KEY, algorithm='RS256', headers=headers)
    return encoded_jwt

# ============================================================
# 4. API 接口
# ============================================================
@app.get("/api/get-jwt")
async def get_jwt(user_id: str):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    jwt_token = generate_user_jwt(user_id)
    return JSONResponse(content={"jwt": jwt_token})

# ============================================================
# 5. 根路径（可选，用于健康检查）
# ============================================================
@app.get("/")
async def root():
    return {"message": "Coze JWT Backend is running!"}