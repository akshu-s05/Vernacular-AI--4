def update_sync():
    with open('backend/main.py', 'r', encoding='utf-8') as f:
        code = f.read()

    old_sync_code = """    # Pull published teacher lessons
    published_lessons = db.query(TeacherContent).filter_by(is_published=True).all()
    pulled_items = []
    for pl in published_lessons:
        pulled_items.append({
            "id": pl.id,
            "lesson_id": pl.lesson_id,
            "title": pl.title,
            "content": pl.content,
            "santali_translation": pl.santali_translation,
            "version": pl.version,
            "published_at": str(pl.published_at)
        })"""

    new_sync_code = """    # Pull published teacher lessons
    published_lessons = db.query(TeacherContent).filter_by(is_published=True).all()
    pulled_items = []
    for pl in published_lessons:
        pulled_items.append({
            "id": pl.id,
            "lesson_id": pl.lesson_id,
            "title": pl.title,
            "content": pl.content,
            "santali_translation": pl.santali_translation,
            "version": pl.version,
            "published_at": str(pl.published_at)
        })

    # Pull latest worksheets and quizzes for offline availability
    worksheets = db.query(Worksheet).order_by(Worksheet.created_at.desc()).limit(10).all()
    pulled_worksheets = [{
        "id": w.id,
        "lesson_id": w.lesson_id,
        "title": w.title,
        "content_bilingual": w.content_bilingual,
        "instructions": w.instructions
    } for w in worksheets]

    quizzes = db.query(Quiz).order_by(Quiz.created_at.desc()).limit(10).all()
    pulled_quizzes = []
    for q in quizzes:
        q_questions = db.query(QuizQuestion).filter_by(quiz_id=q.id).all()
        pulled_quizzes.append({
            "id": q.id,
            "lesson_id": q.lesson_id,
            "title": q.title,
            "questions": [{
                "id": qq.id,
                "question_text": qq.question_text,
                "option_a": qq.option_a,
                "option_b": qq.option_b,
                "option_c": qq.option_c,
                "option_d": qq.option_d,
                "correct_option": qq.correct_option,
                "explanation": qq.explanation
            } for qq in q_questions]
        })"""

    old_return = """    return {
        "status": "SYNCED",
        "sync_timestamp": str(now),
        "items_pushed": pushed,
        "items_pulled": len(pulled_items),
        "updates": pulled_items
    }"""

    new_return = """    return {
        "status": "SYNCED",
        "sync_timestamp": str(now),
        "items_pushed": pushed,
        "items_pulled": len(pulled_items) + len(pulled_worksheets) + len(pulled_quizzes),
        "updates": pulled_items,
        "offline_worksheets": pulled_worksheets,
        "offline_quizzes": pulled_quizzes
    }"""

    if old_sync_code in code and old_return in code:
        code = code.replace(old_sync_code, new_sync_code).replace(old_return, new_return)
        with open('backend/main.py', 'w', encoding='utf-8') as f:
            f.write(code)
        print("Sync endpoint enhanced with offline worksheets and quizzes successfully!")
    else:
        print("Code snippet not matched in backend/main.py")

if __name__ == '__main__':
    update_sync()
