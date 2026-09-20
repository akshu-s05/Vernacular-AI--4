import unittest
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

class TestVernacularAIPedagogyExtended(unittest.TestCase):

    def test_01_server_health(self):
        res = requests.get(f"{BASE_URL}/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertIn("J-Guruji", data["curriculum_source"])

    def test_02_teacher_registration_and_login(self):
        teacher_id = "test_teacher_auto"
        # Register
        reg_res = requests.post(
            f"{BASE_URL}/auth/teacher/register",
            json={
                "name": "Prof S Soren",
                "school": "Dumka Tribal Model School",
                "teacher_id": teacher_id,
                "password": "Password@123",
                "preferred_language": "English"
            }
        )
        self.assertIn(reg_res.status_code, [200, 400])

        # Login
        login_res = requests.post(
            f"{BASE_URL}/auth/teacher/login",
            json={"identifier": teacher_id, "password": "Password@123"}
        )
        self.assertEqual(login_res.status_code, 200)
        data = login_res.json()
        self.assertEqual(data["user"]["identifier"], teacher_id)
        self.assertEqual(data["user"]["name"], "Prof S Soren")

    def test_03_student_registration_and_login(self):
        student_id = "test_student_auto"
        # Register
        reg_res = requests.post(
            f"{BASE_URL}/auth/student/register",
            json={
                "name": "Baha Marandi",
                "school": "Dumka Primary School",
                "student_id": student_id,
                "password": "Student@123",
                "class_number": 3,
                "preferred_language": "Santali (English)"
            }
        )
        self.assertIn(reg_res.status_code, [200, 400])

        # Login
        login_res = requests.post(
            f"{BASE_URL}/auth/student/login",
            json={"identifier": student_id, "password": "Student@123"}
        )
        self.assertEqual(login_res.status_code, 200)
        data = login_res.json()
        self.assertEqual(data["user"]["identifier"], student_id)
        self.assertEqual(data["user"]["class_number"], 3)
        self.assertEqual(data["user"]["preferred_language"], "Santali (English)")

    def test_04_curriculum_flow_and_jguruji_integration(self):
        # Grade -> Subject -> Chapter -> Subtopic
        grade_res = requests.get(f"{BASE_URL}/curriculum/3")
        self.assertEqual(grade_res.status_code, 200)
        g_data = grade_res.json()
        self.assertEqual(g_data["grade"], 3)
        self.assertGreater(len(g_data["subjects"]), 0)

        subject_id = g_data["subjects"][0]["id"]
        chap_res = requests.get(f"{BASE_URL}/chapters/{subject_id}")
        self.assertEqual(chap_res.status_code, 200)
        chapters = chap_res.json()
        self.assertGreater(len(chapters), 0)

        chapter_id = chapters[0]["id"]
        sub_res = requests.get(f"{BASE_URL}/subtopics/{chapter_id}")
        self.assertEqual(sub_res.status_code, 200)
        subtopics = sub_res.json()
        self.assertGreater(len(subtopics), 0)
        self.assertIn("title", subtopics[0])

    def test_05_teacher_document_upload_and_mapping(self):
        # Teacher uploads educational text matching J-Guruji syllabus ('My Classroom' chapter)
        files = {"file": ("classroom_lesson.txt", b"My Classroom lesson in primary education. Learning words and objects.")}
        data = {"teacher_identifier": "test_teacher_auto"}
        res = requests.post(f"{BASE_URL}/upload-document", files=files, data=data)
        self.assertEqual(res.status_code, 200)
        res_data = res.json()
        self.assertEqual(res_data["status"], "SUCCESS")
        self.assertIn("mapped_lesson", res_data)

    def test_06_translation_word_sentence_chapter(self):
        # English -> Santali
        res_word = requests.post(
            f"{BASE_URL}/translate",
            json={"text": "hello", "source_language": "English", "target_language": "Santali"}
        )
        self.assertEqual(res_word.status_code, 200)
        self.assertIn("Johar", res_word.json()["translated_text"])

        # Sentence translation
        res_sent = requests.post(
            f"{BASE_URL}/translate",
            json={"text": "teacher gives book to student", "source_language": "English", "target_language": "Santali"}
        )
        self.assertEqual(res_sent.status_code, 200)
        self.assertIn("Machet", res_sent.json()["translated_text"])

    def test_07_voice_translation_pipeline(self):
        res = requests.post(
            f"{BASE_URL}/voice-translate",
            json={
                "transcript_text": "नमस्ते बच्चों, आज हम विद्यालय में पढ़ाई करेंगे",
                "source_language": "Hindi",
                "target_language": "Santali"
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertIn("translated_text", data)
        self.assertIn("latency_seconds", data)

    def test_08_ai_assistant_dynamic_doubt_resolution(self):
        # 1. Santali (English)
        res_en = requests.post(
            f"{BASE_URL}/ask-doubt",
            json={
                "student_identifier": "test_student_auto",
                "lesson_id": 1,
                "question": "How do we say subtraction in Santali?",
                "language": "Santali (English)"
            }
        )
        self.assertEqual(res_en.status_code, 200)
        self.assertIn("Subtraction", res_en.json()["response"])
        self.assertIn("Bhegar", res_en.json()["response"])

        # 2. Santali (Hindi)
        res_hi = requests.post(
            f"{BASE_URL}/ask-doubt",
            json={
                "student_identifier": "test_student_auto",
                "lesson_id": 1,
                "question": "संथाली में जोड़ को क्या कहते हैं?",
                "language": "Santali (Hindi)"
            }
        )
        self.assertEqual(res_hi.status_code, 200)
        self.assertIn("जोड़", res_hi.json()["response"])
        self.assertIn("Mesa", res_hi.json()["response"])

        # 3. Hindi
        res_pure_hi = requests.post(
            f"{BASE_URL}/ask-doubt",
            json={
                "student_identifier": "test_student_auto",
                "lesson_id": 1,
                "question": "गिनती कैसे सीखते हैं?",
                "language": "Hindi"
            }
        )
        self.assertEqual(res_pure_hi.status_code, 200)
        self.assertIn("संख्याओं", res_pure_hi.json()["response"])

        # 4. English
        res_pure_en = requests.post(
            f"{BASE_URL}/ask-doubt",
            json={
                "student_identifier": "test_student_auto",
                "lesson_id": 1,
                "question": "How to count in Santali?",
                "language": "English"
            }
        )
        self.assertEqual(res_pure_en.status_code, 200)
        self.assertIn("numbers", res_pure_en.json()["response"].lower())

    def test_09_quiz_flashcard_worksheet_generation(self):
        # Quiz
        q_res = requests.post(
            f"{BASE_URL}/generate-quiz",
            json={"lesson_id": 1, "class_number": 3, "subject": "Mathematics", "chapter": "Numbers", "language": "Santali"}
        )
        self.assertEqual(q_res.status_code, 200)
        q_data = q_res.json()
        self.assertEqual(q_data["total_questions"], 5)
        self.assertEqual(len(q_data["questions"]), 5)

        # Flashcards
        fc_res = requests.post(
            f"{BASE_URL}/generate-flashcards",
            json={"lesson_id": 1, "class_number": 3, "subject": "Mathematics", "chapter": "Numbers"}
        )
        self.assertEqual(fc_res.status_code, 200)
        fc_data = fc_res.json()
        self.assertGreaterEqual(len(fc_data["flashcards"]), 5)

        # Worksheet
        ws_res = requests.post(
            f"{BASE_URL}/generate-worksheet",
            json={"lesson_id": 1, "class_number": 3, "subject": "Mathematics", "chapter": "Numbers"}
        )
        self.assertEqual(ws_res.status_code, 200)
        ws_data = ws_res.json()
        self.assertIn("content_bilingual", ws_data)

    def test_10_teacher_draft_save_publish_sync(self):
        # 1. Save draft
        draft_res = requests.post(
            f"{BASE_URL}/lessons",
            json={
                "teacher_identifier": "test_teacher_auto",
                "lesson_id": 1,
                "title": "Numbers and Counting in Santali",
                "content": "Explanation of counting from 1 to 10 for Class 3 students.",
                "santali_translation": "ᱢᱤᱫ, ᱵᱟᱨ, ᱯᱮ, ᱯᱩᱱ, ᱢᱚᱬᱮ, ᱛᱩᱨᱩᱭ, ᱮᱭᱟᱭ, ᱤᱨᱟᱹᱞ, ᱟᱨᱮ, ᱜᱮᱞ",
                "activities": "Count 5 leaves and write down in Ol Chiki",
                "publish_now": False
            }
        )
        self.assertEqual(draft_res.status_code, 200)
        lesson_record = draft_res.json()
        self.assertEqual(lesson_record["status"], "SUCCESS")
        content_id = lesson_record["content"]

        # 2. Publish
        pub_res = requests.post(f"{BASE_URL}/lessons/{content_id}/publish")
        self.assertEqual(pub_res.status_code, 200)
        self.assertTrue(pub_res.json()["published"])

        # 3. Student sync to pull published lesson and offline assets
        sync_res = requests.post(
            f"{BASE_URL}/sync",
            json={
                "user_identifier": "test_student_auto",
                "role": "student",
                "progress_records": [{"lesson_id": 1, "is_completed": True, "best_score": 90.0}]
            }
        )
        self.assertEqual(sync_res.status_code, 200)
        sync_data = sync_res.json()
        self.assertEqual(sync_data["status"], "SYNCED")
        self.assertGreater(sync_data["items_pulled"], 0)
        self.assertIn("offline_worksheets", sync_data)
        self.assertIn("offline_quizzes", sync_data)

        # 4. Check student progress
        prog_res = requests.get(f"{BASE_URL}/student/progress?identifier=test_student_auto")
        self.assertEqual(prog_res.status_code, 200)
        prog_data = prog_res.json()
        self.assertGreaterEqual(prog_data["total_lessons_completed"], 1)

if __name__ == "__main__":
    unittest.main()
