from fastapi import APIRouter, HTTPException, Response, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import logging
import os
from io import BytesIO
import sys
from pathlib import Path
import base64
import pandas as pd

import sys
import bareunpy as brn
import google.protobuf.text_format as tf

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from backend.domain.wordcloud.wordcloud_service import WordCloudService
from backend.domain.wordcloud.wordcloud_model import WordCloudRequest, WordCloudConfig

# 로깅 설정

logger = logging.getLogger(__name__)

router = APIRouter()

# 업로드된 파일을 저장할 딕셔너리 초기화
uploaded_files = {}

# 워드클라우드 서비스 인스턴스 생성
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
        # 워드클라우드 설정을 WordCloudConfig로 변환
        config = WordCloudConfig(
            text=request.text,
            background_color=request.background_color,
            color_func=request.color_func,
            mask_type=request.mask_type,
            width=request.width,
            height=request.height,
            max_words=request.max_words,
            font=request.font
        )
        
        # 워드클라우드 이미지 생성
        result = wordcloud_service.create_wordcloud(request.text, config)
        
        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('message', '워드클라우드 생성 실패'))
            
        # JSON 응답 반환
        return {
            "success": True,
            "message": result.get('message', '워드클라우드가 생성되었습니다.'),
            "data": {
                "wordcloud_id": result['data']['wordcloud_id'],
                "image": result['data']['image'],
                "word_frequency": result['data']['word_frequency']
            }
        }
        
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

@router.get("/download/{filename}")
async def download_excel(filename: str):
    """워드클라우드 단어 빈도수 데이터를 엑셀 파일로 다운로드"""
    try:
        # 세션에서 데이터를 가져오거나, 임시 저장된 데이터를 가져옵니다
        data = wordcloud_service.get_last_word_frequency()
        
        if not data:
            raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다")
            
        # DataFrame 생성
        df = pd.DataFrame(data)
        
        # Excel 파일 생성
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        
        # 파일 다운로드 응답
        headers = {
            'Content-Disposition': f'attachment; filename=wordcloud_frequency_{filename}.xlsx',
            'Access-Control-Expose-Headers': 'Content-Disposition'
        }
        return StreamingResponse(
            output, 
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers=headers
        )
        
    except Exception as e:
        logger.error(f"엑셀 파일 생성 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-wordcloud")
async def upload_wordcloud(
    file: UploadFile = File(...),
    background_color: str = Form(None),
    width: int = Form(800),
    height: int = Form(400),
    font: str = Form(None),
    mask_type: str = Form("rectangle")
):
    try:
        # 파일 내용 읽기
        content = await file.read()
        text = content.decode('utf-8')
        
        # 설정 생성
        config = WordCloudConfig(
            text=text,  # 파일 내용을 text 필드에 설정
            background_color=background_color,
            width=width,
            height=height,
            font=font,
            mask_type=mask_type
        )
        
        # 워드클라우드 생성
        result = wordcloud_service.create_wordcloud(text, config)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """파일 업로드만 처리하는 엔드포인트"""
    try:
        content = await file.read()
        text = content.decode('utf-8')
        
        # 파일 내용을 메모리에 저장
        file_id = str(len(uploaded_files) + 1)  # 간단한 ID 생성
        uploaded_files[file_id] = {
            "filename": file.filename,
            "content": text
        }
        
        return {
            "status": "success",
            "data": {
                "file_id": file_id,
                "filename": file.filename
            }
        }
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/uploaded-files")
async def get_uploaded_files():
    """업로드된 파일 목록 반환"""
    return {
        "status": "success",
        "data": [
            {"file_id": k, "filename": v["filename"]}
            for k, v in uploaded_files.items()
        ]
    }

@router.get("/file-content/{file_id}")
async def get_file_content(file_id: str):
    """특정 파일의 내용 반환"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "status": "success",
        "data": {
            "content": uploaded_files[file_id]["content"],
            "filename": uploaded_files[file_id]["filename"]
        }
    }

@router.get("/all-files-content")
async def get_all_files_content():
    """모든 업로드된 파일의 내용을 합쳐서 반환"""
    try:
        if not uploaded_files:
            return {"status": "error", "message": "업로드된 파일이 없습니다."}
        
        # 모든 파일의 내용을 하나의 문자열로 합침
        combined_content = "\n".join(file["content"] for file in uploaded_files.values())
        
        return {
            "status": "success",
            "data": {
                "content": combined_content,
                "file_count": len(uploaded_files)
            }
        }
    except Exception as e:
        logger.error(f"Error getting all files content: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.delete("/delete-file/{file_id}")
async def delete_file(file_id: str):
    """업로드된 파일 삭제"""
    try:
        if file_id not in uploaded_files:
            return {"status": "error", "message": "파일을 찾을 수 없습니다."}
        
        # 파일 삭제
        del uploaded_files[file_id]
        
        return {
            "status": "success",
            "message": "파일이 삭제되었습니다."
        }
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return {"status": "error", "message": str(e)}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.get("/test")
async def test():


# 아래에 "https://bareun.ai/"에서 이메일 인증 후 발급받은 API KEY("koba-...")를 입력해주세요. "로그인-내정보 확인"
    API_KEY = "koba-5E34BFY-27YUXYI-QW4U6KY-CCEEYIA" # <- 본인의 API KEY로 교체 
    t = brn.Tagger(API_KEY, "localhost", 5757)
    res = t.tags(["안녕하세요. 정말 좋은 날씨네요."])
    m = res.msg()
    tf.PrintMessage(m, out=sys.stdout, as_utf8=True)
    return res.as_json()

