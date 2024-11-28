from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
from domain.wordcloud.wordcloud_service import WordCloudService
from domain.wordcloud.wordcloud_model import WordCloudConfig

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

wordcloud_service = WordCloudService()

class WordCloudRequest(BaseModel):
    text: str
    config: dict = {}

@app.post("/api/wordcloud")
async def create_wordcloud(request: WordCloudRequest):
    try:
        logger.debug(f"Received request: {request}")
        result = wordcloud_service.create_wordcloud(request.text, request.config)
        logger.debug("WordCloud created successfully")
        return result
    except Exception as e:
        logger.error(f"Error creating wordcloud: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
