# Python Project

이 프로젝트는 Python으로 작성된 기본 프로젝트입니다.

## 설치 방법

1. 프로젝트를 클론합니다
2. 가상환경을 생성합니다:
   ```
   python -m venv venv
   ```
3. 가상환경을 활성화합니다:
   - Windows:
     ```
     .\venv\Scripts\activate
     ```
4. 필요한 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```

## 설치 및 실행 방법

### 1. Python 설치
1. [Python 공식 웹사이트](https://www.python.org/downloads/)에서 Python 3.8 이상 버전을 다운로드합니다.
2. 다운로드한 설치 파일을 실행합니다.
3. 설치 시 **"Add Python to PATH"** 옵션을 반드시 체크하세요!
4. 설치가 완료되면 명령 프롬프트(cmd)를 실행하여 다음 명령어로 Python이 정상적으로 설치되었는지 확인합니다:
   ```bash
   python --version
   ```

### 2. 프로젝트 다운로드
1. 이 저장소를 다운로드하거나 클론합니다.
2. 명령 프롬프트(cmd)에서 프로젝트 폴더로 이동합니다:
   ```bash
   cd 프로젝트_폴더_경로
   ```

### 3. 가상환경 생성 및 활성화 (권장)
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 4. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 5. 실행 방법

#### 백엔드 서버 실행
1. 프로젝트 루트 디렉토리에서 다음 명령어를 실행합니다:
   ```bash
   # 방법 1: Python 모듈로 실행
   python -m backend.main

   # 방법 2: 직접 실행
   python backend/main.py
   ```
2. 서버가 성공적으로 시작되면 콘솔에 "Server running on http://localhost:5000" 메시지가 표시됩니다.

#### Electron 앱 실행
1. 새로운 터미널 창을 엽니다 (기존 서버는 실행 중인 상태로 둡니다).
2. frontend 폴더로 이동합니다:
   ```bash
   cd frontend
   ```
3. 처음 실행하는 경우, 필요한 npm 패키지를 설치합니다:
   ```bash
   npm install
   ```
4. Electron 앱을 실행합니다:
   ```bash
   # 개발 모드로 실행
   npm run dev

   # 또는 프로덕션 모드로 실행
   npm start
   ```

#### 주의사항
- 백엔드 서버가 실행되고 있는 상태에서 Electron 앱을 실행해야 합니다.
- 서버 포트(5000)가 이미 사용 중인 경우, 다른 프로그램을 종료하거나 포트를 변경해야 할 수 있습니다.
- 개발 중에는 `npm run dev` 명령어를 사용하면 코드 변경 사항이 실시간으로 반영됩니다.

## 프로젝트 구조

```
python_project/
├── README.md
├── requirements.txt
├── .gitignore        # Git 버전 관리 제외 설정
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

## Git 버전 관리

프로젝트는 Git을 사용하여 버전 관리됩니다. `.gitignore` 파일에 다음과 같은 항목들이 설정되어 있습니다:

### Python 관련
- `__pycache__/`
- 컴파일된 Python 파일 (*.pyc, *.pyo)
- 배포 관련 디렉토리 (dist/, build/)
- 가상환경 디렉토리 (venv/, env/, .venv/)

### Node.js 관련
- `node_modules/`
- npm 및 yarn 로그 파일
- `package-lock.json`

### 개발 환경
- IDE 설정 파일 (.idea/, .vscode/)
- 데이터베이스 파일 (*.db, *.sqlite3)
- 로그 파일 (*.log)
- 테스트 커버리지 파일

## 변경 사항 기록 (Changelog)

### 2024-01-09
#### 워드클라우드 단어 빈도수 퍼센트 계산 추가
- **파일:** `backend/domain/wordcloud/wordcloud_service.py`
- **변경 내용:**
  1. 단어 빈도수에 퍼센트 정보 추가
     - 전체 단어 수 대비 각 단어의 출현 비율 계산
     - 소수점 2자리까지 표시
  2. 응답 형식 업데이트
     ```json
     {
       "success": true,
       "image": "base64_image_data",
       "words": [
         {
           "word": "단어",
           "frequency": 10,
           "percentage": 5.26
         },
         ...
       ]
     }
     ```
- **변경 이유:** 
  - 단어 빈도수 테이블에 퍼센트 정보 표시 기능 추가
  - 전체 텍스트에서 각 단어가 차지하는 비중 시각화

#### 워드클라우드 단어 빈도수 분석 기능 추가
- **파일:** `backend/domain/wordcloud/wordcloud_service.py`
- **변경 내용:**
  1. 단어 빈도수 계산 로직 추가
     - 2글자 이상의 단어만 포함
     - 빈도수 기준 내림차순, 단어 기준 오름차순 정렬
     - 상위 100개 단어만 반환
  2. 응답 형식
     ```json
     {
       "success": true,
       "image": "base64_image_data",
       "words": [
         {
           "word": "단어",
           "frequency": 빈도수
         },
         ...
       ]
     }
     ```
- **변경 이유:** 
  - 워드클라우드와 함께 단어 빈도수 정보 제공
  - 데이터 분석 및 시각화 기능 강화

#### 클라이언트 워드클라우드 요청 구조 수정
- **파일:** `frontend/src/index.js`
- **변경 내용:**
  1. API 요청 데이터 구조 수정
     ```javascript
     // 변경 전
     {
         text: "텍스트",
         config: {
             font: "폰트명",
             background_color: "색상",
             // ...
         }
     }
     
     // 변경 후
     {
         text: "텍스트",
         font: "폰트명",
         background_color: "색상",
         // ...
     }
     ```
  2. 응답 처리 로직 개선
     - 성공/실패 상태 확인
     - 이미지 데이터 경로 수정
     - 에러 메시지 처리 강화
- **변경 이유:** 
  - 서버의 `WordCloudRequest` 모델 구조와 일치하도록 수정
  - 응답 처리 로직 표준화

#### 워드클라우드 이미지 생성 오류 수정
- **관련 파일:**
  - `backend/domain/wordcloud/wordcloud_service.py`
  - `backend/api/routes.py`
- **변경 내용:**
  1. 워드클라우드 서비스 응답 형식 개선
     - 성공/실패 여부를 명시적으로 포함
     - 오류 발생 시 적절한 에러 메시지 반환
     ```python
     # 성공 시
     {
         'success': True,
         'image': 'base64_encoded_image_data',
         'words': []
     }
     
     # 실패 시
     {
         'success': False,
         'error': '오류 메시지'
     }
     ```
  2. API 응답 처리 개선
     - 서비스 실패 시 적절한 HTTP 오류 응답 반환
     - 이미지 데이터 검증 로직 추가
- **변경 이유:** 
  - base64 이미지 데이터가 undefined로 반환되는 문제 해결
  - 오류 처리 및 응답 형식 표준화

#### 워드클라우드 API 응답 형식 수정
- **파일:** `backend/api/routes.py`
- **변경 내용:**
  - 워드클라우드 생성 API의 응답 형식을 이미지 바이너리에서 JSON 형식으로 변경
  - base64로 인코딩된 이미지를 Data URL 형식으로 포함하여 반환
  ```json
  {
    "success": true,
    "data": {
      "image": "data:image/png;base64,...",
      "words": []
    }
  }
  ```
- **변경 이유:** 클라이언트에서 JSON 형식의 응답을 기대하고 있어, 이미지 바이너리 대신 base64 인코딩된 이미지를 포함한 JSON 응답으로 수정
