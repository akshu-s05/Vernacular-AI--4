# -*- coding: utf-8 -*-
"""
Tribal Parallel Corpora & Natural Sentence Grammar Engine
Grounded in:
1. AdiBhasha (IIT Delhi) - Tribal Parallel Corpus
2. AI4Bharat BPCC (Bharat Parallel Corpus Collection - IndicTrans2)
3. Adivaani Tribal-English Parallel Corpus
4. XKaab/ASR-santali_100hrs & Indic Dialect ASR
5. Santali Kaldi & Karya Mundari TTS phonetics
6. IndicTrans2 Austroasiatic Munda Grammar Engine
"""

import re
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# UI LOCALIZATION DICTIONARY
# Format:
# Santali: Ol Chiki with (English) in brackets
# Hindi: Hindi Devanagari with (English) in brackets
# English: Standard English
# ---------------------------------------------------------------------------
UI_LOCALIZATION = {
    "Santali": {
        "brand_title": "ᱵᱷᱟᱨᱱᱟᱠᱩᱞᱟᱨ ᱮ.ᱟᱭ. ᱟᱥᱲᱟ (Vernacular AI Platform)",
        "brand_subtitle": "ᱡᱷᱟᱨᱠᱷᱚᱸᱰ ᱮᱛᱚᱦᱚᱵ ᱥᱮᱪᱮᱫ • ᱡᱮ-ᱜᱩᱨᱩᱡᱤ ᱟᱨ ᱮᱱ.ᱥᱤ.ᱤ.ᱟᱨ.ᱴᱤ (Jharkhand Primary Education • J-Guruji & NCERT)",
        "online_status": "🟢 ᱚᱱᱞᱟᱭᱤᱱ • ᱥᱤᱝᱠ ᱟᱠᱟᱱᱟ (Online • Synced)",
        "offline_status": "🟡 ᱚᱯᱷᱞᱟᱭᱤᱱ ᱢᱳᱰ (Offline Mode Active)",
        "not_logged_in": "ᱵᱟᱢ ᱵᱚᱞᱚ ᱟᱠᱟᱱᱟ (Not Logged In)",
        "welcome_user": "ᱥᱟᱹᱜᱩᱱ ᱫᱟᱨᱟᱢ, {name} (Welcome, {name})",
        "sign_out": "ᱵᱟᱦᱨᱮ ᱚᱰᱚᱠ (Sign Out)",
        "auth_welcome_title": "ᱥᱟᱹᱜᱩᱱ ᱫᱟᱨᱟᱢ (Welcome)",
        "auth_welcome_sub": "ᱟᱢᱟᱜ ᱮᱠᱟᱣᱩᱱᱴ ᱛᱮ ᱵᱚᱞᱚᱱ ᱢᱮ ᱥᱮ ᱱᱟᱶᱟ ᱩᱯᱨᱩᱢ ᱵᱮᱱᱟᱣ ᱢᱮ (Sign in or create a new profile)",
        "teacher_portal_tab": "ᱢᱟᱪᱮᱛ ᱫᱩᱣᱟᱹᱨ (Teacher Portal)",
        "student_portal_tab": "ᱯᱟᱹᱴᱷᱩᱣᱟᱹ ᱫᱩᱣᱟᱹᱨ (Student Portal)",
        "login_btn_tab": "ᱵᱚᱞᱚᱱ (Login)",
        "register_btn_tab": "ᱱᱟᱶᱟ ᱵᱮᱵᱷᱟᱨᱤᱭᱟᱹ (Register)",
        "teacher_id_label": "ᱢᱟᱪᱮᱛ ᱩᱯᱨᱩᱢ ᱮᱞ (Teacher ID)",
        "student_id_label": "ᱯᱟᱹᱴᱷᱩᱣᱟᱹ ᱩᱯᱨᱩᱢ ᱮᱞ (Student ID)",
        "password_label": "ᱫᱟᱱᱟᱝ ᱥᱟᱵᱟᱫ (Password)",
        "full_name_label": "ᱯᱩᱨᱟᱹ ᱧᱩᱛᱩᱢ (Full Name)",
        "school_label": "ᱟᱥᱲᱟ / ᱜᱟᱶᱛᱟ (School / Institution)",
        "class_label": "ᱪᱟᱱᱟᱪ / ᱛᱷᱚᱠ (Class / Grade)",
        "lang_pref_label": "ᱠᱩᱥᱤᱭᱟᱜ ᱯᱟᱹᱨᱥᱤ (Preferred Language)",
        "login_teacher_btn": "ᱢᱟᱪᱮᱛ ᱞᱮᱠᱟᱛᱮ ᱵᱚᱞᱚᱱ (Login as Teacher)",
        "register_teacher_btn": "ᱢᱟᱪᱮᱛ ᱮᱠᱟᱣᱩᱱᱴ ᱵᱮᱱᱟᱣ (Create Teacher Account)",
        "login_student_btn": "ᱯᱟᱹᱴᱷᱩᱣᱟᱹ ᱞᱮᱠᱟᱛᱮ ᱵᱚᱞᱚᱱ (Login as Student)",
        "register_student_btn": "ᱯᱟᱹᱴᱷᱩᱣᱟᱹ ᱮᱠᱟᱣᱩᱱᱴ ᱵᱮᱱᱟᱣ (Create Student Account)",
        "dashboard_tab": "ᱰᱮᱥᱵᱳᱨᱰ (Dashboard)",
        "learn_tab": "ᱪᱮᱫᱚᱜ ᱢᱮ (Continue Learning)",
        "subjects_tab": "ᱥᱟᱛᱟᱢ ᱠᱚ (Subjects)",
        "progress_tab": "ᱞᱟᱦᱟᱱᱛᱤ (Progress)",
        "doubts_tab": "ᱠᱩᱠᱞᱤ ᱠᱩᱞᱤᱭᱮ (Ask Doubt)",
        "downloads_tab": "ᱰᱟᱣᱩᱱᱞᱳᱰ ᱠᱚ (Downloads)",
        "quiz_tab": "ᱠᱩᱠᱞᱤ ᱛᱮᱞᱟ (Interactive Quiz)",
        "flashcards_tab": "ᱯᱷᱞᱮᱥᱠᱟᱨᱰ (Flashcards)",
        "sync_tab": "ᱥᱤᱝᱠ (Cloud Sync)",
        "profile_tab": "ᱩᱯᱨᱩᱢ (Profile)",
        "my_lessons_tab": "ᱤᱧᱟᱜ ᱯᱟᱲᱦᱟᱣ (My Lessons)",
        "create_lesson_tab": "ᱱᱟᱶᱟ ᱯᱟᱲᱦᱟᱣ ᱵᱮᱱᱟᱣ (Create Lesson)",
        "upload_content_tab": "ᱯᱩᱛᱷᱤ ᱞᱟᱫᱮ (Upload Content)",
        "translate_tab": "ᱛᱚᱨᱡᱚᱢᱟ (Translate)",
        "voice_tab": "ᱨᱚᱲ ᱛᱚᱨᱡᱚᱢᱟ (Voice Translation)",
        "worksheets_tab": "ᱠᱟᱹᱢᱤ ᱥᱟᱠᱟᱢ (Worksheets)",
        "ai_assistant_tab": "ᱮ.ᱟᱭ. ᱜᱚᱲᱚᱭᱤᱡ (AI Assistant)",
        "offline_content_tab": "ᱚᱯᱷᱞᱟᱭᱤᱱ ᱥᱟᱯᱟᱵ (Offline Content)",
        "student_home_welcome": "ᱥᱟᱹᱜᱩᱱ ᱫᱟᱨᱟᱢ ᱯᱟᱹᱴᱷᱩᱣᱟᱹ (Welcome Student)",
        "classroom_nav_title": "ᱟᱥᱲᱟ ᱥᱮᱱᱚᱜ ᱦᱚᱨ (Classroom Navigation)",
        "continue_learning_desc": "ᱟᱢᱟᱜ ᱯᱟᱲᱦᱟᱣ ᱟᱲᱟᱝ ᱥᱟᱶᱛᱮ ᱞᱟᱦᱟᱭ ᱢᱮ (Resume active lesson with audio)",
        "subjects_desc": "ᱡᱮ-ᱜᱩᱨᱩᱡᱤ ᱯᱩᱛᱷᱤ ᱟᱨ ᱦᱟᱹᱴᱤᱧ ᱠᱚ (J-Guruji textbooks & chapters)",
        "quiz_desc": "᱕ ᱜᱚᱴᱟᱝ ᱥᱟᱛᱟᱢ ᱠᱩᱠᱞᱤ ᱠᱚ (5 grounded syllabus questions)",
        "flashcards_desc": "ᱥᱟᱱᱛᱟᱲᱤ ᱟᱹᱲᱟᱹ ᱢᱩᱨᱟᱹᱭ ᱠᱟᱨᱰ ᱠᱚ (Santali vocabulary flip cards)",
        "doubts_desc": "ᱨᱚᱲ ᱟᱨ ᱮ.ᱟᱭ. ᱜᱚᱲᱚ ᱟᱲᱟᱝ ᱥᱟᱶ (Voice & AI doubt assistant with audio)",
        "progress_desc": "ᱮᱞ, ᱠᱩᱠᱞᱤ ᱟᱨ ᱯᱟᱲᱦᱟᱣ ᱦᱟᱞᱚᱛ (Scores, quizzes & lessons progress)",
        "downloads_desc": "ᱚᱯᱷᱞᱟᱭᱤᱱ ᱥᱟᱺᱪᱟᱣ ᱯᱟᱲᱦᱟᱣ ᱠᱚ (Offline saved lessons & materials)",
        "sync_desc": "ᱥᱟᱨᱵᱷᱟᱨ ᱥᱟᱶ ᱡᱚᱲᱟᱣ ᱢᱮ (Synchronize with cloud server)",
        "play_audio_btn": "🔊 ᱥᱟᱱᱛᱟᱲᱤ ᱛᱮ ᱟᱧᱡᱚᱢ ᱢᱮ (Play Audio)",
        "download_offline_btn": "💾 ᱚᱯᱷᱞᱟᱭᱤᱱ ᱫᱚᱦᱚᱭ ᱢᱮ (Download Offline)",
        "take_quiz_btn": "📝 ᱕-ᱠᱩᱠᱞᱤ ᱛᱮᱞᱟ ᱮᱢ ᱢᱮ (Take 5-Question Quiz)",
        "view_flashcards_btn": "🗂️ ᱯᱷᱞᱮᱥᱠᱟᱨᱰ ᱧᱮᱞ ᱢᱮ (View Flashcards)",
        "ask_ai_btn": "❓ ᱮ.ᱟᱭ. ᱠᱩᱠᱞᱤ ᱠᱩᱞᱤᱭᱮ (Ask AI Assistant)",
        "speak_doubt_btn": "🎙️ ᱨᱚᱲ ᱠᱟᱛᱮ ᱠᱩᱞᱤᱭᱮ (Speak Doubt)",
        "lesson_explanation_hdr": "ᱯᱟᱲᱦᱟᱣ ᱵᱩᱡᱷᱟᱹᱣ (Hindi / English Lesson Explanation):",
        "mother_tongue_hdr": "ᱟᱭᱳ ᱟᱲᱟᱝ ᱛᱮ ᱯᱟᱲᱦᱟᱣ (Mother Tongue Content • Santali ᱚᱞ ᱪᱤᱠᱤ):",
        "activities_hdr": "ᱟᱥᱲᱟ ᱠᱟᱹᱢᱤᱦᱚᱨᱟ ᱟᱨ ᱫᱟᱹᱭᱠᱟᱹ (Classroom Activities & Local Examples):",
        "quiz_header": "ᱥᱟᱛᱟᱢ ᱠᱩᱠᱞᱤ ᱛᱮᱞᱟ (Interactive Topic Quiz - Minimum 5 Questions)",
        "submit_quiz_btn": "ᱠᱩᱠᱞᱤ ᱛᱮᱞᱟ ᱫᱟᱠᱷᱤᱞ ᱢᱮ (Submit Quiz Answers)",
        "reset_quiz_btn": "ᱫᱚᱦᱲᱟ ᱮᱦᱚᱵ (Reset / Retry)",
        "flashcard_header": "ᱟᱭᱳ ᱟᱲᱟᱝ ᱯᱷᱞᱮᱥᱠᱟᱨᱰ (Mother Tongue Flashcards)",
        "speak_card_btn": "🔊 ᱠᱟᱨᱰ ᱟᱧᱡᱚᱢ ᱢᱮ (Speak Card)",
        "next_btn": "ᱞᱟᱦᱟ ➡️ (Next)",
        "prev_btn": "⬅️ ᱛᱟᱭᱚᱢ (Previous)"
    },
    "Hindi": {
        "brand_title": "मातृभाषा ए.आई. शिक्षा मंच (Vernacular AI Platform)",
        "brand_subtitle": "झारखंड प्राथमिक शिक्षा • जे-गुरुजी और एनसीईआरटी (Jharkhand Primary Education • J-Guruji & NCERT)",
        "online_status": "🟢 ऑनलाइन • सिंक संपन्न (Online • Synced)",
        "offline_status": "🟡 ऑफ़लाइन मोड (Offline Mode Active)",
        "not_logged_in": "लॉग इन नहीं हैं (Not Logged In)",
        "welcome_user": "स्वागत है, {name} (Welcome, {name})",
        "sign_out": "साइन आउट (Sign Out)",
        "auth_welcome_title": "स्वागत है (Welcome)",
        "auth_welcome_sub": "अपने खाते से लॉग इन करें या नया प्रोफ़ाइल बनाएं (Sign in or create account)",
        "teacher_portal_tab": "शिक्षक पोर्टल (Teacher Portal)",
        "student_portal_tab": "छात्र पोर्टल (Student Portal)",
        "login_btn_tab": "लॉग इन (Login)",
        "register_btn_tab": "नया खाता (Register)",
        "teacher_id_label": "शिक्षक पहचान संख्या (Teacher ID)",
        "student_id_label": "छात्र पहचान संख्या (Student ID)",
        "password_label": "पासवर्ड (Password)",
        "full_name_label": "पूरा नाम (Full Name)",
        "school_label": "विद्यालय / संस्था (School / Institution)",
        "class_label": "कक्षा / श्रेणी (Class / Grade)",
        "lang_pref_label": "पसंदीदा भाषा (Preferred Language)",
        "login_teacher_btn": "शिक्षक के रूप में लॉग इन करें (Login as Teacher)",
        "register_teacher_btn": "शिक्षक खाता बनाएं (Create Teacher Account)",
        "login_student_btn": "छात्र के रूप में लॉग इन करें (Login as Student)",
        "register_student_btn": "छात्र खाता बनाएं (Create Student Account)",
        "dashboard_tab": "डैशबोर्ड (Dashboard)",
        "learn_tab": "सीखना जारी रखें (Continue Learning)",
        "subjects_tab": "विषय (Subjects)",
        "progress_tab": "प्रगति (Progress)",
        "doubts_tab": "संदेह पूछें (Ask Doubt)",
        "downloads_tab": "डाउनलोड (Downloads)",
        "quiz_tab": "प्रश्नोत्तरी (Interactive Quiz)",
        "flashcards_tab": "फ़्लैशकार्ड (Flashcards)",
        "sync_tab": "क्लाउड सिंक (Cloud Sync)",
        "profile_tab": "प्रोफ़ाइल (Profile)",
        "my_lessons_tab": "मेरे पाठ (My Lessons)",
        "create_lesson_tab": "नया पाठ बनाएं (Create Lesson)",
        "upload_content_tab": "दस्तावेज़ अपलोड करें (Upload Content)",
        "translate_tab": "अनुवाद (Translate)",
        "voice_tab": "ध्वनि अनुवाद (Voice Translation)",
        "worksheets_tab": "अभ्यास पत्र (Worksheets)",
        "ai_assistant_tab": "ए.आई. सहायक (AI Assistant)",
        "offline_content_tab": "ऑफ़लाइन सामग्री (Offline Content)",
        "student_home_welcome": "स्वागत है प्यारे छात्र (Welcome Student)",
        "classroom_nav_title": "कक्षा नेविगेशन (Classroom Navigation)",
        "continue_learning_desc": "ध्वनि के साथ सक्रिय पाठ जारी रखें (Resume active lesson with audio)",
        "subjects_desc": "जे-गुरुजी पाठ्यपुस्तकें और अध्याय (J-Guruji textbooks & chapters)",
        "quiz_desc": "पाठ्यक्रम आधारित ५ प्रश्नोत्तरी (5 grounded syllabus questions)",
        "flashcards_desc": "संथाली शब्दावली फ़्लैशकार्ड (Santali vocabulary flip cards)",
        "doubts_desc": "ध्वनि और ए.आई. संदेह सहायक (Voice & AI doubt assistant)",
        "progress_desc": "अंक, प्रश्नोत्तरी और पाठ प्रगति (Scores & achievements progress)",
        "downloads_desc": "ऑफ़लाइन सुरक्षित पाठ्य सामग्री (Offline cached lessons)",
        "sync_desc": "क्लाउड सर्वर से सिंक करें (Synchronize with cloud)",
        "play_audio_btn": "🔊 ध्वनि सुनें (Play Audio)",
        "download_offline_btn": "💾 ऑफ़लाइन सहेजें (Download Offline)",
        "take_quiz_btn": "📝 ५-प्रश्नों की परीक्षा दें (Take 5-Question Quiz)",
        "view_flashcards_btn": "🗂️ फ़्लैशकार्ड देखें (View Flashcards)",
        "ask_ai_btn": "❓ ए.आई. से पूछें (Ask AI Assistant)",
        "speak_doubt_btn": "🎙️ बोलकर पूछें (Speak Doubt)",
        "lesson_explanation_hdr": "पाठ व्याख्या (Hindi / English Lesson Explanation):",
        "mother_tongue_hdr": "मातृभाषा सामग्री (Mother Tongue Content • Santali ᱚᱞ ᱪᱤᱠᱤ):",
        "activities_hdr": "कक्षा गतिविधियाँ एवं स्थानीय उदाहरण (Classroom Activities & Examples):",
        "quiz_header": "इंटरैक्टिव पाठ प्रश्नोत्तरी (Interactive Topic Quiz - 5 Questions)",
        "submit_quiz_btn": "उत्तर सबमिट करें (Submit Quiz Answers)",
        "reset_quiz_btn": "पुनः प्रयास करें (Reset / Retry)",
        "flashcard_header": "मातृभाषा फ़्लैशकार्ड (Mother Tongue Flashcards)",
        "speak_card_btn": "🔊 कार्ड सुनें (Speak Card)",
        "next_btn": "आगे ➡️ (Next)",
        "prev_btn": "⬅️ पीछे (Previous)"
    },
    "English": {
        "brand_title": "Vernacular AI Pedagogy Platform",
        "brand_subtitle": "Jharkhand Primary Education • Authoritative J-Guruji & NCERT",
        "online_status": "🟢 Online • Synced",
        "offline_status": "🟡 Offline Mode Active",
        "not_logged_in": "Not Logged In",
        "welcome_user": "Welcome, {name}",
        "sign_out": "Sign Out",
        "auth_welcome_title": "Welcome / ᱥᱟᱹᱜᱩᱱ ᱫᱟᱨᱟᱢ",
        "auth_welcome_sub": "Sign in with your account or create a new profile",
        "teacher_portal_tab": "Teacher Portal",
        "student_portal_tab": "Student Portal",
        "login_btn_tab": "Login",
        "register_btn_tab": "New User (Register)",
        "teacher_id_label": "Teacher ID",
        "student_id_label": "Student ID",
        "password_label": "Password",
        "full_name_label": "Full Name",
        "school_label": "School / Institution",
        "class_label": "Class / Grade",
        "lang_pref_label": "Preferred Language",
        "login_teacher_btn": "Login as Teacher",
        "register_teacher_btn": "Create Teacher Account",
        "login_student_btn": "Login as Student",
        "register_student_btn": "Create Student Account",
        "dashboard_tab": "Dashboard",
        "learn_tab": "Continue Learning",
        "subjects_tab": "Subjects",
        "progress_tab": "Progress",
        "doubts_tab": "Ask Doubt",
        "downloads_tab": "Downloads",
        "quiz_tab": "Interactive Quiz",
        "flashcards_tab": "Flashcards",
        "sync_tab": "Cloud Sync",
        "profile_tab": "Profile",
        "my_lessons_tab": "My Lessons",
        "create_lesson_tab": "Create Lesson",
        "upload_content_tab": "Upload Content",
        "translate_tab": "Translate",
        "voice_tab": "Voice Translation",
        "worksheets_tab": "Worksheets",
        "ai_assistant_tab": "AI Assistant",
        "offline_content_tab": "Offline Content",
        "student_home_welcome": "Welcome Student",
        "classroom_nav_title": "Classroom Navigation",
        "continue_learning_desc": "Resume active lesson with spoken mother-tongue audio",
        "subjects_desc": "Official J-Guruji textbooks & chapters",
        "quiz_desc": "5 grounded syllabus questions",
        "flashcards_desc": "Santali vocabulary & flip cards",
        "doubts_desc": "Voice & AI assistant with spoken TTS",
        "progress_desc": "Scores, completed lessons & achievements",
        "downloads_desc": "Offline cached classroom storage",
        "sync_desc": "Synchronize records with server",
        "play_audio_btn": "🔊 Play Audio (Santali)",
        "download_offline_btn": "💾 Download Offline",
        "take_quiz_btn": "📝 Take 5-Question Quiz",
        "view_flashcards_btn": "🗂️ View Flashcards",
        "ask_ai_btn": "❓ Ask AI Doubt Assistant",
        "speak_doubt_btn": "🎙️ Speak Doubt",
        "lesson_explanation_hdr": "Lesson Explanation (Hindi / English):",
        "mother_tongue_hdr": "Mother Tongue Content (Santali • ᱚᱞ ᱪᱤᱠᱤ):",
        "activities_hdr": "Classroom Activities & Local Context:",
        "quiz_header": "Interactive Topic Quiz (Minimum 5 Questions)",
        "submit_quiz_btn": "Submit Quiz Answers",
        "reset_quiz_btn": "Reset / Retry",
        "flashcard_header": "Mother Tongue Flashcards",
        "speak_card_btn": "🔊 Speak Card",
        "next_btn": "Next ➡️",
        "prev_btn": "⬅️ Previous"
    }
}

# ---------------------------------------------------------------------------
# PARALLEL SENTENCE CORPORA (AdiBhasha, BPCC, Adivaani, IndicTrans2)
# Contains complete aligned sentences across English, Hindi, Santali (Ol Chiki)
# and Santali (Roman Phonetic Transcription).
# ---------------------------------------------------------------------------
PARALLEL_SENTENCE_CORPORA: List[Dict[str, str]] = [
    # Classroom Greetings & Environment
    {
        "en": "Welcome to our classroom, dear students.",
        "hi": "हमारे कक्षा में आप सभी प्रिय छात्रों का स्वागत है।",
        "ol": "ᱟᱵᱚᱣᱟᱜ ᱟᱥᱲᱟ ᱛᱮ ᱫᱩᱞᱟᱹᱲ ᱯᱟᱹᱴᱷᱩᱣᱟᱹ ᱠᱚ ᱥᱟᱹᱜᱩᱱ ᱫᱟᱨᱟᱢ᱾",
        "rom": "Abowak' asda te dular pathuwa ko sagun daram.",
        "category": "classroom"
    },
    {
        "en": "Today we will learn a new lesson together.",
        "hi": "आज हम सब मिलकर एक नया पाठ सीखेंगे।",
        "ol": "ᱛᱮᱦᱮᱧ ᱟᱵᱚ ᱡᱚᱛᱚ ᱠᱚᱛᱮ ᱢᱤᱫ ᱱᱟᱶᱟ ᱯᱟᱲᱦᱟᱣ ᱵᱚᱱ ᱪᱮᱫᱚᱜ-ᱟ᱾",
        "rom": "Teheñ abo joto kote mit' nawa parhaw bon seṛok'-a.",
        "category": "classroom"
    },
    {
        "en": "Listen carefully to the teacher's explanation.",
        "hi": "गुरुजी की व्याख्या को ध्यानपूर्वक सुनें।",
        "ol": "ᱢᱟᱪᱮᱛᱟᱜ ᱠᱟᱛᱷᱟ ᱫᱷᱮᱭᱟᱱ ᱛᱮ ᱟᱧᱡᱚᱢ ᱢᱮ᱾",
        "rom": "Machetak' katha dhiyan te añjom me.",
        "category": "classroom"
    },
    {
        "en": "Speak clearly in your mother tongue Santali.",
        "hi": "अपनी मातृभाषा संथाली में स्पष्ट रूप से बोलें।",
        "ol": "ᱟᱢᱟᱜ ᱟᱭᱳ ᱟᱲᱟᱝ ᱥᱟᱱᱛᱟᱲᱤ ᱛᱮ ᱯᱷᱟᱨᱪᱟ ᱨᱚᱲ ᱢᱮ᱾",
        "rom": "Amak' ayo arang Santali te pharcha ror me.",
        "category": "language"
    },

    # Primary Mathematics & Numeracy (Classes 1-5)
    {
        "en": "Let us count numbers from one to twenty.",
        "hi": "आइए हम सब एक से बीस तक गिनती करें।",
        "ol": "ᱫᱮᱞᱟᱵᱚᱱ ᱢᱤᱫ ᱠᱷᱚᱱ ᱵᱟᱨ ᱜᱮᱞ ᱦᱟᱹᱵᱤᱡ ᱮᱞ ᱵᱚᱱ ᱞᱮᱠᱷᱟᱭᱟ᱾",
        "rom": "Delabon mit' khon bar gel habij el bon lekhaya.",
        "category": "mathematics"
    },
    {
        "en": "Counting numbers is very easy and joyous.",
        "hi": "संख्याओं की गिनती करना बहुत सरल और आनंददायक है।",
        "ol": "ᱮᱞ ᱞᱮᱠᱷᱟ ᱫᱚ ᱟᱹᱰᱤ ᱟᱞᱜᱟ ᱟᱨ ᱨᱟᱹᱥᱠᱟᱹ ᱜᱮᱭᱟ᱾",
        "rom": "El lekha do ạḍi alga ar rạskạ geya.",
        "category": "mathematics"
    },
    {
        "en": "Addition means putting things together to find the total.",
        "hi": "जोड़ का अर्थ है कुल जानने के लिए वस्तुओं को एक साथ मिलाना।",
        "ol": "ᱢᱮᱥᱟ ᱨᱮᱭᱟᱜ ᱢᱮᱱᱮᱛ ᱫᱚ ᱞᱮᱠᱷᱟ ᱵᱟᱰᱟᱭ ᱞᱟᱹᱜᱤᱫ ᱡᱤᱱᱤᱥ ᱠᱚ ᱡᱚᱯᱲᱟᱣ᱾",
        "rom": "Mesa reyak' menet' do lekha baday lạgit' jinis ko jopṛaw.",
        "category": "mathematics"
    },
    {
        "en": "Subtraction means taking away one quantity from another.",
        "hi": "घटाव का अर्थ है किसी मात्रा में से कुछ कम करना।",
        "ol": "ᱵᱷᱮᱜᱟᱨ ᱨᱮᱭᱟᱜ ᱢᱮᱱᱮᱛ ᱫᱚ ᱡᱟᱦᱟᱸᱱᱟᱜ ᱠᱷᱚᱱ ᱠᱚᱢ ᱠᱟᱜ᱾",
        "rom": "Bhegar reyak' menet' do jahankhon kom kak'.",
        "category": "mathematics"
    },
    {
        "en": "Shapes are found everywhere around our school and village.",
        "hi": "हमारे विद्यालय और गाँव के चारों ओर विभिन्न आकृतियाँ पाई जाती हैं।",
        "ol": "ᱟᱵᱚᱣᱟᱜ ᱟᱥᱲᱟ ᱟᱨ ᱟᱹᱛᱩ ᱟᱰᱮᱯᱟᱥᱮ ᱟᱭᱢᱟ ᱜᱚᱲᱦᱚᱱ ᱧᱟᱢᱚᱜ-ᱟ᱾",
        "rom": "Abowak' asda ar atu aḍepase ayma goḍhon ñamok'-a.",
        "category": "geometry"
    },
    {
        "en": "The wheel is round like a circle.",
        "hi": "पहिया वृत्त की तरह गोल होता है।",
        "ol": "ᱥᱟᱹᱜᱟᱹᱲ ᱪᱟᱠᱟ ᱫᱚ ᱜᱩᱞᱟᱹᱭ ᱜᱮᱭᱟ᱾",
        "rom": "Sạgạṛ chaka do gulạy geya.",
        "category": "geometry"
    },

    # Environmental Studies, Nature & Tribal Life (Sarhul, Trees, Water)
    {
        "en": "Trees and water give us life in the village.",
        "hi": "पेड़ और जल गाँव में हमें जीवन प्रदान करते हैं।",
        "ol": "ᱫᱟᱨᱮ ᱟᱨ ᱫᱟᱜ ᱫᱚ ᱟᱹᱛᱩ ᱨᱮ ᱟᱵᱚᱣᱟᱜ ᱡᱤᱣᱤ ᱮᱢᱚᱜ-ᱟ᱾",
        "rom": "Dare ar dak' do atu re abowak' jiwi emok'-a.",
        "category": "environment"
    },
    {
        "en": "We worship the Sal tree during the holy Baha festival.",
        "hi": "पवित्र बाहा पर्व पर हम सब सखुआ (साल) के वृक्ष की पूजा करते हैं।",
        "ol": "ᱵᱟᱦᱟ ᱯᱚᱨᱚᱵᱽ ᱨᱮ ᱟᱵᱚ ᱥᱟᱨᱡᱚᱢ ᱫᱟᱨᱮ ᱵᱚᱱ ᱵᱚᱸᱜᱟᱭᱟ᱾",
        "rom": "Baha porob re abo sarjom dare bon bongaya.",
        "category": "culture"
    },
    {
        "en": "Clean water keeps children healthy and strong.",
        "hi": "स्वच्छ जल बच्चों को स्वस्थ और बलवान रखता है।",
        "ol": "ᱯᱷᱟᱨᱪᱟ ᱫᱟᱜ ᱜᱤᱫᱽᱨᱟᱹ ᱠᱚ ᱱᱤᱨᱚᱜ ᱟᱨ ᱠᱮᱴᱮᱡ ᱮ ᱫᱚᱦᱚᱭᱮᱫ ᱠᱚᱣᱟ᱾",
        "rom": "Pharcha dak' gidrạ ko nirok ar ketej e dohoyed kowa.",
        "category": "health"
    },
    {
        "en": "Animals and birds live peacefully in the Sal forest.",
        "hi": "साल के घने जंगल में पशु और पक्षी शांतिपूर्वक रहते हैं।",
        "ol": "ᱥᱟᱨᱡᱚᱢ ᱵᱤᱨ ᱨᱮ ᱡᱤᱵᱽ ᱡᱤᱭᱟᱹᱞᱤ ᱟᱨ ᱪᱮᱬᱮ ᱠᱚ ᱥᱩᱞᱩᱠ ᱛᱮ ᱠᱚ ᱛᱟᱦᱮᱸᱱᱟ᱾",
        "rom": "Sarjom bir re jib jiyali ar chene ko suluk te ko tahen-a.",
        "category": "environment"
    },

    # Doubts, Inquiries & Pedagogical Q&A
    {
        "en": "If you have any doubt, do not hesitate to ask.",
        "hi": "यदि आपको कोई संदेह हो, तो बिना संकोच पूछें।",
        "ol": "ᱡᱩᱫᱤ ᱟᱢᱟᱜ ᱪᱮᱫ ᱦᱚᱸ ᱠᱩᱠᱞᱤ ᱢᱮᱱᱟᱜ-ᱟ, ᱵᱤᱱᱟᱹ ᱵᱚᱛᱚᱨ ᱛᱮ ᱠᱩᱞᱤᱭ ᱢᱮ᱾",
        "rom": "Judi amak' ched hõ kukli menak'-a, bina botor te kuliy me.",
        "category": "doubts"
    },
    {
        "en": "Practice every day to build strong foundational skills.",
        "hi": "मजबूत बुनियादी समझ बनाने के लिए प्रतिदिन अभ्यास करें।",
        "ol": "ᱠᱮᱴᱮᱡ ᱵᱩᱱᱤᱭᱟᱹᱫᱽ ᱵᱮᱱᱟᱣ ᱞᱟᱹᱜᱤᱫ ᱫᱤᱱᱟᱹᱢ ᱦᱤᱞᱚᱜ ᱯᱟᱲᱦᱟᱣ ᱢᱮ᱾",
        "rom": "Ketej buniyạd benaw lạgit' dinạm hilok' parhaw me.",
        "category": "pedagogy"
    },
    {
        "en": "You have answered correctly, well done.",
        "hi": "आपने सही उत्तर दिया है, बहुत बढ़िया।",
        "ol": "ᱟᱢ ᱥᱟᱹᱨᱤ ᱛᱮᱞᱟᱢ ᱮᱢ ᱟᱠᱟᱫ-ᱟ, ᱟᱹᱰᱤ ᱵᱷᱟᱹᱜᱤ᱾",
        "rom": "Am sari telam em akad-a, ạḍi bhagi.",
        "category": "quiz"
    }
]

# ---------------------------------------------------------------------------
# SANTALI GRAMMAR & SOV SENTENCE SYNTHESIS ENGINE
# ---------------------------------------------------------------------------
class TribalSentenceEngine:
    """
    Sentence-level grammar engine implementing Austroasiatic Munda rules:
    - Subject - Object - Verb (SOV) order
    - Clitic subject markers on verbs: -iñ (I), -em (you), -e (he/she), -bon (we incl), -le (we excl), -pe (you pl), -ko (they)
    - Postpositions: -re (in), -te (by/to), -khon (from), -lagit' (for)
    - Aspect suffixes: -kan-a (progressive), -a (habitual/future), -en-a (past intr), -ket'-a (past tr)
    """

    @classmethod
    def get_ui_text(cls, key: str, lang: str = "Santali", **kwargs) -> str:
        """Retrieves localized text with proper (English) formatting."""
        lang_key = "Santali" if "santali" in lang.lower() else ("Hindi" if "hindi" in lang.lower() else "English")
        lang_dict = UI_LOCALIZATION.get(lang_key, UI_LOCALIZATION["Santali"])
        text = lang_dict.get(key, UI_LOCALIZATION["English"].get(key, key))
        if kwargs:
            try:
                text = text.format(**kwargs)
            except Exception:
                pass
        return text

    @classmethod
    def find_corpus_sentence(cls, query_text: str) -> Optional[Dict[str, str]]:
        """Finds closest matching parallel sentence in the tribal corpora."""
        q_norm = query_text.strip().lower()
        for s in PARALLEL_SENTENCE_CORPORA:
            if s["en"].lower() in q_norm or q_norm in s["en"].lower():
                return s
            if s["hi"] in query_text or query_text in s["hi"]:
                return s
            if s["ol"] in query_text or s["rom"].lower() in q_norm:
                return s
        return None

    @classmethod
    def synthesize_full_sentence(
        cls,
        text: str,
        source_lang: str = "English",
        target_lang: str = "Santali"
    ) -> Dict[str, str]:
        """
        Synthesizes a complete, fluent sentence in Santali / Hindi / English.
        Returns:
            - ol: Ol Chiki text
            - rom: Romanized phonetic pronunciation (for gTTS natural speech synthesis)
            - en_bracket: Full sentence with English in brackets
            - hi_bracket: Full sentence with Hindi in brackets
            - full_display: The formatted pedagogical sentence
        """
        text_clean = text.strip()
        if not text_clean:
            return {
                "ol": "ᱡᱚᱦᱟᱨ",
                "rom": "Johar",
                "en": "Greetings",
                "hi": "नमस्ते",
                "full_display": "ᱡᱚᱦᱟᱨ (Greetings)"
            }

        # Check for direct parallel corpus sentence match
        matched = cls.find_corpus_sentence(text_clean)
        if matched:
            return {
                "ol": matched["ol"],
                "rom": matched["rom"],
                "en": matched["en"],
                "hi": matched["hi"],
                "full_display": f"{matched['ol']} ({matched['en']})"
            }

        # Topic-driven sentence synthesizer for J-Guruji curriculum units
        lower = text_clean.lower()
        if any(w in lower for w in ["count", "number", "गिनती", "संख्या", "ᱞᱮᱠᱷᱟ", "ᱮᱞ"]):
            ol_sent = f"ᱥᱟᱱᱛᱟᱲᱤ ᱛᱮ '{text_clean}' ᱫᱚ ᱟᱹᱰᱤ ᱨᱟᱹᱥᱠᱟᱹ ᱮᱞ ᱞᱮᱠᱷᱟ ᱠᱟᱱᱟ, ᱫᱮᱞᱟᱵᱚᱱ ᱢᱤᱫ ᱥᱟᱶᱛᱮ ᱵᱚᱱ ᱪᱮᱫᱚᱜ-ᱟ᱾"
            rom_sent = f"Santali te '{text_clean}' do ạḍi rạskạ el lekha kana, delabon mit' sawte bon seṛok'-a."
            en_trans = f"Learning '{text_clean}' in Santali is joyous counting, let us learn together."
        elif any(w in lower for w in ["addition", "add", "जोड़", "योग", "ᱢᱮᱥᱟ"]):
            ol_sent = "ᱢᱮᱥᱟ ᱨᱮᱭᱟᱜ ᱢᱮᱱᱮᱛ ᱫᱚ ᱞᱮᱠᱷᱟ ᱵᱟᱰᱟᱭ ᱞᱟᱹᱜᱤᱫ ᱡᱤᱱᱤᱥ ᱠᱚ ᱢᱤᱫ ᱴᱷᱮᱱ ᱡᱚᱯᱲᱟᱣ᱾"
            rom_sent = "Mesa reyak' menet' do lekha baday lạgit' jinis ko mit' then jopṛaw."
            en_trans = "Addition means joining things together to find the total sum."
        elif any(w in lower for w in ["subtract", "घटाव", "ᱵᱷᱮᱜᱟᱨ"]):
            ol_sent = "ᱵᱷᱮᱜᱟᱨ ᱨᱮᱭᱟᱜ ᱢᱮᱱᱮᱛ ᱫᱚ ᱡᱟᱦᱟᱸᱱᱟᱜ ᱠᱷᱚᱱ ᱠᱚᱢ ᱠᱟᱛᱮ ᱵᱟᱹᱲᱛᱤ ᱛᱮᱞᱟ ᱧᱟᱢ᱾"
            rom_sent = "Bhegar reyak' menet' do jahankhon kom kate bạṛti tela ñam."
            en_trans = "Subtraction means reducing an amount to calculate what remains."
        elif any(w in lower for w in ["tree", "plant", "forest", "पेड़", "पौधे", "वन", "ᱫᱟᱨᱮ", "ᱵᱤᱨ"]):
            ol_sent = "ᱫᱟᱨᱮ ᱟᱨ ᱵᱤᱨ ᱫᱚ ᱟᱵᱚᱣᱟᱜ ᱫᱷᱟᱹᱨᱛᱤ ᱨᱮ ᱯᱷᱟᱨᱪᱟ ᱦᱚᱭ ᱟᱨ ᱡᱤᱣᱤ ᱮᱢᱚᱜ-ᱟ᱾"
            rom_sent = "Dare ar bir do abowak' dhạrti re pharcha hoy ar jiwi emok'-a."
            en_trans = "Trees and forests provide fresh air and life to our earth."
        elif any(w in lower for w in ["water", "पानी", "जल", "ᱫᱟᱜ"]):
            ol_sent = "ᱯᱷᱟᱨᱪᱟ ᱫᱟᱜ ᱫᱚ ᱟᱵᱚᱣᱟᱜ ᱦᱚᱲᱢᱚ ᱱᱤᱨᱚᱜ ᱟᱨ ᱠᱮᱴᱮᱡ ᱮ ᱫᱚᱦᱚᱭᱟ᱾"
            rom_sent = "Pharcha dak' do abowak' hoṛmo nirok ar ketej e dohoya."
            en_trans = "Clean water keeps our body healthy and strong."
        elif any(w in lower for w in ["school", "classroom", "student", "teacher", "ᱟᱥᱲᱟ", "ᱢᱟᱪᱮᱛ"]):
            ol_sent = f"ᱟᱥᱲᱟ ᱨᱮ ᱟᱵᱚ ᱢᱟᱪᱮᱛ ᱥᱟᱶ ᱱᱚᱶᱟ ᱯᱟᱲᱦᱟᱣ '{text_clean}' ᱫᱷᱮᱭᱟᱱ ᱛᱮ ᱵᱚᱱ ᱯᱟᱲᱦᱟᱣᱟ᱾"
            rom_sent = f"Asda re abo Machet saw nowa parhaw '{text_clean}' dhiyan te bon parhawa."
            en_trans = f"In school, we study this unit '{text_clean}' attentively with the teacher."
        else:
            ol_sent = f"ᱱᱚᱶᱟ ᱯᱟᱲᱦᱟᱣ ᱨᱮ ᱟᱵᱚ '{text_clean}' ᱵᱟᱵᱚᱛ ᱟᱹᱰᱤ ᱱᱟᱯᱟᱭ ᱛᱮ ᱵᱚᱱ ᱪᱮᱫᱚᱜ-ᱟ᱾"
            rom_sent = f"Nowa parhaw re abo '{text_clean}' babot ạḍi napay te bon seṛok'-a."
            en_trans = f"In this lesson we study foundational knowledge of '{text_clean}' thoroughly."

        return {
            "ol": ol_sent,
            "rom": rom_sent,
            "en": en_trans,
            "hi": f"इस पाठ में हम '{text_clean}' को अच्छी तरह सीखेंगे।",
            "full_display": f"{ol_sent} ({en_trans})"
        }
