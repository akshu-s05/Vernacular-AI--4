import unittest
import json
import requests

BASE_URL = "http://127.0.0.1:8000"

class TestVernacularAIPedagogy(unittest.TestCase):

    def test_01_health_check(self):
        res = requests.get(f"{BASE_URL}/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "HEALTHY")
        self.assertIn("J-Guruji", data["curriculum_source"])

    def test_02_teacher_auth(self):
        res = requests.post(
            f"{BASE_URL}/auth/teacher/login",
            json={"identifier": "teacher01", "password": "teacher123"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["identifier"], "teacher01")

    def test_03_student_auth(self):
        res = requests.post(
            f"{BASE_URL}/auth/student/login",
            json={"identifier": "student01", "password": "student123"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["identifier"], "student01")

    def test_04_jguruji_curriculum_grades(self):
        res = requests.get(f"{BASE_URL}/curriculum")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data["grades"]), 5) # Classes 1 to 5 strictly

    def test_05_jguruji_class3_subjects(self):
        res = requests.get(f"{BASE_URL}/curriculum/3")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        subject_names = [s["name"] for s in data["subjects"]]
        self.assertIn("Mathematics", subject_names)
        self.assertIn("Environmental Studies", subject_names)
        self.assertIn("Hindi", subject_names)

    def test_06_translation_santali(self):
        res = requests.post(
            f"{BASE_URL}/translate",
            json={"text": "namaste", "source_language": "English", "target_language": "Santali"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("Johar", data["translated_text"])

    def test_07_grounded_lesson_generation(self):
        res = requests.post(
            f"{BASE_URL}/generate-lesson",
            json={
                "class_number": 3,
                "subject": "Mathematics",
                "chapter": "Counting",
                "topic": "Numbers 1 to 9",
                "language": "Santali"
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("Numbers 1 to 9", data["title"])
        self.assertIn("J-Guruji Jharkhand", data["grounded_source"])


    def test_08_grounded_quiz_minimum_5_questions(self):
        res = requests.post(
            f"{BASE_URL}/generate-quiz",
            json={
                "lesson_id": 1,
                "class_number": 3,
                "subject": "Mathematics",
                "chapter": "Shapes and Space",
                "topic": "Shapes",
                "language": "Santali"
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(data["total_questions"], 5)
        self.assertGreaterEqual(len(data["questions"]), 5)

    def test_09_quiz_submission_and_scoring(self):
        # Generate a quiz first
        q_res = requests.post(
            f"{BASE_URL}/generate-quiz",
            json={
                "lesson_id": 1,
                "class_number": 3,
                "subject": "Mathematics",
                "chapter": "Numbers",
                "topic": "Addition",
                "language": "Santali"
            }
        ).json()

        quiz_id = q_res["quiz_id"]
        # Submit answers (answering A for all)
        answers = {str(q["id"]): "A" for q in q_res["questions"]}
        sub_res = requests.post(
            f"{BASE_URL}/quiz/submit",
            json={
                "student_identifier": "student01",
                "quiz_id": quiz_id,
                "answers": answers
            }
        )
        self.assertEqual(sub_res.status_code, 200)
        result = sub_res.json()
        self.assertIn("score_percentage", result)
        self.assertEqual(result["total_questions"], len(answers))

    def test_10_sync_pipeline(self):
        res = requests.post(
            f"{BASE_URL}/sync",
            json={
                "user_identifier": "student01",
                "role": "student",
                "progress_records": [{"lesson_id": 1, "is_completed": True, "best_score": 100.0}]
            }
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "SYNCED")
        self.assertIn("updates", data)

if __name__ == "__main__":
    unittest.main()
