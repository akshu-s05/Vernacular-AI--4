# Vernacular AI Pedagogy Platform
### AI-Powered Vernacular Pedagogy and Real-Time Translation Tool for Mother Tongue-Based Primary Education
**Problem Statement:** SIH26042  
**Primary Prototype Language:** Santali (ᱚᱞ ᱪᱤᱠᱤ / Ol Chiki & Roman script)  
**Extensible Target Languages:** Ho, Mundari  
**Target User Roles:** Primary Teachers & Primary School Students (Classes 1 to 5)

---

## 1. Authoritative Syllabus Source: J-Guruji Jharkhand
> **CRITICAL ARCHITECTURAL GUARANTEE:**
> **J-Guruji Jharkhand (DoSE&L, Govt. of Jharkhand)** is the **sole authoritative source of truth** for all curriculum hierarchy in this application:
> `https://jguruji.jharkhand.gov.in/`
>
> Neither LLMs, general web scrapers, Wikipedia, CBSE, nor NCERT were used to invent or guess syllabus information. All 1,373 syllabus records, subjects, chapters, and topics were extracted directly from J-Guruji.

### Verified Database Curriculum Statistics
From the actual SQLite database populated via `data/imports/extract_jguruji.ps1` and `backend/import_curriculum.py`:

- **Total Class 1–5 Subjects:** 35
- **Total Class 1–5 Chapters:** 801
- **Total Class 1–5 Lessons / Topics:** 1,254
- **Total Raw Extracted Records:** 1,373

#### Class-by-Class Breakdown:
- **Class 1:** 7 Subjects, 127 Chapters, 194 Lessons/Topics
  - English (11 chapters), Hindi (34 chapters), Library (1 chapters), Mathematics (23 chapters), Teacher Resource (2 chapters), Urdu (45 chapters), Value Education (11 chapters)
- **Class 2:** 7 Subjects, 154 Chapters, 214 Lessons/Topics
  - English (33 chapters), Hindi (45 chapters), Library (1 chapters), Mathematics (23 chapters), Teacher Resource (2 chapters), Urdu (39 chapters), Value Education (11 chapters)
- **Class 3:** 7 Subjects, 170 Chapters, 272 Lessons/Topics
  - English (33 chapters), Environmental Studies (30 chapters), Hindi (34 chapters), Library (1 chapters), Mathematics (25 chapters), Urdu (36 chapters), Value Education (11 chapters)
- **Class 4:** 7 Subjects, 175 Chapters, 287 Lessons/Topics
  - English (40 chapters), Environmental Studies (49 chapters), Hindi (26 chapters), Library (1 chapters), Mathematics (26 chapters), Urdu (22 chapters), Value Education (11 chapters)
- **Class 5:** 7 Subjects, 175 Chapters, 287 Lessons/Topics
  - English (39 chapters), Environmental Studies (44 chapters), Hindi (32 chapters), Library (1 chapters), Mathematics (25 chapters), Urdu (23 chapters), Value Education (11 chapters)

---

## 2. Architecture & Connected Components

The project is architected as a connected, modular platform:

```
Vernacular AI--4/
├── backend/
│   ├── main.py                  # FastAPI Application with 20+ RESTful endpoints
│   ├── database.py              # SQLite / Relational Engine & SessionLocal
│   ├── models.py                # Complete SQLAlchemy relational schemas
│   ├── ai_services.py           # Curriculum-grounded AI, Translation, Quiz, Flashcards, Doubts
│   ├── import_curriculum.py     # Database population pipeline from raw J-Guruji extraction
│   ├── validate_curriculum.py   # Statistical validation script
│   ├── vernacular_ai.db         # Persistent SQLite Database
│   └── static/
│       └── index.html           # Single connected frontend (Teacher & Student Portals)
├── flutter_app/
│   ├── lib/
│   │   ├── services/
│   │   │   └── api_service.dart # Dart/Flutter API client connecting to backend
│   │   └── main.dart            # Flutter cross-platform mobile/web entry
│   ├── test/
│   │   └── app_test.dart        # Dart unit verification tests
│   └── pubspec.yaml             # Flutter dependencies specification
├── data/
│   ├── curriculum/
│   │   └── jguruji_class1_5_raw.json # 1,373 authentic records extracted from J-Guruji
│   └── imports/
│       └── extract_jguruji.ps1  # Automated crawler and extractor for jguruji.jharkhand.gov.in
├── tests/
│   └── test_backend.py          # Complete integration test suite (10/10 passing)
├── .env.example                 # Config template
└── README.md
```

---

## 3. Demo Accounts
The database is pre-seeded with credentials:

- **Teacher Account:**
  - **Teacher ID:** `teacher01`
  - **Password:** `teacher123`
  - **Name:** Anita Kumar
  - **School:** Government Primary School

- **Student Account:**
  - **Student ID:** `student01`
  - **Password:** `student123`
  - **Name:** Rahul
  - **Class:** 3
  - **Preferred Language:** Santali

---

## 4. How to Run Locally

### Start Backend and Web Application
```powershell
# From project root:
.\tools\python311\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Open your browser at:
`http://127.0.0.1:8000/app/`

### Run Automated Backend Tests
```powershell
.\tools\python311\python.exe tests\test_backend.py
```

### Validate Database Statistics
```powershell
.\tools\python311\python.exe backend\validate_curriculum.py
```

---

## 5. Completed Workflows & Verification Checklist

- [x] **J-Guruji Direct Extraction:** 1,373 authentic records crawled and verified without hallucinating syllabus names.
- [x] **Relational Database:** SQLite database with Grade, Subject, Chapter, Lesson, Content, User, Quiz, Flashcard, Worksheet, Doubt, and Sync schemas.
- [x] **Role Selection & Secure Authentication:** Teacher and Student login/registration with bcrypt hashing and JWT tokens.
- [x] **Dynamic Dropdowns:** Teacher lesson creation and student browsing load strictly from J-Guruji database.
- [x] **Document Upload & Curriculum Mapping:** Files uploaded by teachers are checked against existing J-Guruji chapters and mapped without inventing new syllabi.
- [x] **Translation Engine:** Real-time Hindi/English to Santali translation core supporting Ol Chiki and Roman transliteration.
- [x] **Voice-to-Voice Architecture:** Simulated speech input with latency benchmarking and Santali TTS playback support.
- [x] **Curriculum-Grounded AI:** Lesson drafts, worksheets, 5-question quizzes, and doubt explanations are constrained strictly within the selected J-Guruji curriculum item.
- [x] **Interactive 5-Question Quiz:** Color-coded immediate feedback, score calculation, and progress persistence.
- [x] **Interactive Flashcards:** 3D flip card interaction with Ol Chiki script display and Next/Previous navigation.
- [x] **Teacher &rarr; Student Publishing & Sync:** Versioned lesson updates downloaded by students on Sync.
