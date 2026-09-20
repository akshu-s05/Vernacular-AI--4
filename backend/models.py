import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Float
)
from sqlalchemy.orm import relationship
from database import Base

class CurriculumSource(Base):
    __tablename__ = "curriculum_sources"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), default="J-Guruji Jharkhand")
    source_url = Column(String(500), nullable=False)
    source_authority = Column(String(200), default="DoSE&L, Govt. of Jharkhand")
    source_reference = Column(String(200), nullable=True)
    imported_at = Column(DateTime, default=datetime.datetime.utcnow)
    version = Column(String(50), default="1.0")

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    class_number = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)

    subjects = relationship("Subject", back_populates="grade", cascade="all, delete-orphan")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    original_name = Column(String(150), nullable=True)
    source_reference = Column(String(500), nullable=True)

    grade = relationship("Grade", back_populates="subjects")
    chapters = relationship("Chapter", back_populates="subject", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    original_name = Column(String(255), nullable=True)
    order = Column(Integer, default=1)
    source_reference = Column(String(500), nullable=True)

    subject = relationship("Subject", back_populates="chapters")
    lessons = relationship("Lesson", back_populates="chapter", cascade="all, delete-orphan")

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=True)
    topic = Column(String(255), nullable=True)
    source_reference = Column(String(500), nullable=True)
    order = Column(Integer, default=1)

    chapter = relationship("Chapter", back_populates="lessons")
    contents = relationship("CurriculumContent", back_populates="lesson", cascade="all, delete-orphan")
    teacher_contents = relationship("TeacherContent", back_populates="lesson", cascade="all, delete-orphan")

class CurriculumContent(Base):
    __tablename__ = "curriculum_contents"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    content_type = Column(String(50), default="textbook")
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=True)
    language = Column(String(50), default="Hindi")
    source_reference = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    lesson = relationship("Lesson", back_populates="contents")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(20), nullable=False) # "teacher" or "student"
    identifier = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    school = Column(String(200), default="Government Primary School")
    password_hash = Column(String(255), nullable=False)
    preferred_language = Column(String(50), default="Santali")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    teacher_profile = relationship("TeacherProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    student_profile = relationship("StudentProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")

class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    teacher_id = Column(String(50), unique=True, index=True, nullable=False)
    department = Column(String(100), default="Primary Section")

    user = relationship("User", back_populates="teacher_profile")

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    class_number = Column(Integer, nullable=False, default=3)

    user = relationship("User", back_populates="student_profile")

class TeacherContent(Base):
    __tablename__ = "teacher_contents"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    activities = Column(Text, nullable=True)
    examples = Column(Text, nullable=True)
    language = Column(String(50), default="Hindi")
    santali_translation = Column(Text, nullable=True)
    is_published = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    server_version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    published_at = Column(DateTime, nullable=True)

    lesson = relationship("Lesson", back_populates="teacher_contents")
    versions = relationship("LessonVersion", back_populates="teacher_content", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="teacher_content", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="teacher_content", cascade="all, delete-orphan")
    worksheets = relationship("Worksheet", back_populates="teacher_content", cascade="all, delete-orphan")

class LessonVersion(Base):
    __tablename__ = "lesson_versions"

    id = Column(Integer, primary_key=True, index=True)
    teacher_content_id = Column(Integer, ForeignKey("teacher_contents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    santali_translation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_by = Column(String(100), nullable=True)

    teacher_content = relationship("TeacherContent", back_populates="versions")

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    teacher_content_id = Column(Integer, ForeignKey("teacher_contents.id"), nullable=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    language = Column(String(50), default="Santali")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    teacher_content = relationship("TeacherContent", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(255), nullable=False)
    option_b = Column(String(255), nullable=False)
    option_c = Column(String(255), nullable=False)
    option_d = Column(String(255), nullable=False)
    correct_option = Column(String(10), nullable=False) # "A", "B", "C", "D"
    explanation = Column(Text, nullable=True)

    quiz = relationship("Quiz", back_populates="questions")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False, index=True)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    score_percentage = Column(Float, nullable=False)
    completed_at = Column(DateTime, default=datetime.datetime.utcnow)

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    teacher_content_id = Column(Integer, ForeignKey("teacher_contents.id"), nullable=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    front_text = Column(Text, nullable=False)
    back_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    teacher_content = relationship("TeacherContent", back_populates="flashcards")

class Worksheet(Base):
    __tablename__ = "worksheets"

    id = Column(Integer, primary_key=True, index=True)
    teacher_content_id = Column(Integer, ForeignKey("teacher_contents.id"), nullable=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content_bilingual = Column(Text, nullable=False) # Bilingual Hindi/English + Santali
    instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    teacher_content = relationship("TeacherContent", back_populates="worksheets")

class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    is_completed = Column(Boolean, default=False)
    last_accessed = Column(DateTime, default=datetime.datetime.utcnow)
    quizzes_taken = Column(Integer, default=0)
    best_score = Column(Float, default=0.0)

class Doubt(Base):
    __tablename__ = "doubts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    audio_path = Column(String(500), nullable=True)
    response_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    answered_at = Column(DateTime, nullable=True)

class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    last_sync_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    items_pushed = Column(Integer, default=0)
    items_pulled = Column(Integer, default=0)
    status = Column(String(50), default="SUCCESS")
