# trailine-research

트레킹/하이킹 코스에 대한 분석 관련 저장소

## Installation

### 선제조건

* python >= 3.13
* using package manager **uv**
* Windows 11

### 과정

1. 가상환경 세팅
```shell
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
.\venv\Scripts\Activate.ps1
```

2. 의존성 설치
```shell
uv pip install -e .
```

추가로 선택적 의존성 설치도 가능하다.
```shell
# 테스트에 필요한 패키지(pytest) 설치
pip install -e ".[test]"

# 노트북과 시각화에 필요한 패키지 모두 설치
pip install -e ".[notebook, visual]"

# 모든 선택적 의존성 설치
pip install -e ".[test, notebook, visual, script]"
```

## 스크립트

* `preprocess-raw [json파일]`: 트래킹 및 파이킹 코스가 들어있는 JSON 파일을 받아서 `processed` 디렉토리에 적재한다
  * JSON파일의, [코스 이미지 생성 사이트](https://trail-course-guide.vercel.app) 에서 JSON파일로 추출할 수 있다.