import os
import json
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import (
    CurriculumSource, Grade, Subject, Chapter, Lesson, CurriculumContent,
    User, TeacherProfile, StudentProfile
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def init_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

def import_jguruji_data(json_path: str = "./data/curriculum/jguruji_class1_5_raw.json"):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Curriculum JSON file not found at: {json_path}")

    with open(json_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    db: Session = SessionLocal()
    try:
        source = db.query(CurriculumSource).filter_by(source_name="J-Guruji Jharkhand").first()
        if not source:
            source = CurriculumSource(
                source_name="J-Guruji Jharkhand",
                source_url="https://jguruji.jharkhand.gov.in/",
                source_authority="Department of School Education & Literacy, Govt. of Jharkhand",
                source_reference="SummaryResources & SummaryDetails API/Tables",
                version="1.0"
            )
            db.add(source)
            db.commit()
            db.refresh(source)

        for c_num in range(1, 6):
            grade = db.query(Grade).filter_by(class_number=c_num).first()
            if not grade:
                grade = Grade(class_number=c_num, name=f"Class {c_num}")
                db.add(grade)
        db.commit()

        # Group data into hierarchy: Class -> Subject -> Chapter -> Topic/Lesson
        records_processed = 0
        subject_cache = {}
        chapter_cache = {}
        lesson_cache = {}

        for item in data:
            c_num = item["class_number"]
            s_name = item["subject"].strip()
            s_hindi = item.get("subject_hindi", "").strip() or s_name
            ch_name = item["chapter"].strip()
            ch_hindi = item.get("chapter_hindi", "").strip() or ch_name
            topic_name = item.get("topic", "").strip()
            source_url = item.get("source_url", "https://jguruji.jharkhand.gov.in/")

            grade = db.query(Grade).filter_by(class_number=c_num).first()
            if not grade:
                continue

            subj_key = f"{c_num}|{s_name}"
            if subj_key not in subject_cache:
                subj = db.query(Subject).filter_by(grade_id=grade.id, name=s_name).first()
                if not subj:
                    subj = Subject(
                        grade_id=grade.id,
                        name=s_name,
                        original_name=s_hindi,
                        source_reference=source_url
                    )
                    db.add(subj)
                    db.commit()
                    db.refresh(subj)
                subject_cache[subj_key] = subj
            else:
                subj = subject_cache[subj_key]

            # Chapter
            ch_key = f"{subj.id}|{ch_name}"
            if ch_key not in chapter_cache:
                chap = db.query(Chapter).filter_by(subject_id=subj.id, name=ch_name).first()
                if not chap:
                    chap = Chapter(
                        subject_id=subj.id,
                        name=ch_name,
                        original_name=ch_hindi,
                        source_reference=source_url
                    )
                    db.add(chap)
                    db.commit()
                    db.refresh(chap)
                chapter_cache[ch_key] = chap
            else:
                chap = chapter_cache[ch_key]

            # Lesson / Topic
            les_title = topic_name if topic_name else ch_name
            les_key = f"{chap.id}|{les_title}"
            if les_key not in lesson_cache:
                les = db.query(Lesson).filter_by(chapter_id=chap.id, title=les_title).first()
                if not les:
                    les = Lesson(
                        chapter_id=chap.id,
                        title=les_title,
                        original_name=ch_hindi if not topic_name else topic_name,
                        topic=topic_name,
                        source_reference=source_url
                    )
                    db.add(les)
                    db.commit()
                    db.refresh(les)
                lesson_cache[les_key] = les

            records_processed += 1

        print(f"Curriculum import completed! Processed {records_processed} raw records.")
        print(f"Subjects created/verified: {len(subject_cache)}")
        print(f"Chapters created/verified: {len(chapter_cache)}")
        print(f"Lessons created/verified: {len(lesson_cache)}")

        # Seed Demo Accounts
        teacher_user = db.query(User).filter_by(identifier="teacher01").first()
        if not teacher_user:
            teacher_user = User(
                role="teacher",
                identifier="teacher01",
                name="Anita Kumar",
                school="Government Primary School",
                password_hash=hash_password("teacher123"),
                preferred_language="Hindi"
            )
            db.add(teacher_user)
            db.commit()
            db.refresh(teacher_user)

            t_prof = TeacherProfile(
                user_id=teacher_user.id,
                teacher_id="teacher01",
                department="Primary Section"
            )
            db.add(t_prof)
            db.commit()
            print("Seeded Demo Teacher: teacher01 (Anita Kumar)")

        student_user = db.query(User).filter_by(identifier="student01").first()
        if not student_user:
            student_user = User(
                role="student",
                identifier="student01",
                name="Rahul",
                school="Government Primary School",
                password_hash=hash_password("student123"),
                preferred_language="Santali"
            )
            db.add(student_user)
            db.commit()
            db.refresh(student_user)

            s_prof = StudentProfile(
                user_id=student_user.id,
                student_id="student01",
                class_number=3
            )
            db.add(s_prof)
            db.commit()
            print("Seeded Demo Student: student01 (Rahul, Class 3)")

    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    import_jguruji_data()
