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
