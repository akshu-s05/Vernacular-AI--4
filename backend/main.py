import os
import io
import re
import json
import datetime
import urllib.parse
from typing import List, Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from sqlalchemy import func
from sqlalchemy.orm import Session
from pydantic import BaseModel
import jwt
from passlib.context import CryptContext

from database import engine, get_db, Base
from models import (
    User, TeacherProfile, StudentProfile, Grade, Subject, Chapter, Lesson,
    CurriculumSource, TeacherContent, LessonVersion, Quiz, QuizQuestion,
    QuizAttempt, Flashcard, Worksheet, StudentProgress, Doubt, SyncLog
)
from ai_services import AIService
from tribal_corpora import UI_LOCALIZATION, TribalSentenceEngine

# Password hashing & JWT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "vernacular_ai_jharkhand_secure_token")
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

app = FastAPI(
    title="Vernacular AI Pedagogy Platform - Backend",
    description="Mother Tongue-Based Primary Education & Real-Time Translation API grounded strictly in J-Guruji Jharkhand syllabus.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(__file__), "static")

@app.api_route("/", methods=["GET", "HEAD"])
def get_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "Vernacular AI Backend Online", "docs": "/docs"}

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static_files")
    app.mount("/app", StaticFiles(directory=static_dir, html=True), name="static_app")

@app.get("/api/localization")
def get_localization(lang: Optional[str] = None):
    """Returns complete UI localization dictionary for Santali, Hindi, and English."""
    if lang:
        target = "Santali" if "santali" in lang.lower() else ("Hindi" if "hindi" in lang.lower() else "English")
        return {"language": target, "strings": UI_LOCALIZATION.get(target, UI_LOCALIZATION["Santali"])}
    return {"languages": list(UI_LOCALIZATION.keys()), "localizations": UI_LOCALIZATION}


# ----------------- SCHEMAS -----------------
class TeacherRegisterRequest(BaseModel):
    name: str
    school: str
    teacher_id: Optional[str] = None
    identifier: Optional[str] = None
    id: Optional[str] = None
    password: str
    preferred_language: str = "Hindi"

    @property
    def resolved_teacher_id(self) -> str:
        tid = self.teacher_id or self.identifier or self.id or ""
        return tid.strip()

class StudentRegisterRequest(BaseModel):
    name: str
    school: str
    student_id: Optional[str] = None
    identifier: Optional[str] = None
    id: Optional[str] = None
    password: str
    class_number: int = 3
    preferred_language: str = "Santali"

    @property
    def resolved_student_id(self) -> str:
        sid = self.student_id or self.identifier or self.id or ""
        return sid.strip()

class LoginRequest(BaseModel):
    identifier: Optional[str] = None
    student_id: Optional[str] = None
    teacher_id: Optional[str] = None
    id: Optional[str] = None
    username: Optional[str] = None
    password: str

    @property
    def resolved_identifier(self) -> str:
        ident = self.identifier or self.student_id or self.teacher_id or self.id or self.username or ""
        return ident.strip()


class TranslateRequest(BaseModel):
    text: str
    source_language: str = "Hindi"
    target_language: str = "Santali"

class VoiceTranslateRequest(BaseModel):
    audio_base64: Optional[str] = None
    transcript_text: str
    source_language: str = "Hindi"
    target_language: str = "Santali"

class CreateLessonRequest(BaseModel):
    teacher_identifier: str
    lesson_id: int
    title: str
    content: str
    activities: Optional[str] = ""
    examples: Optional[str] = ""
    language: str = "Hindi"
    santali_translation: Optional[str] = ""
    publish_now: bool = False

class GenerateLessonRequest(BaseModel):
    class_number: int
    subject: str
    chapter: str
    topic: Optional[str] = ""
    language: str = "Santali"

class GenerateQuizRequest(BaseModel):
    lesson_id: int
    class_number: int
    subject: str
    chapter: str
    topic: Optional[str] = ""
    language: str = "Santali"

class GenerateFlashcardRequest(BaseModel):
    lesson_id: int
    class_number: int
    subject: str
    chapter: str
    topic: Optional[str] = ""
    language: Optional[str] = "Santali (English)"

class GenerateWorksheetRequest(BaseModel):
    lesson_id: int
    class_number: int
    subject: str
    chapter: str
    topic: Optional[str] = ""
    language: Optional[str] = "Santali (English)"

class DoubtRequest(BaseModel):
    student_identifier: str
    lesson_id: int
    question: str
    language: str = "Santali"

class ChatRequest(BaseModel):
    message: str
    user_identifier: Optional[str] = "student"
    class_number: Optional[int] = 3
    subject: Optional[str] = "General"
    chapter: Optional[str] = "Curriculum"
    language: Optional[str] = "Santali (English)"
    history: Optional[List[dict]] = []

class QuizSubmitRequest(BaseModel):
    student_identifier: str
    quiz_id: int
    answers: dict # question_id -> selected_option ("A", "B", "C", "D")

class SyncRequest(BaseModel):
    user_identifier: str
    role: str
    client_last_sync: Optional[str] = None
    progress_records: Optional[List[dict]] = []

# ----------------- AUTHENTICATION -----------------

@app.post("/auth/teacher/register")
def register_teacher(req: TeacherRegisterRequest, db: Session = Depends(get_db)):
    tid = req.resolved_teacher_id
    if not tid:
        raise HTTPException(status_code=400, detail="Teacher ID is required")

    existing = db.query(User).filter(func.lower(User.identifier) == tid.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Teacher ID already registered")

    user = User(
        role="teacher",
        identifier=tid,
        name=req.name.strip(),
        school=req.school.strip(),
        password_hash=hash_password(req.password),
        preferred_language=req.preferred_language
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = TeacherProfile(user_id=user.id, teacher_id=tid)
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": user.identifier, "role": user.role, "id": user.id})
    return {
        "status": "SUCCESS",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "role": user.role,
            "identifier": user.identifier,
            "name": user.name,
            "school": user.school,
            "preferred_language": user.preferred_language
        }
    }

@app.post("/auth/teacher/login")
def login_teacher(req: LoginRequest, db: Session = Depends(get_db)):
    ident = req.resolved_identifier
    if not ident:
        raise HTTPException(status_code=400, detail="Teacher ID / Identifier is required")

    user = db.query(User).filter(
        func.lower(User.identifier) == ident.lower(),
        User.role == "teacher"
    ).first()

    # Fallback to teacher_profiles table if needed
    if not user:
        t_prof = db.query(TeacherProfile).filter(func.lower(TeacherProfile.teacher_id) == ident.lower()).first()
        if t_prof:
            user = db.query(User).filter(User.id == t_prof.user_id, User.role == "teacher").first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid teacher credentials")

    token = create_access_token({"sub": user.identifier, "role": user.role, "id": user.id})
    return {
        "status": "SUCCESS",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "role": user.role,
            "identifier": user.identifier,
            "name": user.name,
            "school": user.school,
            "preferred_language": user.preferred_language
        }
    }

@app.post("/auth/student/register")
def register_student(req: StudentRegisterRequest, db: Session = Depends(get_db)):
    sid = req.resolved_student_id
    if not sid:
        raise HTTPException(status_code=400, detail="Student ID is required")

    existing = db.query(User).filter(func.lower(User.identifier) == sid.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already registered")

    user = User(
        role="student",
        identifier=sid,
        name=req.name.strip(),
        school=req.school.strip(),
        password_hash=hash_password(req.password),
        preferred_language=req.preferred_language
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = StudentProfile(user_id=user.id, student_id=sid, class_number=req.class_number)
    db.add(profile)
    db.commit()

    token = create_access_token({"sub": user.identifier, "role": user.role, "id": user.id})
    return {
        "status": "SUCCESS",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "role": user.role,
            "identifier": user.identifier,
            "name": user.name,
            "school": user.school,
            "class_number": req.class_number,
            "preferred_language": user.preferred_language
        }
    }

@app.post("/auth/student/login")
def login_student(req: LoginRequest, db: Session = Depends(get_db)):
    ident = req.resolved_identifier
    if not ident:
        raise HTTPException(status_code=400, detail="Student ID / Identifier is required")

    # Match User by identifier (case-insensitive) with role check
    user = db.query(User).filter(
        func.lower(User.identifier) == ident.lower(),
        User.role == "student"
    ).first()

    # Fallback: check StudentProfile student_id if identifier was different
    if not user:
        s_prof = db.query(StudentProfile).filter(func.lower(StudentProfile.student_id) == ident.lower()).first()
        if s_prof:
            user = db.query(User).filter(User.id == s_prof.user_id, User.role == "student").first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid student credentials")

    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    token = create_access_token({"sub": user.identifier, "role": user.role, "id": user.id})
    return {
        "status": "SUCCESS",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "role": user.role,
            "identifier": user.identifier,
            "name": user.name,
            "school": user.school,
            "class_number": profile.class_number if profile else 3,
            "preferred_language": user.preferred_language
        }
    }

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    school: Optional[str] = None
    class_number: Optional[int] = None
    preferred_language: Optional[str] = None

@app.get("/teacher/profile")
def get_teacher_profile(identifier: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=identifier, role="teacher").first()
    if not user:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return {
        "id": user.id,
        "name": user.name,
        "school": user.school,
        "identifier": user.identifier,
        "preferred_language": user.preferred_language
    }

@app.put("/teacher/profile")
def update_teacher_profile(identifier: str, req: ProfileUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=identifier, role="teacher").first()
    if not user:
        raise HTTPException(status_code=404, detail="Teacher not found")
    if req.name:
        user.name = req.name
    if req.school:
        user.school = req.school
    if req.preferred_language:
        user.preferred_language = req.preferred_language
    db.commit()
    db.refresh(user)
    return {
        "status": "SUCCESS",
        "user": {
            "id": user.id,
            "name": user.name,
            "school": user.school,
            "identifier": user.identifier,
            "preferred_language": user.preferred_language
        }
    }

@app.get("/student/profile")
def get_student_profile(identifier: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=identifier, role="student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    return {
        "id": user.id,
        "name": user.name,
        "school": user.school,
        "identifier": user.identifier,
        "class_number": profile.class_number if profile else 3,
        "preferred_language": user.preferred_language
    }

@app.put("/student/profile")
def update_student_profile(identifier: str, req: ProfileUpdateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=identifier, role="student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if req.name:
        user.name = req.name
    if req.school:
        user.school = req.school
    if req.preferred_language:
        user.preferred_language = req.preferred_language
    if req.class_number and profile:
        profile.class_number = req.class_number
    db.commit()
    db.refresh(user)
    return {
        "status": "SUCCESS",
        "user": {
            "id": user.id,
            "name": user.name,
            "school": user.school,
            "identifier": user.identifier,
            "class_number": profile.class_number if profile else 3,
            "preferred_language": user.preferred_language
        }
    }

# ----------------- CURRICULUM HIERARCHY (STRICT J-GURUJI) -----------------

@app.get("/curriculum")
def get_curriculum_overview(db: Session = Depends(get_db)):
    grades = db.query(Grade).order_by(Grade.class_number).all()
    res = []
    for g in grades:
        subjs = db.query(Subject).filter_by(grade_id=g.id).all()
        res.append({
            "grade_id": g.id,
            "class_number": g.class_number,
            "name": g.name,
            "subjects_count": len(subjs)
        })
    return {"grades": res, "source": "J-Guruji Jharkhand (Authoritative)"}

@app.get("/curriculum/{grade_number}")
def get_grade_curriculum(grade_number: int, db: Session = Depends(get_db)):
    grade = db.query(Grade).filter_by(class_number=grade_number).first()
    if not grade:
        raise HTTPException(status_code=404, detail=f"Class {grade_number} not available in J-Guruji source.")
    subjects = db.query(Subject).filter_by(grade_id=grade.id).all()
    sub_list = []
    for s in subjects:
        chaps = db.query(Chapter).filter_by(subject_id=s.id).all()
        sub_list.append({
            "id": s.id,
            "name": s.name,
            "original_name": s.original_name,
            "chapters_count": len(chaps),
            "source_reference": s.source_reference
        })
    return {"grade": grade_number, "subjects": sub_list}

@app.get("/subjects/{grade_number}")
def get_subjects_by_grade(grade_number: int, db: Session = Depends(get_db)):
    grade = db.query(Grade).filter_by(class_number=grade_number).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    subjects = db.query(Subject).filter_by(grade_id=grade.id).all()
    return [{"id": s.id, "name": s.name, "original_name": s.original_name} for s in subjects]

@app.get("/chapters/{subject_id}")
def get_chapters_by_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter_by(id=subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    chapters = db.query(Chapter).filter_by(subject_id=subject.id).all()
    return [{
        "id": c.id,
        "name": c.name,
        "original_name": c.original_name,
        "source_reference": c.source_reference
    } for c in chapters]

@app.get("/subtopics/{chapter_id}")
def get_subtopics_by_chapter(chapter_id: int, db: Session = Depends(get_db)):
    chapter = db.query(Chapter).filter_by(id=chapter_id).first()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    lessons = db.query(Lesson).filter_by(chapter_id=chapter.id).all()
    return [{
        "id": l.id,
        "title": l.title,
        "original_name": l.original_name,
        "topic": l.topic,
        "source_reference": l.source_reference
    } for l in lessons]

@app.get("/lesson/{lesson_id}")
@app.get("/lessons/{lesson_id}")
def get_lesson_detail(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter_by(id=lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    chapter = db.query(Chapter).filter_by(id=lesson.chapter_id).first()
    subject = db.query(Subject).filter_by(id=chapter.subject_id).first() if chapter else None
    grade = db.query(Grade).filter_by(id=subject.grade_id).first() if subject else None
    class_num = grade.class_number if grade else 3

    # Check if teacher published content exists
    teacher_content = db.query(TeacherContent).filter_by(lesson_id=lesson.id, is_published=True).order_by(TeacherContent.version.desc()).first()

    if teacher_content:
        title = teacher_content.title
        content = teacher_content.content
        activities = teacher_content.activities or ""
        examples = teacher_content.examples or ""
        santali_text = teacher_content.santali_translation or ""
        source_note = f"Verified Teacher Curriculum Unit (v{teacher_content.version}) • J-Guruji Jharkhand"
    else:
        # Generate rich curriculum grounding
        generated = AIService.generate_lesson_grounded(
            class_number=class_num,
            subject=subject.name if subject else "General",
            chapter=chapter.name if chapter else "Unit",
            topic=lesson.title,
            language="Santali"
        )
        title = f"{lesson.title} - {lesson.original_name}" if lesson.original_name else lesson.title
        content = generated["content"]
        activities = generated["activities"]
        examples = generated["examples"]
        santali_text = generated["santali_translation"]
        source_note = generated["grounded_source"]

    if not santali_text or len(santali_text.strip()) < 5:
        trans_topic = AIService.translate_multilingual(lesson.title, source_lang="English", target_lang="Santali")
        santali_text = f"ᱡᱚᱦᱟᱨ! (Johar!) ᱱᱚᱶᱟ ᱯᱟᱲᱦᱟᱣ ᱨᱮ ᱟᱵᱚ '{trans_topic.get('translated_text', lesson.title)}' ᱵᱟᱵᱚᱛ ᱵᱚᱱ ᱪᱮᱫᱚᱜ-ᱟ᱾ ᱢᱟᱪᱮᱛ ᱥᱟᱶᱛᱮ ᱨᱚᱲ ᱢᱮ!"

    tts_url = f"/api/tts?text={urllib.parse.quote(santali_text)}&lang=hi"
    has_quiz = db.query(Quiz).filter_by(lesson_id=lesson.id).count() > 0
    has_flashcards = db.query(Flashcard).filter_by(lesson_id=lesson.id).count() > 0

    return {
        "status": "SUCCESS",
        "lesson_id": lesson.id,
        "title": title,
        "original_name": lesson.original_name or "",
        "class_number": class_num,
        "subject": subject.name if subject else "General",
        "chapter": chapter.name if chapter else "Curriculum Unit",
        "content": content,
        "activities": activities,
        "examples": examples,
        "santali_translation": santali_text,
        "source_reference": lesson.source_reference or source_note,
        "has_quiz": has_quiz,
        "has_flashcards": has_flashcards,
        "audio_url": tts_url
    }

@app.get("/teacher/stats")
def get_teacher_stats(identifier: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=identifier, role="teacher").first()
    if not user:
        raise HTTPException(status_code=404, detail="Teacher not found")

    total_lessons = db.query(TeacherContent).filter_by(teacher_id=user.id).count()
    published_count = db.query(TeacherContent).filter_by(teacher_id=user.id, is_published=True).count()
    drafts_count = total_lessons - published_count
    
    # Calculate sync pending logs
    last_log = db.query(SyncLog).filter_by(user_id=user.id).order_by(SyncLog.last_sync_timestamp.desc()).first()
    pending_sync = 0 if last_log else drafts_count

    return {
        "lessons_prepared": total_lessons,
        "drafts": drafts_count,
        "published": published_count,
        "pending_sync": pending_sync,
        "last_sync": str(last_log.last_sync_timestamp) if last_log else "Never"
    }

@app.get("/teacher/lessons")
def get_teacher_lessons(identifier: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=identifier, role="teacher").first()
    if not user:
        raise HTTPException(status_code=404, detail="Teacher not found")

    contents = db.query(TeacherContent).filter_by(teacher_id=user.id).order_by(TeacherContent.updated_at.desc()).all()
    res = []
    for c in contents:
        lesson = db.query(Lesson).filter_by(id=c.lesson_id).first()
        chap = db.query(Chapter).filter_by(id=lesson.chapter_id).first() if lesson else None
        subj = db.query(Subject).filter_by(id=chap.subject_id).first() if chap else None
        grade = db.query(Grade).filter_by(id=subj.grade_id).first() if subj else None

        res.append({
            "id": c.id,
            "lesson_id": c.lesson_id,
            "title": c.title,
            "content": c.content,
            "activities": c.activities,
            "examples": c.examples,
            "santali_translation": c.santali_translation,
            "is_published": c.is_published,
            "version": c.version,
            "class_number": grade.class_number if grade else None,
            "subject": subj.name if subj else None,
            "chapter": chap.name if chap else None,
            "created_at": str(c.created_at),
            "updated_at": str(c.updated_at)
        })
    return res

@app.get("/student/lessons")
def get_student_lessons(class_number: int, db: Session = Depends(get_db)):
    # Returns published teacher contents for the specific grade
    grade = db.query(Grade).filter_by(class_number=class_number).first()
    if not grade:
        return []

    published_contents = db.query(TeacherContent).filter_by(is_published=True).all()
    res = []
    for c in published_contents:
        lesson = db.query(Lesson).filter_by(id=c.lesson_id).first()
        chap = db.query(Chapter).filter_by(id=lesson.chapter_id).first() if lesson else None
        subj = db.query(Subject).filter_by(id=chap.subject_id).first() if chap else None
        if subj and subj.grade_id == grade.id:
            # Check quiz and flashcards count
            q_cnt = db.query(Quiz).filter_by(teacher_content_id=c.id).count()
            f_cnt = db.query(Flashcard).filter_by(teacher_content_id=c.id).count()
            res.append({
                "id": c.id,
                "lesson_id": c.lesson_id,
                "title": c.title,
                "content": c.content,
                "activities": c.activities,
                "examples": c.examples,
                "santali_translation": c.santali_translation,
                "version": c.version,
                "class_number": class_number,
                "subject": subj.name,
                "chapter": chap.name,
                "has_quiz": q_cnt > 0,
                "has_flashcards": f_cnt > 0,
                "published_at": str(c.published_at)
            })
    return res

@app.post("/lessons")
def create_or_update_lesson(req: CreateLessonRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=req.teacher_identifier, role="teacher").first()
    if not user:
        raise HTTPException(status_code=404, detail="Teacher not found")

    lesson = db.query(Lesson).filter_by(id=req.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Invalid J-Guruji Lesson reference")

    # Check existing draft/content
    existing = db.query(TeacherContent).filter_by(teacher_id=user.id, lesson_id=req.lesson_id).first()
    now = datetime.datetime.utcnow()

    if existing:
        new_version = existing.version + 1
        existing.title = req.title
        existing.content = req.content
        existing.activities = req.activities
        existing.examples = req.examples
        existing.language = req.language
        existing.santali_translation = req.santali_translation
        existing.version = new_version
        existing.server_version = new_version
        existing.updated_at = now
        if req.publish_now:
            existing.is_published = True
            existing.published_at = now

        # Add version log
        ver = LessonVersion(
            teacher_content_id=existing.id,
            version_number=new_version,
            title=req.title,
            content=req.content,
            santali_translation=req.santali_translation,
            updated_by=user.name
        )
        db.add(ver)
        db.commit()
        db.refresh(existing)
        return {"status": "SUCCESS", "action": "UPDATED", "content": existing.id, "version": new_version}
    else:
        content = TeacherContent(
            teacher_id=user.id,
            lesson_id=req.lesson_id,
            title=req.title,
            content=req.content,
            activities=req.activities,
            examples=req.examples,
            language=req.language,
            santali_translation=req.santali_translation,
            is_published=req.publish_now,
            version=1,
            server_version=1,
            created_at=now,
            updated_at=now,
            published_at=now if req.publish_now else None
        )
        db.add(content)
        db.commit()
        db.refresh(content)

        ver = LessonVersion(
            teacher_content_id=content.id,
            version_number=1,
            title=req.title,
            content=req.content,
            santali_translation=req.santali_translation,
            updated_by=user.name
        )
        db.add(ver)
        db.commit()
        return {"status": "SUCCESS", "action": "CREATED", "content": content.id, "version": 1}

@app.post("/lessons/{id}/publish")
def publish_lesson(id: int, db: Session = Depends(get_db)):
    content = db.query(TeacherContent).filter_by(id=id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Lesson not found")

    content.is_published = True
    content.published_at = datetime.datetime.utcnow()
    content.server_version += 1
    db.commit()
    return {"status": "SUCCESS", "published": True, "server_version": content.server_version}

# ----------------- TEACHER FILE UPLOAD & CURRICULUM MAPPING -----------------

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    teacher_identifier: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(identifier=teacher_identifier, role="teacher").first()
    if not user:
        raise HTTPException(status_code=404, detail="Teacher not found")

    content_bytes = await file.read()
    filename = file.filename or "uploaded_document"
    text_extracted = ""

    try:
        text_extracted = content_bytes.decode("utf-8", errors="ignore")
    except Exception:
        text_extracted = f"Extracted text content from binary file {filename}"

    # Curriculum matching algorithm against J-Guruji
    # Searches subject and chapter names
    matches = []
    first_lesson_match = None

    all_chapters = db.query(Chapter).all()
    for ch in all_chapters:
        if ch.name.lower() in text_extracted.lower() or (ch.original_name and ch.original_name.lower() in text_extracted.lower()):
            les = db.query(Lesson).filter_by(chapter_id=ch.id).first()
            subj = db.query(Subject).filter_by(id=ch.subject_id).first()
            gr = db.query(Grade).filter_by(id=subj.grade_id).first()
            matches.append({
                "class_number": gr.class_number,
                "subject": subj.name,
                "chapter": ch.name,
                "lesson_id": les.id if les else None,
                "lesson_title": les.title if les else ch.name
            })
            if not first_lesson_match and les:
                first_lesson_match = les

    if not matches:
        return {
            "status": "UNMAPPED",
            "message": "No matching J-Guruji curriculum item found. Uploaded content must map strictly to existing J-Guruji curriculum hierarchy.",
            "extracted_chars": len(text_extracted),
            "filename": filename
        }

    return {
        "status": "SUCCESS",
        "filename": filename,
        "extracted_chars": len(text_extracted),
        "matches": matches[:5],
        "mapped_lesson": matches[0]
    }

# ----------------- TRANSLATION & VOICE TRANSLATE -----------------

def extract_spoken_text(text: str) -> str:
    """Extract Romanized phonetic pronunciation or dynamically transliterate Ol Chiki Santali into phonetic text for TTS."""
    if not text:
        return ""
    # 1. Look for bracketed romanized phonetic text e.g. "ᱡᱚᱦᱟᱨ (Johar!)"
    matches = re.findall(r"\(([^)]+)\)", text)
    if matches:
        return " ".join(matches).strip()
    matches_sq = re.findall(r"\[([^\]]+)\]", text)
    if matches_sq:
        return " ".join(matches_sq).strip()

    # 2. Check if text has Ol Chiki script characters ([ᱚ-ᱽ])
    if any('\u1C50' <= char <= '\u1C7F' for char in text):
        # 2a. Direct lookup in parallel tribal sentence corpus
        matched = TribalSentenceEngine.find_corpus_sentence(text)
        if matched and matched.get("rom"):
            return matched["rom"].strip()

        # 2b. Synthesize via dynamic translation to Hindi/phonetic representation
        try:
            url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=sat&tl=hi&q={urllib.parse.quote(text.strip())}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str) and data[0].strip():
                        return data[0].strip()
        except Exception as ex:
            print(f"Notice: Dynamic phonetic transliteration: {ex}")

        # 2c. Ol Chiki letter-by-letter phonetic transliteration
        ol_map = {
            '\u1C5A': 'la', '\u1C5B': 'at', '\u1C5C': 'ag', '\u1C5D': 'ang', '\u1C5E': 'al',
            '\u1C5F': 'la', '\u1C60': 'aak', '\u1C61': 'aaj', '\u1C62': 'am',  '\u1C63': 'aaw',
            '\u1C64': 'i',  '\u1C65': 'is', '\u1C66': 'ih',  '\u1C67': 'in',  '\u1C68': 'ir',
            '\u1C69': 'u',  '\u1C6A': 'uc', '\u1C6B': 'ud',  '\u1C6C': 'uy',  '\u1C6D': 'e',
            '\u1C6E': 'ep', '\u1C6F': 'ed', '\u1C70': 'en',  '\u1C71': 'er',  '\u1C72': 'o',
            '\u1C73': 'ot', '\u1C74': 'ob', '\u1C75': 'on',  '\u1C76': 'or',  '\u1C77': 'oh',
            '\u1C78': '',   '\u1C79': '',   '\u1C7A': '',   '\u1C7B': '',   '\u1C7C': '',
            '\u1C7D': '',   '\u1C7E': '.',  '\u1C7F': '.'
        }
        translit = "".join(ol_map.get(ch, ch) for ch in text)
        if translit.strip():
            return translit.strip()

    # 3. Clean Latin words
    latin_words = re.findall(r"[A-Za-z0-9\s.,'?!-]+", text)
    if latin_words and len("".join(latin_words).strip()) > 3:
        return "".join(latin_words).strip()
    return text.strip()

@app.get("/api/tts")
def stream_tts(text: str, santali_text: Optional[str] = None, lang: str = "hi"):
    """
    Generates dynamic speech audio using gTTS from the active Santali text string.
    Streams live MP3 audio with no-cache headers to guarantee non-static dynamic playback.
    """
    input_to_speak = santali_text or text
    cleaned = extract_spoken_text(input_to_speak).strip()
    if not cleaned:
        cleaned = "Johar, Sagun Setag"

    # Select TTS phonetic voice
    has_devanagari = any('\u0900' <= c <= '\u097F' for c in cleaned)
    target_lang = "hi" if (has_devanagari or lang in ["santali", "Santali", "hi", "Hindi"]) else "en"

    try:
        tts = gTTS(text=cleaned, lang=target_lang, slow=False)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return Response(
            content=mp3_fp.read(),
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    except Exception as e:
        try:
            tts = gTTS(text=cleaned, lang="en", slow=False)
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            return Response(
                content=mp3_fp.read(),
                media_type="audio/mpeg",
                headers={"Cache-Control": "no-cache"}
            )
        except Exception:
            raise HTTPException(status_code=500, detail=f"TTS synthesis error: {str(e)}")

@app.post("/translate")
def translate_text_endpoint(req: TranslateRequest):
    res = AIService.translate_text(req.text, req.source_language, req.target_language)
    return res

@app.post("/voice-translate")
def voice_translate_endpoint(req: VoiceTranslateRequest):
    start_time = datetime.datetime.utcnow()
    trans_res = AIService.translate_text(req.transcript_text, req.source_language, req.target_language)
    elapsed_sec = (datetime.datetime.utcnow() - start_time).total_seconds()

    trans_text = trans_res.get("translated_text", "")
    ts_now = int(datetime.datetime.utcnow().timestamp() * 1000)
    tts_url = f"/api/tts?santali_text={urllib.parse.quote(trans_text)}&text={urllib.parse.quote(trans_text)}&lang=hi&_t={ts_now}"

    return {
        "status": "SUCCESS",
        "input_transcript": req.transcript_text,
        "source_language": req.source_language,
        "target_language": req.target_language,
        "translated_text": trans_text,
        "audio_tts_url": tts_url,
        "tts_status": "Santali Voice Audio Generated & Ready",
        "latency_seconds": round(elapsed_sec, 3)
    }

# ----------------- PEDAGOGICAL AI GENERATION (GROUNDED) -----------------

@app.post("/generate-lesson")
def generate_lesson_endpoint(req: GenerateLessonRequest):
    return AIService.generate_lesson_grounded(
        class_number=req.class_number,
        subject=req.subject,
        chapter=req.chapter,
        topic=req.topic or "",
        language=req.language
    )

@app.post("/generate-quiz")
def generate_quiz_endpoint(req: GenerateQuizRequest, db: Session = Depends(get_db)):
    questions = AIService.generate_quiz_grounded(
        class_number=req.class_number,
        subject=req.subject,
        chapter=req.chapter,
        topic=req.topic or "",
        language=req.language
    )

    # Save to database
    quiz = Quiz(
        lesson_id=req.lesson_id,
        title=f"Quiz: {req.topic or req.chapter}",
        language=req.language
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    q_objs = []
    for q in questions:
        item = QuizQuestion(
            quiz_id=quiz.id,
            question_text=q["question_text"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_option=q["correct_option"],
            explanation=q["explanation"]
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        q_objs.append({
            "id": item.id,
            "question_text": item.question_text,
            "option_a": item.option_a,
            "option_b": item.option_b,
            "option_c": item.option_c,
            "option_d": item.option_d,
            "correct_option": item.correct_option,
            "explanation": item.explanation
        })

    return {
        "status": "SUCCESS",
        "quiz_id": quiz.id,
        "title": quiz.title,
        "total_questions": len(q_objs),
        "questions": q_objs
    }

@app.post("/generate-flashcards")
def generate_flashcards_endpoint(req: GenerateFlashcardRequest, db: Session = Depends(get_db)):
    cards = AIService.generate_flashcards_grounded(
        class_number=req.class_number,
        subject=req.subject,
        chapter=req.chapter,
        topic=req.topic or "",
        language=getattr(req, "language", "Santali (English)")
    )
    saved_cards = []
    for c in cards:
        fc = Flashcard(
            lesson_id=req.lesson_id,
            front_text=c["front_text"],
            back_text=c["back_text"],
            category=c["category"]
        )
        db.add(fc)
        db.commit()
        db.refresh(fc)
        saved_cards.append({
            "id": fc.id,
            "front_text": fc.front_text,
            "back_text": fc.back_text,
            "category": fc.category
        })
    return {"status": "SUCCESS", "total_cards": len(saved_cards), "flashcards": saved_cards}

@app.post("/generate-worksheet")
def generate_worksheet_endpoint(req: GenerateWorksheetRequest, db: Session = Depends(get_db)):
    data = AIService.generate_worksheet_grounded(
        class_number=req.class_number,
        subject=req.subject,
        chapter=req.chapter,
        topic=req.topic or "",
        language=getattr(req, "language", "Santali (English)")
    )
    ws = Worksheet(
        lesson_id=req.lesson_id,
        title=data["title"],
        content_bilingual=data["content_bilingual"],
        instructions=data["instructions"]
    )
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return {
        "status": "SUCCESS",
        "worksheet_id": ws.id,
        "title": ws.title,
        "content_bilingual": ws.content_bilingual,
        "instructions": ws.instructions
    }

@app.post("/ask-doubt")
def ask_doubt_endpoint(req: DoubtRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=req.student_identifier, role="student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    lesson = db.query(Lesson).filter_by(id=req.lesson_id).first()
    chap = db.query(Chapter).filter_by(id=lesson.chapter_id).first() if lesson else None
    subj = db.query(Subject).filter_by(id=chap.subject_id).first() if chap else None
    grade = db.query(Grade).filter_by(id=subj.grade_id).first() if subj else None

    c_num = grade.class_number if grade else 3
    s_name = subj.name if subj else "General"
    ch_name = chap.name if chap else "Topic"

    res = AIService.resolve_doubt(
        class_number=c_num,
        subject=s_name,
        chapter=ch_name,
        student_question=req.question,
        language=req.language
    )

    doubt_record = Doubt(
        student_id=user.id,
        lesson_id=req.lesson_id,
        question_text=req.question,
        response_text=res["response"],
        answered_at=datetime.datetime.utcnow()
    )
    db.add(doubt_record)
    db.commit()

    return res

# ----------------- AI CHAT & STATUS ENDPOINTS -----------------

@app.get("/api/ai/status")
def get_ai_status():
    """
    Returns Groq LLM API connection status, configured model, IndicTrans2 diagnostic test, and connection info.
    """
    test_result = AIService.test_groq_connection()
    indictrans_test = AIService.test_indictrans2_model()
    return {
        "groq_configured": bool(os.getenv("GROQ_API_KEY")),
        "groq_model": os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
        "test_connection": test_result,
        "indictrans2_santali_engine": indictrans_test
    }

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Conversational AI Chat endpoint powered by IndicTrans2 and Groq LLM.
    Automatically translates Santali student doubts into English for grounded pedagogical reasoning,
    and returns rich bilingual guidance with Santali Ol Chiki terminology.
    """
    q_clean = req.message.strip()
    if not q_clean:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    cls = req.class_number or 3
    subj = req.subject or "General"
    chap = req.chapter or "Curriculum"
    lang = req.language or "Santali (English)"

    # Detect if user question contains Santali Ol Chiki or Santali vocabulary
    has_olchiki = any('\u1C50' <= c <= '\u1C7F' for c in q_clean)
    santali_trans = None
    translated_english_query = ""

    if has_olchiki or "santali" in lang.lower():
        santali_trans = AIService.translate_santali_to_english_indictrans2(q_clean)
        translated_english_query = santali_trans.get("english", "")

    # Build prompt messages for Groq
    sys_prompt = (
        f"You are 'Vernacular AI Guru', a warm, cheerful, and encouraging educational tutor for primary school students (Class 1 to 5) in Jharkhand, India. "
        f"You are helping a Class {cls} student in {subj} ('{chap}'). "
        f"Primary language of instruction: {lang}. "
        f"Guidelines:\n"
        f"1. Greet warmly with 'Johar! (ᱡᱚᱦᱟᱨ)'.\n"
        f"2. Keep explanations clear, simple, friendly, and structured for young children with easy examples.\n"
        f"3. When using Santali or Hindi terms, use them naturally in sentences with their English or Hindi meaning. DO NOT repeat words or phrases in a loop.\n"
        f"4. Directly answer the student's question concisely."
    )

    llm_messages = [{"role": "system", "content": sys_prompt}]
    if req.history:
        for h in req.history[-6:]:  # Keep last 6 turns for context
            role = h.get("role", "user")
            content = h.get("content", "")
            if role in ["user", "assistant"] and content:
                llm_messages.append({"role": role, "content": content})

    user_query_content = q_clean
    if translated_english_query and has_olchiki:
        user_query_content = (
            f"Student Question (Santali Ol Chiki): {q_clean}\n"
            f"[IndicTrans2 English Translation: \"{translated_english_query}\"]\n"
            f"Please address this question warmly with simple explanations and Santali/English context."
        )

    llm_messages.append({"role": "user", "content": user_query_content})

    reply = AIService.call_groq_llm(llm_messages, temperature=0.6, max_tokens=450)

    source = "groq_cloud_llm"
    if not reply:
        # Fallback to local rule-based curriculum engine
        rule_res = AIService.resolve_doubt(
            class_number=cls,
            subject=subj,
            chapter=chap,
            student_question=q_clean,
            language=lang
        )
        reply = rule_res["response"]
        source = "local_curriculum_engine"

    # If student exists, optionally persist to Doubts history
    user = db.query(User).filter_by(identifier=req.user_identifier).first()
    if user:
        doubt_rec = Doubt(
            student_id=user.id,
            lesson_id=1,
            question_text=q_clean,
            response_text=reply,
            answered_at=datetime.datetime.utcnow()
        )
        db.add(doubt_rec)
        db.commit()

    return {
        "reply": reply,
        "source": source,
        "model": os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b") if source == "groq_cloud_llm" else "curriculum_rule_grounded",
        "santali_translation": santali_trans,
        "class_number": cls,
        "subject": subj,
        "chapter": chap,
        "language": lang
    }

# ----------------- QUIZ SUBMISSION & PROGRESS -----------------

@app.post("/quiz/submit")
def submit_quiz_endpoint(req: QuizSubmitRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=req.student_identifier, role="student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    quiz = db.query(Quiz).filter_by(id=req.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = db.query(QuizQuestion).filter_by(quiz_id=quiz.id).all()
    if not questions:
        raise HTTPException(status_code=400, detail="Quiz has no questions")

    correct_count = 0
    feedback = []

    for q in questions:
        selected = req.answers.get(str(q.id))
        is_correct = (selected == q.correct_option)
        if is_correct:
            correct_count += 1
        feedback.append({
            "question_id": q.id,
            "question_text": q.question_text,
            "selected_option": selected,
            "correct_option": q.correct_option,
            "is_correct": is_correct,
            "explanation": q.explanation
        })

    total = len(questions)
    score_pct = round((correct_count / total) * 100.0, 1)

    attempt = QuizAttempt(
        user_id=user.id,
        quiz_id=quiz.id,
        total_questions=total,
        correct_answers=correct_count,
        score_percentage=score_pct
    )
    db.add(attempt)

    # Update student progress
    prog = db.query(StudentProgress).filter_by(user_id=user.id, lesson_id=quiz.lesson_id).first()
    if not prog:
        prog = StudentProgress(
            user_id=user.id,
            lesson_id=quiz.lesson_id,
            is_completed=True,
            quizzes_taken=1,
            best_score=score_pct
        )
        db.add(prog)
    else:
        prog.quizzes_taken += 1
        prog.last_accessed = datetime.datetime.utcnow()
        if score_pct > prog.best_score:
            prog.best_score = score_pct
        prog.is_completed = True

    db.commit()

    return {
        "status": "SUCCESS",
        "total_questions": total,
        "correct_answers": correct_count,
        "wrong_answers": total - correct_count,
        "score_percentage": score_pct,
        "feedback": feedback
    }

@app.get("/student/progress")
def get_student_progress(identifier: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=identifier, role="student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    progs = db.query(StudentProgress).filter_by(user_id=user.id).all()
    attempts = db.query(QuizAttempt).filter_by(user_id=user.id).all()

    completed_lessons = [p.lesson_id for p in progs if p.is_completed]
    avg_score = (sum(a.score_percentage for a in attempts) / len(attempts)) if attempts else 0.0

    return {
        "student_identifier": identifier,
        "total_lessons_completed": len(completed_lessons),
        "total_quizzes_taken": len(attempts),
        "average_score": round(avg_score, 1),
        "progress_items": [{
            "lesson_id": p.lesson_id,
            "is_completed": p.is_completed,
            "quizzes_taken": p.quizzes_taken,
            "best_score": p.best_score,
            "last_accessed": str(p.last_accessed)
        } for p in progs]
    }

@app.get("/student/continue-learning")
def continue_learning(identifier: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=identifier, role="student").first()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    class_num = profile.class_number if profile else 3

    last_prog = db.query(StudentProgress).filter_by(user_id=user.id).order_by(StudentProgress.last_accessed.desc()).first()
    target_lesson_id = last_prog.lesson_id if last_prog else None

    if not target_lesson_id:
        # Default to first lesson of student's class
        grade = db.query(Grade).filter_by(class_number=class_num).first()
        subj = db.query(Subject).filter_by(grade_id=grade.id).first() if grade else None
        chap = db.query(Chapter).filter_by(subject_id=subj.id).first() if subj else None
        les = db.query(Lesson).filter_by(chapter_id=chap.id).first() if chap else None
        target_lesson_id = les.id if les else 1

    detail = get_lesson_detail(target_lesson_id, db=db)
    # Also record that the student accessed this lesson
    if user:
        p = db.query(StudentProgress).filter_by(user_id=user.id, lesson_id=target_lesson_id).first()
        if not p:
            p = StudentProgress(user_id=user.id, lesson_id=target_lesson_id, is_completed=False, last_accessed=datetime.datetime.utcnow())
            db.add(p)
            db.commit()
        else:
            p.last_accessed = datetime.datetime.utcnow()
            db.commit()

    return detail

# ----------------- OFFLINE SYNCHRONIZATION -----------------

@app.post("/sync")
def sync_endpoint(req: SyncRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=req.user_identifier).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    now = datetime.datetime.utcnow()
    pushed = len(req.progress_records) if req.progress_records else 0

    # Process pending progress from client
    if req.progress_records:
        for p in req.progress_records:
            les_id = p.get("lesson_id")
            if les_id:
                prog = db.query(StudentProgress).filter_by(user_id=user.id, lesson_id=les_id).first()
                if not prog:
                    prog = StudentProgress(
                        user_id=user.id,
                        lesson_id=les_id,
                        is_completed=p.get("is_completed", True),
                        best_score=p.get("best_score", 0.0)
                    )
                    db.add(prog)
                else:
                    if p.get("best_score", 0) > prog.best_score:
                        prog.best_score = p["best_score"]
                    prog.is_completed = True
        db.commit()

    # Pull published teacher lessons
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
        })

    # Log synchronization
    sync_log = SyncLog(
        user_id=user.id,
        last_sync_timestamp=now,
        items_pushed=pushed,
        items_pulled=len(pulled_items),
        status="SUCCESS"
    )
    db.add(sync_log)
    db.commit()

    return {
        "status": "SYNCED",
        "sync_timestamp": str(now),
        "items_pushed": pushed,
        "items_pulled": len(pulled_items) + len(pulled_worksheets) + len(pulled_quizzes),
        "updates": pulled_items,
        "offline_worksheets": pulled_worksheets,
        "offline_quizzes": pulled_quizzes
    }

@app.get("/sync/status")
def get_sync_status(identifier: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(identifier=identifier).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    last_log = db.query(SyncLog).filter_by(user_id=user.id).order_by(SyncLog.last_sync_timestamp.desc()).first()
    return {
        "identifier": identifier,
        "last_sync_timestamp": str(last_log.last_sync_timestamp) if last_log else None,
        "status": last_log.status if last_log else "NEVER_SYNCED"
    }

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Vernacular AI Pedagogy Engine",
        "curriculum_source": "J-Guruji Jharkhand (Authoritative)",
        "timestamp": str(datetime.datetime.utcnow())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
