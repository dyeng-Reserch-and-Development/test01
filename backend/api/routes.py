from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
from io import BytesIO
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from backend.domain.wordcloud.wordcloud_service import WordCloudService
from backend.domain.wordcloud.wordcloud_model import WordCloudRequest

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter()
wordcloud_service = WordCloudService()

class FontInfo(BaseModel):
    name: str
    supports_korean: bool
    file_name: str

class FontResponse(BaseModel):
    fonts: List[FontInfo]

@router.post("/generate")
async def generate_wordcloud(request: WordCloudRequest):
    """워드클라우드 생성 엔드포인트"""
    try:
        # 워드클라우드 이미지 생성
        image = wordcloud_service.create_wordcloud(request)
        
        # 이미지를 바이트로 변환
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # 이미지를 스트리밍 응답으로 반환
        return StreamingResponse(
            content=img_byte_arr,
            media_type="image/png",
            headers={
                "Content-Disposition": "inline; filename=wordcloud.png"
            }
        )
        
    except Exception as e:
        logger.error(f"워드클라우드 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fonts", response_model=FontResponse)
async def get_system_fonts():
    """시스템 폰트 목록 반환 엔드포인트"""
    try:
        font_dir = os.path.join(os.environ['SYSTEMROOT'], 'Fonts')
        fonts = []
        
        # 폰트 파일 확장자
        font_extensions = ('.ttf', '.otf')
        
        # 한글 지원 여부 확인 함수
        def check_korean_support(font_path):
            try:
                from fontTools.ttLib import TTFont
                font = TTFont(font_path)
                for table in font['cmap'].tables:
                    if 0xAC00 in table.cmap:  # 대표적인 한글 문자 '가' 확인
                        font.close()
                        return True
                font.close()
                return False
            except Exception as e:
                logger.error(f"폰트 분석 중 오류 발생: {str(e)}")
                return False
        
        # 폰트 디렉토리 스캔
        for file in os.listdir(font_dir):
            if file.lower().endswith(font_extensions):
                font_path = os.path.join(font_dir, file)
                font_name = os.path.splitext(file)[0]
                
                # 한글 지원 여부 확인
                supports_korean = check_korean_support(font_path)
                
                fonts.append(FontInfo(
                    name=font_name,
                    supports_korean=supports_korean,
                    file_name=file
                ))
        
        # 이름순으로 정렬하되, 한글 지원 폰트를 앞으로
        sorted_fonts = sorted(fonts, key=lambda x: (not x.supports_korean, x.name.lower()))
        return FontResponse(fonts=sorted_fonts)
        
    except Exception as e:
        logger.error(f"폰트 목록 조회 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
