from app.schemas.quiz import ChoiceSubmit, QuestionSubmit, QuizSubmitRequest

def transform_to_quiz_submit(data):
    questions = []
    
    data = data.dict()
    # 퀴즈 데이터 변환
    answers = data['answers'][0]['questions']
    metadata = data['answers'][0]
    
    for q in answers:
        choices = [ChoiceSubmit(choice["id"], choice["is_selected"]) for choice in q["choices"]]
        question = QuestionSubmit(q["id"], q["text"], choices)
        questions.append(question)

    quiz_request = QuizSubmitRequest(
        quiz_id=metadata["quiz_id"],
        title=metadata["title"],
        description=metadata["description"],
        questions=answers
    )
    
    return quiz_request
