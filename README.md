# SJH_Quiz

## 진행 기기 및 소프트웨어 버전

```
Mac

Python 3.12.2

Docker version 28.0.1
```

## 실행 방법
```python
git clone git@github.com:woodstock1993/SJH_Quiz.git

cd SJH_Quiz/

docker compose up -d

docker exec -it fastapi_server /bin/sh

poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "Initial migration"

-> http://localhost:8000/docs
```

## 제거 방법
```
docker compose down -v

docker system prune -af 
```

## 기술  
```
Python
FastAPI
PostgreSQL  
SQLAlchemy  
Alembic  
Poetry
Docker
```

## 폴더 구조
```
├── Dockerfile
├── README.md
├── alembic
├── alembic.ini
├── app
│   ├── __init__.py
│   ├── __pycache__
│   ├── api            / FastAPI 엔드포인트(라우트) 정의
│   ├── core           / 애플리케이션 설정 및 토큰
│   ├── crud           / 데이터베이스 CRUD 로직
│   ├── db             / 데이터베이스 연결 및 초기화 관리
│   ├── main.py        / FastAPI 애플리케이션 진입 파일 
│   ├── models         / ORM 모델 정의 
│   ├── schemas        / Pydantic 데이터 검증 스키마
│   └── utils          / 유틸리티 함수 모음
├── docker-compose.yml
├── poetry.lock        / Poetry 의존성 파일  
├── pyproject.toml     / Poetry 설정 파일
```

## 주요 흐름도
![Image](https://github.com/user-attachments/assets/74b9cda6-4176-43cd-b0ce-50cc3700a713)