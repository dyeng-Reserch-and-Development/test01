from typing import Optional, Any
from pydantic import BaseModel, ConfigDict
import logging
import os
import re
import numpy as np
from PIL import Image

class WordCloudConfig(BaseModel):
    """워드클라우드 설정"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    text: str
    background_color: str = "white"
    color_func: str = "single_color"
    mask_type: str = "rectangle"
    width: int = 800
    height: int = 400
    max_words: int = 200
    font: Optional[str] = None
    mask: Optional[Any] = None  # numpy.ndarray 타입을 Any로 처리
    font_path: Optional[str] = None

class WordCloudRequest(BaseModel):
    """워드클라우드 생성 요청"""
    text: str
    background_color: str = "white"
    color_func: str = "single_color"
    mask_type: str = "rectangle"
    width: int = 800
    height: int = 400
    max_words: int = 200
    font: Optional[str] = None

class WordCloudGenerator:
    """워드클라우드 생성기"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _create_mask(self, mask_type: str, width: int, height: int) -> np.ndarray:
        """마스크 이미지 생성"""
        mask = np.zeros((height, width), dtype=np.uint8)
        
        if mask_type == "circle":
            # 원형 마스크
            center = (width//2, height//2)
            radius = min(width, height)//2
            img = Image.fromarray(mask)
            draw = ImageDraw.Draw(img)
            draw.ellipse([
                center[0]-radius, 
                center[1]-radius,
                center[0]+radius, 
                center[1]+radius
            ], fill=255)
            mask = np.array(img)
            
        elif mask_type == "heart":
            # 하트 모양 마스크
            img = Image.fromarray(mask)
            draw = ImageDraw.Draw(img)
            
            # 하트 모양 그리기
            center_x = width // 2
            center_y = height // 2
            size = min(width, height) // 2
            
            # 하트 모양의 점들
            heart_points = [
                (center_x, center_y + size//2),  # bottom point
                (center_x - size//2, center_y - size//4),  # left control
                (center_x, center_y - size),  # top control
                (center_x + size//2, center_y - size//4),  # right control
            ]
            
            draw.polygon(heart_points, fill=255)
            mask = np.array(img)
            
        else:  # rectangle or default
            mask.fill(255)  # 전체를 흰색으로
        
        return mask
    
    def _get_color_func(self, color_type: str):
        """색상 함수 생성"""
        if color_type == "random_color":
            import random
            def random_color(*args, **kwargs):
                return f"hsl({random.randint(0, 360)}, 70%, 50%)"
            return random_color
            
        elif color_type == "gradient_color":
            def gradient_color(*args, **kwargs):
                # 빨간색에서 보라색으로 그라데이션
                word = args[0] if args else ""
                font_size = args[1] if len(args) > 1 else 10
                position = font_size / 100.0  # font_size를 0-1 사이 값으로 정규화
                
                # HSL 색상 범위 설정 (0: 빨강, 60: 노랑, 120: 초록, 180: 청록, 240: 파랑, 300: 보라)
                hue = int(300 * position)  # position에 따라 0-300 사이의 색상
                return f"hsl({hue}, 80%, 50%)"
            return gradient_color
            
        else:  # single_color
            def single_color(*args, **kwargs):
                return "black"
            return single_color
    
    def generate(self, config: WordCloudConfig) -> Image:
        """워드클라우드 이미지 생성"""
        try:
            from wordcloud import WordCloud
            import numpy as np
            from PIL import Image
            
            # 색상 함수 가져오기
            color_func = self._get_color_func(config.color_func)
            
            self.logger.debug(f"워드클라우드 생성 시작: 폰트={config.font_path}, 마스크={config.mask.shape if config.mask is not None else 'None'}")
            
            # WordCloud 객체 생성
            wc = WordCloud(
                font_path=config.font_path,  # 폰트 경로
                width=config.width,
                height=config.height,
                background_color=config.background_color,
                max_words=config.max_words,
                mask=config.mask,  # 마스크
                color_func=color_func,
                prefer_horizontal=0.7,
                min_font_size=10,
                max_font_size=200,
                relative_scaling=0.5,
                repeat=False,
                random_state=42
            )
            
            # 워드클라우드 생성
            wc.generate(config.text)
            
            # PIL Image로 변환
            image = wc.to_image()
            
            return image
            
        except Exception as e:
            self.logger.error(f"워드클라우드 생성 중 오류 발생: {str(e)}")
            raise Exception(f"워드클라우드 생성 실패: {str(e)}")

    def preprocess_text(self, text: str) -> str:
        """한글 텍스트 전처리 - 간단한 버전"""
        # 한글과 영문만 남기고 나머지는 공백으로 변경
        text = re.sub(r'[^\가-힣a-zA-Z\s]', ' ', text)
        # 공백으로 분리하여 단어 목록 생성
        words = text.split()
        # 2글자 이상인 단어만 선택
        words = [word for word in words if len(word) >= 2]
        return ' '.join(words)

    def create_mask(self, width, height, mask_type):
        mask = np.zeros((height, width), dtype=np.uint8)
        center_y, center_x = height // 2, width // 2
        
        if mask_type == 'circle':
            y, x = np.ogrid[:height, :width]
            radius = min(center_x, center_y) - 20
            dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            mask[dist_from_center <= radius] = 255
        elif mask_type == 'heart':
            scale = min(center_x, center_y) / 2 
            y, x = np.ogrid[:height, :width]
            x = (x - center_x) / scale
            y = (y - center_y) / scale
            mask[(x**2 + (y*1.0 + abs(x)**1.0)**2) < 8] = 255  # 수식 추가 조정
        else:  # rectangle or default
            padding = min(width, height) // 10
            mask[padding:height-padding, padding:width-padding] = 255
        
        # 마스크 반전
        return 255 - mask
