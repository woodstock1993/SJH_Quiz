# SJH_Quiz

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

## 기술  
```
Python 3.12

FastAPI
PostgreSQL  
SQLAlchemy  
Alembic  
Swagger UI (`/docs`)
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
│   ├── api           / FastAPI 엔드포인트(라우트) 정의
│   ├── core          / 애플리케이션 설정 및 토큰
│   ├── crud          / 데이터베이스 CRUD 로직
│   ├── db            / 데이터베이스 연결 및 초기화 관리
│   ├── main.py       / FastAPI 애플리케이션 진입점 
│   ├── models        / ORM 모델 정의 
│   ├── schemas       / Pydantic 데이터 검증 스키마
│   └── utils         / 유틸리티 함수 모음
├── docker-compose.yml
├── poetry.lock
├── pyproject.toml    / Poetry 프로젝트 설정 파일
```