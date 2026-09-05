import os
import time
import uuid
import jwt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
# 2. CORS 中间件配置
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
    """为特定用户生成包含 session_name 的 JWT"""
    headers = {
        "alg": "RS256",
        "typ": "JWT",
        "kid": PUBLIC_KEY_FINGERPRINT
    }
    payload = {
        "iss": APP_ID,
        "aud": "api.coze.cn",
        "iat": int(time.time()),
        "exp": int(time.time()) + 600,  # 10分钟后过期
        "jti": str(uuid.uuid4()),
        "session_name": user_unique_id  # 关键：用户唯一标识
    }
    encoded_jwt = jwt.encode(payload, PRIVATE_KEY, algorithm='RS256', headers=headers)
    return encoded_jwt

# ============================================================
# 4. API 接口
# ============================================================
@app.get("/api/get-jwt")
async def get_jwt(auth0_user_id: str):
    """
    接收 Auth0 的用户ID（sub），直接用作 session_name 生成 JWT
    参数名改为 auth0_user_id 以明确其来源
    """
    if not auth0_user_id:
        raise HTTPException(status_code=400, detail="auth0_user_id is required")
    
    # 直接将 Auth0 的用户ID 作为 session_name
    # Auth0 的 sub 是全局唯一的，可以直接用作内部 user_id
    user_id = auth0_user_id
    
    # 生成 JWT
    jwt_token = generate_user_jwt(user_id)
    return JSONResponse(content={"jwt": jwt_token})

# ============================================================
# 5. 根路径（健康检查）
# ============================================================
@app.get("/")
async def root():
    return {"message": "Coze JWT Backend is running!"}
