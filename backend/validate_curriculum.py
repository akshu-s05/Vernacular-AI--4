from sqlalchemy.orm import Session
from database import SessionLocal
from models import Grade, Subject, Chapter, Lesson, CurriculumSource, User

def validate_curriculum():
    db: Session = SessionLocal()
    try:
        source = db.query(CurriculumSource).first()
        print("=" * 60)
        print("OFFICIAL J-GURUJI CURRICULUM IMPORT REPORT")
        print("=" * 60)
        print(f"Source Authority : {source.source_authority}")
        print(f"Source URL       : {source.source_url}")
        print(f"Imported At      : {source.imported_at}")
        print("-" * 60)

        total_subjects = 0
        total_chapters = 0
        total_lessons = 0

        for class_num in range(1, 6):
            grade = db.query(Grade).filter_by(class_number=class_num).first()
            if not grade:
                print(f"Class {class_num}: Not available in J-Guruji source.")
                continue

            subjects = db.query(Subject).filter_by(grade_id=grade.id).all()
            subj_count = len(subjects)
            total_subjects += subj_count

            chap_count = 0
            lesson_count = 0
            subject_breakdown = []

            for s in subjects:
                chaps = db.query(Chapter).filter_by(subject_id=s.id).all()
                c_cnt = len(chaps)
                chap_count += c_cnt
                for c in chaps:
                    les = db.query(Lesson).filter_by(chapter_id=c.id).all()
                    lesson_count += len(les)
                subject_breakdown.append(f"{s.name} ({c_cnt} chapters)")

            total_chapters += chap_count
            total_lessons += lesson_count

            print(f"Class {class_num}:")
            print(f"  Subjects found: {subj_count}")
            print(f"  Chapters found: {chap_count}")
            print(f"  Lessons/Topics: {lesson_count}")
            print(f"  Subject list  : {', '.join(subject_breakdown)}")
            print()

        print("-" * 60)
        print(f"TOTAL CLASS 1-5 SUBJECTS : {total_subjects}")
        print(f"TOTAL CLASS 1-5 CHAPTERS : {total_chapters}")
        print(f"TOTAL CLASS 1-5 LESSONS  : {total_lessons}")
        print("=" * 60)

        # Users verification
        users = db.query(User).all()
        print(f"Total Users Registered: {len(users)}")
        for u in users:
            print(f"  - [{u.role.upper()}] {u.name} (ID: {u.identifier}, School: {u.school})")
        print("=" * 60)

    finally:
        db.close()

if __name__ == "__main__":
    validate_curriculum()
