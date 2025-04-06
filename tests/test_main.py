import re

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import redis_client
from app.db.session import Base, get_db
from app.api.v1.router import router

from app.models.user import User

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides = {}
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_start_quiz():
    ############################
    # 1 어드민 계정 생성 API 테스트 #
    ############################
    admin_resp = client.post("/api/v1/user/", json={
        "email": "admin@admin.com",
        "name": "admin",
        "is_active": True,
        "is_superuser": True,
        "password": "password"
    })
    assert admin_resp.status_code == 201
    admin_id = admin_resp.json()["id"]
    
    ############################
    # 2 사용자 계정 생성 API 테스트 #
    ############################
    user_resp = client.post("/api/v1/user/", json={
        "email": "user@user.com",
        "name": "user",
        "is_active": True,
        "is_superuser": False,
        "password": "password"
    })
    assert user_resp.status_code == 201
    user_id = user_resp.json()["id"]
    
    ############################
    # 3 어드민 토큰 발급 API 테스트 #
    ############################
    admin_token_resp = client.post("/api/v1/auth/token/", json={
        "email": "admin@admin.com",
        "password": "password"
    })
    assert admin_token_resp.status_code == 200
    admin_token = admin_token_resp.json()["access_token"]
    
    quiz_resp = client.post(
        "/api/v1/quiz/sample",
        params={"title": "샘플 퀴즈", "description": "100 문제와 문제 별 5지선다", "user_id": admin_id},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert quiz_resp.status_code == 200
    quiz_id = quiz_resp.json()["id"]
    
    ##########################
    # 4 유저 토큰 발급 API 테스트 #
    ##########################
    user_token_resp = client.post("/api/v1/auth/token/", json={
        "email": "user@user.com",
        "password": "password"
    })
    assert user_token_resp.status_code == 200
    user_token = user_token_resp.json()["access_token"]
    
    ##################################################
    # 5 문제(문제 100개, 문제 별 선택지 5개)  생성 API 테스트 #
    ##################################################
    start_resp = client.get(
        f"/api/v1/quiz/{quiz_id}/start",
        params={"user_id": user_id},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert start_resp.status_code == 200
    data = start_resp.json()

    validation_resp = client.get(
        f"/api/v1/quiz/{quiz_id}/validate",        
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    valid_quiz = validation_resp.json()
    assert valid_quiz["valid"] == True
    
    assert data["quiz_id"] == quiz_id
    assert len(data["questions"]) == 100
    assert "choices" in data["questions"][0]
    assert len(data["questions"][0]["choices"]) == 5


    #######################################################
    # 6 사용자 시험 시작 시 해당 퀴즈에 대한 응시 기록 생성 API 테스트 #
    #######################################################
    quiz_data = start_resp.json()
    user_quiz_attempt_key = f"quiz:{quiz_id}:user_quiz_attempts:"
        
    keys = redis_client.keys(f"{user_quiz_attempt_key}*")

    assert keys, "Redis에 user_quiz_attempt 정보가 없음"

    filtered_keys = [
        k for k in keys if re.match(r".*:\d+$", k)
    ]

    assert filtered_keys, "숫자로 끝나는 유효한 user_quiz_attempt 키가 없음"

    # 최신 키 선택
    latest_key = sorted(filtered_keys)[-1]
    user_quiz_attempt_id = int(latest_key.split(":")[-1])
    
    
    # 유저가 문제에 대한 답안을 선택 할 때 1번부터 100번 문제에 대해 1,2,3,4,5 돌아가면서 선택
    for idx, question in enumerate(quiz_data["questions"]):
        question_id = question["id"]
        choices = question["choices"]
                
        selected_index = idx % 5
        selected_choice_id = choices[selected_index]["id"]

        answer_resp = client.patch(
            f"/api/v1/quiz/{quiz_id}/answer",
            params={"user_quiz_attempt_id": user_quiz_attempt_id},
            json={
                "quiz_attempt_id": user_quiz_attempt_id,
                "question_id": question_id,
                "selected_choice_id": selected_choice_id            },
            headers={"Authorization": f"Bearer {user_token}"}
        )

        assert answer_resp.status_code == 200
        answer_data = answer_resp.json()
        assert answer_data["question_id"] == question_id
        assert answer_data["choice_id"] == selected_choice_id
        assert answer_data["message"] == "Answer updated successfully"
    
    redis_answer_key = f"quiz:{quiz_id}:user_quiz_attempts:{user_quiz_attempt_id}:answers"
    all_answers = redis_client.hgetall(redis_answer_key)
    assert len(all_answers) == 100

    ##############################################################
    # 8 새로고침 시 유저 별 퀴즈 정보와 유저가 선택한 답안을 불러오는 API 테스트 #
    ##############################################################
    refresh_resp = client.get(
        f"/api/v1/quiz/refresh/{user_quiz_attempt_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"quiz_id": quiz_id}
    )
    assert refresh_resp.status_code == 200
    quiz_data = refresh_resp.json()

    for idx, question in enumerate(quiz_data["questions"]):
        selected = [c for c in question["choices"] if c.get("is_selected")]
        assert selected, f"문제 {question['id']}에 선택된 답안이 없음"

    ######################
    # 9 퀴즈 제출 API 테스트 #
    ######################
    submission_payload = {
        "user_id": 2,
        "quiz_attempt_id": 1,
        "answers": [
            {
                "quiz_id": 1,
                "title": quiz_data["title"],
                "description": quiz_data["description"],
                "questions": quiz_data["questions"]
            }
        ]
    }

    submit_resp = client.post(
        f"/api/v1/quiz/{quiz_id}/submit",
        headers={"Authorization": f"Bearer {user_token}"},
        params={"user_quiz_attempt_id": user_quiz_attempt_id},
        json=submission_payload
    )
    assert submit_resp.status_code == 200
    result = submit_resp.json()

    assert result["score"] == 20
    assert result["total"] == 100
