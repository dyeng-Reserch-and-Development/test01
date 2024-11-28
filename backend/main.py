from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os
from pathlib import Path

# 데이터베이스 초기화 임포트
from .infrastructure.db_config import init_db

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 프로젝트 루트 디렉토리 설정
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_PATH = PROJECT_ROOT / "frontend" / "src"

logger.debug(f"Project root: {PROJECT_ROOT}")
logger.debug(f"Frontend path: {FRONTEND_PATH}")

# FastAPI 앱 생성
app = FastAPI()

# 앱 시작 시 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
from .api.routes import router
app.include_router(router, prefix="/api")

# 정적 파일 서빙 설정
app.mount("/", StaticFiles(directory=str(FRONTEND_PATH), html=True), name="static")

# 미들웨어 설정
@app.middleware("http")
async def log_requests(request, call_next):
    logger.debug(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response status: {response.status_code}")
    return response

@app.get("/")
async def serve_frontend():
    index_path = os.path.join(FRONTEND_PATH, 'index.html')
    logger.debug(f"Serving frontend from {index_path}")
    return FileResponse(index_path)

if __name__ == "__main__":
    logger.info("Starting server...")
    logger.info(f"Frontend path: {FRONTEND_PATH}")
    logger.info(f"API endpoint: http://localhost:8000/api")
    logger.info("Once server starts, access http://localhost:8000 in your browser")
    
    import uvicorn
    config = uvicorn.Config(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
        log_config=None,  # 기본 uvicorn 로깅 설정 비활성화
    )
    server = uvicorn.Server(config)
    server.run()
