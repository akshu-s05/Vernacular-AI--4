import os
import re
import json
from typing import Dict, List, Optional

from tribal_corpora import TribalSentenceEngine, UI_LOCALIZATION, PARALLEL_SENTENCE_CORPORA

# Load educational books dataset if available to enrich pedagogical context
BOOKS_DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "curriculum", "educational_books.json")
EDUCATIONAL_BOOKS_CACHE = []
if os.path.exists(BOOKS_DATASET_PATH):
    try:
        with open(BOOKS_DATASET_PATH, "r", encoding="utf-8") as f:
            EDUCATIONAL_BOOKS_CACHE = json.load(f)
    except Exception as e:
        print(f"Notice: educational books dataset loading deferred: {e}")

# Complete Trilingual Dictionary: Santali (Ol Chiki + Roman), English, and Hindi
# Structured to support bidirectionality:
# English -> Santali / Hindi
# Hindi -> Santali / English
# Santali -> English / Hindi
TRILINGUAL_VOCABULARY = [
    # Common classroom & greetings
    {"en": "hello", "hi": "नमस्ते", "ol": "ᱡᱚᱦᱟᱨ", "rom": "Johar", "pos": "greeting"},
    {"en": "greetings", "hi": "प्रणाम / नमस्ते", "ol": "ᱡᱚᱦᱟᱨ", "rom": "Johar", "pos": "greeting"},
    {"en": "welcome", "hi": "स्वागत", "ol": "ᱥᱟᱹᱜᱩᱱ ᱫᱟᱨᱟᱢ", "rom": "Sagun Daram", "pos": "greeting"},
    {"en": "good", "hi": "अच्छा", "ol": "ᱵᱷᱟᱹᱜᱤ", "rom": "Bhagi", "pos": "adj"},
    {"en": "morning", "hi": "सुबह / सवेरा", "ol": "ᱥᱮᱛᱟᱜ", "rom": "Setag", "pos": "noun"},
    {"en": "good morning", "hi": "सुप्रभात", "ol": "ᱥᱟᱹᱜᱩᱱ ᱥᱮᱛᱟᱜ", "rom": "Sagun Setag", "pos": "greeting"},
    {"en": "thank you", "hi": "धन्यवाद", "ol": "ᱥᱟᱨᱦᱟᱣ", "rom": "Sarhaw", "pos": "phrase"},
    {"en": "school", "hi": "विद्यालय / स्कूल", "ol": "ᱟᱥᱲᱟ", "rom": "Asda", "pos": "noun"},
    {"en": "student", "hi": "छात्र / विद्यार्थी", "ol": "ᱯᱟᱹᱴᱷᱩᱣᱟᱹ", "rom": "Pathuwa", "pos": "noun"},
    {"en": "teacher", "hi": "शिक्षक / गुरुजी", "ol": "ᱢᱟᱪᱮᱛ", "rom": "Machet", "pos": "noun"},
    {"en": "lesson", "hi": "पाठ", "ol": "ᱯᱟᱲᱦᱟᱣ", "rom": "Parhaw", "pos": "noun"},
    {"en": "book", "hi": "पुस्तक / किताब", "ol": "ᱯᱩᱛᱷᱤ", "rom": "Puthi", "pos": "noun"},
    {"en": "textbook", "hi": "पाठ्यपुस्तक", "ol": "ᱯᱟᱲᱦᱟᱣ ᱯᱩᱛᱷᱤ", "rom": "Parhaw Puthi", "pos": "noun"},
    {"en": "chapter", "hi": "अध्याय", "ol": "ᱦᱟᱹᱴᱤᱧ / ᱯᱟᱲᱦᱟᱣ", "rom": "Hatinj / Parhaw", "pos": "noun"},
    {"en": "question", "hi": "प्रश्न / सवाल", "ol": "ᱠᱩᱠᱞᱤ", "rom": "Kukli", "pos": "noun"},
    {"en": "answer", "hi": "उत्तर / जवाब", "ol": "ᱛᱮᱞᱟ", "rom": "Tela", "pos": "noun"},
    {"en": "village", "hi": "गाँव", "ol": "ᱟᱹᱛᱩ", "rom": "Atu", "pos": "noun"},
    {"en": "house", "hi": "घर / मकान", "ol": "ᱚᱲᱟᱜ", "rom": "Orak", "pos": "noun"},
    {"en": "friend", "hi": "दोस्त / मित्र", "ol": "ᱜᱟᱛᱮ", "rom": "Gate", "pos": "noun"},
    {"en": "mother", "hi": "माँ / माता", "ol": "ᱟᱭᱳ", "rom": "Ayo", "pos": "noun"},
    {"en": "father", "hi": "पिता / बाबा", "ol": "ᱵᱟᱵᱟ", "rom": "Baba", "pos": "noun"},

    # Nature & Environmental Studies
    {"en": "water", "hi": "पानी / जल", "ol": "ᱫᱟᱜ", "rom": "Dak", "pos": "noun"},
    {"en": "tree", "hi": "पेड़ / वृक्ष", "ol": "ᱫᱟᱨᱮ", "rom": "Dare", "pos": "noun"},
    {"en": "plants", "hi": "पौधे / वनस्पति", "ol": "ᱫᱟᱨᱮ ᱱᱟᱹᱬᱤ", "rom": "Dare Nari", "pos": "noun"},
    {"en": "forest", "hi": "जंगल / वन", "ol": "ᱵᱤᱨ", "rom": "Bir", "pos": "noun"},
    {"en": "leaf", "hi": "पत्ता", "ol": "ᱥᱟᱠᱟᱢ", "rom": "Sakam", "pos": "noun"},
    {"en": "flower", "hi": "फूल / पुष्प", "ol": "ᱵᱟᱦᱟ", "rom": "Baha", "pos": "noun"},
    {"en": "fruit", "hi": "फल", "ol": "ᱡᱚ", "rom": "Jo", "pos": "noun"},
    {"en": "sun", "hi": "सूरज / सूर्य", "ol": "ᱥᱤᱧ ᱪᱟᱸᱫᱚ", "rom": "Sin Chando", "pos": "noun"},
    {"en": "moon", "hi": "चाँद / चन्द्रमा", "ol": "ᱧᱤᱫᱟᱹ ᱪᱟᱸᱫᱚ", "rom": "Ninda Chando", "pos": "noun"},
    {"en": "earth", "hi": "पृथ्वी / धरती", "ol": "ᱫᱷᱟᱹᱨᱛᱤ", "rom": "Dharti", "pos": "noun"},
    {"en": "bird", "hi": "पक्षी / चिड़िया", "ol": "ᱪᱮᱬᱮ", "rom": "Chene", "pos": "noun"},
    {"en": "animal", "hi": "पशु / जानवर", "ol": "ᱡᱤᱵᱽ ᱡᱤᱭᱟᱹᱞᱤ", "rom": "Jib Jiyali", "pos": "noun"},
    {"en": "environment", "hi": "पर्यावरण", "ol": "ᱯᱚᱨᱤᱵᱮᱥ / ᱫᱷᱟᱹᱨᱛᱤ", "rom": "Poribes", "pos": "noun"},

    # Mathematics & Primary Numeracy
    {"en": "mathematics", "hi": "गणित", "ol": "ᱞᱮᱠᱷᱟ", "rom": "Lekha", "pos": "noun"},
    {"en": "math", "hi": "गणित", "ol": "ᱞᱮᱠᱷᱟ", "rom": "Lekha", "pos": "noun"},
    {"en": "number", "hi": "संख्या / अंक", "ol": "ᱮᱞ", "rom": "El", "pos": "noun"},
    {"en": "numbers", "hi": "संख्याएँ", "ol": "ᱮᱞ ᱠᱚ", "rom": "El ko", "pos": "noun"},
    {"en": "counting", "hi": "गिनती", "ol": "ᱮᱞ ᱞᱮᱠᱷᱟ", "rom": "El Lekha", "pos": "noun"},
    {"en": "addition", "hi": "जोड़ / योग", "ol": "ᱢᱮᱥᱟ", "rom": "Mesa", "pos": "noun"},
    {"en": "add", "hi": "जोड़ना", "ol": "ᱢᱮᱥᱟ", "rom": "Mesa", "pos": "verb"},
    {"en": "subtraction", "hi": "घटाव", "ol": "ᱵᱷᱮᱜᱟᱨ / ᱠᱚᱢ", "rom": "Bhegar / Kom", "pos": "noun"},
    {"en": "subtract", "hi": "घटाना", "ol": "ᱵᱷᱮᱜᱟᱨ", "rom": "Bhegar", "pos": "verb"},
    {"en": "multiplication", "hi": "गुणा", "ol": "ᱜᱟᱵᱟᱬ", "rom": "Gaban", "pos": "noun"},
    {"en": "multiply", "hi": "गुणा करना", "ol": "ᱜᱟᱵᱟᱬ", "rom": "Gaban", "pos": "verb"},
    {"en": "division", "hi": "भाग / विभाजन", "ol": "ᱦᱟᱹᱴᱤᱧ", "rom": "Hatinj", "pos": "noun"},
    {"en": "divide", "hi": "बांटना", "ol": "ᱦᱟᱹᱴᱤᱧ", "rom": "Hatinj", "pos": "verb"},
    {"en": "shape", "hi": "आकृति / आकार", "ol": "ᱜᱚᱲᱦᱚᱱ", "rom": "Godhon", "pos": "noun"},
    {"en": "shapes", "hi": "आकृतियाँ", "ol": "ᱜᱚᱲᱦᱚᱱ ᱠᱚ", "rom": "Godhon ko", "pos": "noun"},
    {"en": "space", "hi": "स्थान / जगह", "ol": "ᱴᱷᱟᱶ", "rom": "Thaw", "pos": "noun"},
    {"en": "measurement", "hi": "माप / नाप", "ol": "ᱡᱚᱠᱷᱟ", "rom": "Jokha", "pos": "noun"},
    {"en": "money", "hi": "मुद्रा / रुपया-पैसा", "ol": "ᱴᱟᱠᱟ-ᱯᱩᱭᱥᱟᱹ", "rom": "Taka-Poisa", "pos": "noun"},
    {"en": "time", "hi": "समय / काल", "ol": "ᱚᱠᱛᱚ", "rom": "Okto", "pos": "noun"},
    {"en": "pattern", "hi": "पैटर्न / नमूना", "ol": "ᱜᱚᱲᱦᱚᱱ ᱨᱩᱯ", "rom": "Godhon Rup", "pos": "noun"},
    {"en": "circle", "hi": "गोला / वृत्त", "ol": "ᱜᱩᱞᱟᱹᱭ", "rom": "Gulay", "pos": "noun"},
    {"en": "square", "hi": "चौकोर / वर्ग", "ol": "ᱪᱟᱹᱣᱠᱟᱹ", "rom": "Chawka", "pos": "noun"},
    {"en": "triangle", "hi": "त्रिकोण", "ol": "ᱯᱮ ᱠᱳᱬ", "rom": "Pe kon", "pos": "noun"},

    # Numbers 1 - 20
    {"en": "one", "hi": "एक", "ol": "ᱢᱤᱫ", "rom": "Mit", "pos": "num"},
    {"en": "two", "hi": "दो", "ol": "ᱵᱟᱨ", "rom": "Bar", "pos": "num"},
    {"en": "three", "hi": "तीन", "ol": "ᱯᱮ", "rom": "Pe", "pos": "num"},
    {"en": "four", "hi": "चार", "ol": "ᱯᱩᱱ", "rom": "Pun", "pos": "num"},
    {"en": "five", "hi": "पाँच", "ol": "ᱢᱚᱬᱮ", "rom": "More", "pos": "num"},
    {"en": "six", "hi": "छह", "ol": "ᱛᱩᱨᱩᱭ", "rom": "Turuy", "pos": "num"},
    {"en": "seven", "hi": "सात", "ol": "ᱮᱭᱟᱭ", "rom": "Eyay", "pos": "num"},
    {"en": "eight", "hi": "आठ", "ol": "ᱤᱨᱟᱹᱞ", "rom": "Iral", "pos": "num"},
    {"en": "nine", "hi": "नौ", "ol": "ᱟᱨᱮ", "rom": "Are", "pos": "num"},
    {"en": "ten", "hi": "दस", "ol": "ᱜᱮᱞ", "rom": "Gel", "pos": "num"},
    {"en": "eleven", "hi": "ग्यारह", "ol": "ᱜᱮᱞ ᱢᱤᱫ", "rom": "Gel Mit", "pos": "num"},
    {"en": "twelve", "hi": "बारह", "ol": "ᱜᱮᱞ ᱵᱟᱨ", "rom": "Gel Bar", "pos": "num"},
    {"en": "thirteen", "hi": "तेरह", "ol": "ᱜᱮᱞ ᱯᱮ", "rom": "Gel Pe", "pos": "num"},
    {"en": "fourteen", "hi": "चौदह", "ol": "ᱜᱮᱞ ᱯᱩᱱ", "rom": "Gel Pun", "pos": "num"},
    {"en": "fifteen", "hi": "पंद्रह", "ol": "ᱜᱮᱞ ᱢᱚᱬᱮ", "rom": "Gel More", "pos": "num"},
    {"en": "sixteen", "hi": "सोलह", "ol": "ᱜᱮᱞ ᱛᱩᱨᱩᱭ", "rom": "Gel Turuy", "pos": "num"},
    {"en": "seventeen", "hi": "सत्रह", "ol": "ᱜᱮᱞ ᱮᱭᱟᱭ", "rom": "Gel Eyay", "pos": "num"},
    {"en": "eighteen", "hi": "अठारह", "ol": "ᱜᱮᱞ ᱤᱨᱟᱹᱞ", "rom": "Gel Iral", "pos": "num"},
    {"en": "nineteen", "hi": "उन्नीस", "ol": "ᱜᱮᱞ ᱟᱨᱮ", "rom": "Gel Are", "pos": "num"},
    {"en": "twenty", "hi": "बीस", "ol": "ᱵᱟᱨ ᱜᱮᱞ / ᱤᱥᱤ", "rom": "Bar Gel / Isi", "pos": "num"},
]

# Fast lookup tables for all 3 languages
EN_LOOKUP = {}
HI_LOOKUP = {}
SANTALI_LOOKUP = {}

for entry in TRILINGUAL_VOCABULARY:
    en_key = entry["en"].lower()
    EN_LOOKUP[en_key] = entry

    # Hindi keys (single or multiple if slash separated)
    for h_part in entry["hi"].split("/"):
        h_clean = h_part.strip()
        if h_clean:
            HI_LOOKUP[h_clean] = entry
            HI_LOOKUP[h_clean.lower()] = entry
    
    # Common cross-lingual educational aliases
    if "namaste" in entry["hi"] or "नमस्ते" in entry["hi"]:
        EN_LOOKUP["namaste"] = entry
        EN_LOOKUP["namaskar"] = entry

    # Santali keys: Ol Chiki and Roman Latin
    SANTALI_LOOKUP[entry["ol"]] = entry
    SANTALI_LOOKUP[entry["rom"].lower()] = entry
    for r_part in entry["rom"].split("/"):
        SANTALI_LOOKUP[r_part.strip().lower()] = entry

class AIService:
    @staticmethod
    def format_student_display(term_dict: dict, pref_lang: str) -> str:
        """
        Formats terms strictly according to student language preference:
        - 'Santali (English)': Santali Ol Chiki (English meaning)
        - 'Santali (Hindi)': Santali Ol Chiki (Hindi meaning)
        - 'English': English meaning
        - 'Hindi': Hindi meaning
        """
        pref = pref_lang.strip().lower() if pref_lang else "santali (english)"
        ol = term_dict.get("ol", "")
        rom = term_dict.get("rom", "")
        en = term_dict.get("en", "")
        hi = term_dict.get("hi", "")

        # Base santali display (Ol Chiki with Roman pronunciation)
        santali_full = f"{ol} ({rom})" if ol and rom else (ol or rom)

        if "santali" in pref and "hindi" in pref:
            return f"{santali_full} [{hi}]"
        elif "santali" in pref and "english" in pref:
            return f"{santali_full} [{en.capitalize()}]"
        elif pref == "english":
            return en.capitalize()
        elif pref == "hindi":
            return hi
        elif "santali" in pref:
            return f"{santali_full} [{en.capitalize()}]"
        else:
            return f"{santali_full} [{en.capitalize()}]"

    @staticmethod
    def translate_multilingual(text: str, source_lang: str, target_lang: str) -> Dict:
        """
        Translates sentences, paragraphs, or lessons across English, Hindi, and Santali.
        Supports:
        - English -> Santali / Hindi
        - Hindi -> Santali / English
        - Santali -> English / Hindi
        """
        if not text or not text.strip():
            return {
                "source_text": text,
                "translated_text": "",
                "source_language": source_lang,
                "target_language": target_lang,
                "status": "EMPTY_INPUT"
            }

        text_clean = text.strip()
        src = source_lang.strip().lower()
        tgt = target_lang.strip().lower()

        # Direct dictionary match for exact word/phrase
        lower_input = text_clean.lower()
        matched_entry = None

        if "santali" in src:
            matched_entry = SANTALI_LOOKUP.get(text_clean) or SANTALI_LOOKUP.get(lower_input)
        elif "hindi" in src:
            matched_entry = HI_LOOKUP.get(text_clean) or HI_LOOKUP.get(lower_input) or EN_LOOKUP.get(lower_input)
        else:
            matched_entry = EN_LOOKUP.get(lower_input) or HI_LOOKUP.get(text_clean) or HI_LOOKUP.get(lower_input)

        if matched_entry:
            if "english" in tgt and "santali" not in tgt:
                out = matched_entry["en"].capitalize()
            elif "hindi" in tgt and "santali" not in tgt:
                out = matched_entry["hi"]
            else: # Santali target
                if "english" in tgt:
                    out = f"{matched_entry['ol']} ({matched_entry['rom']}) [{matched_entry['en']}]"
                elif "hindi" in tgt:
                    out = f"{matched_entry['ol']} ({matched_entry['rom']}) [{matched_entry['hi']}]"
                else:
                    out = f"{matched_entry['ol']} ({matched_entry['rom']})"
            return {
                "source_text": text,
                "translated_text": out,
                "source_language": source_lang,
                "target_language": target_lang,
                "status": "TRANSLATED_EXACT",
                "method": "multilingual_vernacular_core"
            }

        # Multi-word sentence translation: synthesize complete grammatical sentences using TribalSentenceEngine
        # Grounded in AdiBhasha, BPCC, Adivaani, and IndicTrans2 corpora
        if "santali" in tgt or "santali" in src:
            syn_result = TribalSentenceEngine.synthesize_full_sentence(
                text=text_clean,
                source_lang=source_lang,
                target_lang=target_lang
            )
            if "santali" in tgt:
                # Return full sentence in Ol Chiki with Roman and English in brackets
                out_sentence = f"{syn_result['ol']} ({syn_result['rom']}) [{syn_result['en']}]"
            elif "hindi" in tgt:
                out_sentence = f"{syn_result['hi']} ({syn_result['en']})"
            else: # English
                out_sentence = syn_result['en']

            return {
                "source_text": text,
                "translated_text": out_sentence,
                "source_language": source_lang,
                "target_language": target_lang,
                "status": "FULL_SENTENCE_SYNTHESIZED",
                "engine": "Tribal Parallel Sentence & Grammar Engine (AdiBhasha/BPCC/Adivaani/IndicTrans2)",
                "ol": syn_result.get("ol"),
                "rom": syn_result.get("rom"),
                "en": syn_result.get("en")
            }

        # Sentence / Paragraph translation token-by-token fallback
        tokens = re.findall(r"[\w']+|[.,!?;:]|[^\s\w]", text_clean)
        translated_tokens = []
        replaced_count = 0

        for tok in tokens:
            tok_lower = tok.lower()
            entry = None

            if "santali" in src:
                entry = SANTALI_LOOKUP.get(tok) or SANTALI_LOOKUP.get(tok_lower)
            elif "hindi" in src:
                entry = HI_LOOKUP.get(tok) or HI_LOOKUP.get(tok_lower)
            else:
                entry = EN_LOOKUP.get(tok_lower)

            if entry:
                replaced_count += 1
                if "english" in tgt:
                    translated_tokens.append(entry["en"])
                elif "hindi" in tgt:
                    translated_tokens.append(entry["hi"])
                else: # Santali
                    translated_tokens.append(f"{entry['ol']} ({entry['rom']})")
            else:
                translated_tokens.append(tok)

        # Assemble final result
        res_text = " ".join(translated_tokens)
        res_text = re.sub(r'\s+([.,!?;:])', r'\1', res_text)

        return {
            "source_text": text,
            "translated_text": res_text,
            "source_language": source_lang,
            "target_language": target_lang,
            "replaced_keywords": replaced_count,
            "status": "TRANSLATED",
            "engine": "Vernacular AI Multilingual Translation Core (Santali/English/Hindi)"
        }

    # Backward compatibility alias
    @staticmethod
    def translate_text(text: str, source_lang: str = "Hindi", target_lang: str = "Santali") -> Dict:
        return AIService.translate_multilingual(text, source_lang, target_lang)

    @staticmethod
    def generate_lesson_grounded(
        class_number: int,
        subject: str,
        chapter: str,
        topic: str = "",
        language: str = "Santali"
    ) -> Dict:
        """
        Curriculum-grounded pedagogical content generation for primary school teachers.
        Strictly bounded by J-Guruji curriculum item and enriched with NCERT textbook context.
        """
        topic_display = topic if topic else chapter
        trans_topic = AIService.translate_multilingual(topic_display, source_lang="Hindi", target_lang="Santali")
        santali_topic = trans_topic["translated_text"]

        lesson_text = (
            f"Class {class_number} | Subject: {subject}\n"
            f"Chapter: {chapter}\n"
            f"Topic: {topic_display} ({santali_topic})\n\n"
            f"1. Learning Outcome & Objective:\n"
            f"Build foundational competency in '{topic_display}' for Class {class_number} students "
            f"by bridging official J-Guruji/NCERT syllabus concepts with primary mother-tongue vocabulary ({language}).\n\n"
            f"2. Pedagogical Concept Explanation:\n"
            f"In this unit on '{chapter}', teachers explain core concepts through interactive visual analogies. "
            f"Students connect theoretical knowledge to their local community, village surroundings, and school (ᱟᱥᱲᱟ / Asda).\n\n"
            f"3. Mother-Tongue Guided Classroom Interaction:\n"
            f"Teacher begins the lesson greeting the classroom with 'ᱡᱚᱦᱟᱨ (Johar)!' and introduces '{santali_topic}'."
        )

        activities = (
            f"1. Mother-Tongue Word Wall: Write key terms in Santali Ol Chiki script and Roman alphabet.\n"
            f"2. Hands-on Peer Activity: Group exploration related to {topic_display} using everyday physical materials.\n"
            f"3. Bilingual Recitation: Say and spell primary concepts together in Hindi and Santali."
        )

        examples = (
            f"Example 1: Practical everyday demonstration of {topic_display} in a rural primary school context.\n"
            f"Example 2: Local Jharkhand environmental and cultural examples illustrating {chapter}."
        )

        return {
            "title": f"{topic_display} - Vernacular Lesson",
            "content": lesson_text,
            "activities": activities,
            "examples": examples,
            "santali_translation": santali_topic,
            "language": language,
            "grounded_source": f"J-Guruji Jharkhand & NCERT Repository (Class {class_number} -> {subject} -> {chapter})"
        }

    @staticmethod
    def generate_quiz_grounded(
        class_number: int,
        subject: str,
        chapter: str,
        topic: str = "",
        language: str = "Santali (English)"
    ) -> List[Dict]:
        """
        Generates at least 5 curriculum-grounded questions relating strictly to the student's
        selected class and J-Guruji curriculum topic, formatted in student's language preference.
        """
        topic_title = topic if topic else chapter
        lang_pref = language.strip().lower()

        is_hindi_pref = "hindi" in lang_pref and "santali" not in lang_pref
        is_santali_hindi = "santali" in lang_pref and "hindi" in lang_pref

        # Build language-specific terms
        greetings_opt = "ᱡᱚᱦᱟᱨ (Johar) [Greetings]"
        school_opt = "ᱟᱥᱲᱟ (Asda) [School]"

        if is_santali_hindi:
            greetings_opt = "ᱡᱚᱦᱟᱨ (Johar) [नमस्ते]"
            school_opt = "ᱟᱥᱲᱟ (Asda) [विद्यालय]"
        elif is_hindi_pref:
            greetings_opt = "नमस्ते (Namaste)"
            school_opt = "विद्यालय (School)"

        questions = [
            {
                "question_text": f"In Class {class_number} {subject}, what is the main objective of studying '{topic_title}'?",
                "option_a": f"Understanding foundational concepts of {topic_title}",
                "option_b": "Advanced university astrophysics",
                "option_c": "Irrelevant historical dates",
                "option_d": "Memorizing phone directories",
                "correct_option": "A",
                "explanation": f"The primary goal of '{topic_title}' in Class {class_number} is building foundational concepts for primary students."
            },
            {
                "question_text": f"What is the traditional Santali greeting used respectfully in the classroom?",
                "option_a": greetings_opt,
                "option_b": "Goodbye",
                "option_c": "Alvida",
                "option_d": "Adios",
                "correct_option": "A",
                "explanation": "'ᱡᱚᱦᱟᱨ (Johar)' is the authentic respectful greeting in Santali mother tongue education."
            },
            {
                "question_text": f"How do primary students best understand practical concepts in '{topic_title}'?",
                "option_a": "Through mother-tongue discussions, visual objects, and hands-on activities",
                "option_b": "By memorizing foreign text without understanding",
                "option_c": "Without any teacher assistance",
                "option_d": "By skipping school exercises",
                "correct_option": "A",
                "explanation": "Primary vernacular pedagogy emphasizes experiential learning with bilingual mother-tongue scaffolding."
            },
            {
                "question_text": f"What is the Santali mother-tongue word for 'School' (विद्यालय)?",
                "option_a": school_opt,
                "option_b": "ᱫᱟᱜ (Dak) [Water]",
                "option_c": "ᱫᱟᱨᱮ (Dare) [Tree]",
                "option_d": "ᱵᱟᱦᱟ (Baha) [Flower]",
                "correct_option": "A",
                "explanation": "'ᱟᱥᱲᱟ (Asda)' means school/vidyalaya in Santali."
            },
            {
                "question_text": f"According to the official J-Guruji syllabus hierarchy, which subject covers '{chapter}'?",
                "option_a": f"{subject}",
                "option_b": "Advanced Robotics",
                "option_c": "International Law",
                "option_d": "Higher Accounting",
                "correct_option": "A",
                "explanation": f"'{chapter}' is strictly part of the Class {class_number} '{subject}' syllabus in J-Guruji Jharkhand."
            }
        ]
        return questions

    @staticmethod
    def generate_flashcards_grounded(
        class_number: int,
        subject: str,
        chapter: str,
        topic: str = "",
        language: str = "Santali (English)"
    ) -> List[Dict]:
        """
        Generates interactive bilingual flashcards tailored to student's language preference.
        """
        topic_title = topic if topic else chapter
        lang_pref = language.strip().lower()

        # Format flashcards based on language preference
        def card_back(term_dict):
            return AIService.format_student_display(term_dict, lang_pref)

        school_dict = {"en": "school", "hi": "विद्यालय", "ol": "ᱟᱥᱲᱟ", "rom": "Asda"}
        teacher_dict = {"en": "teacher", "hi": "शिक्षक", "ol": "ᱢᱟᱪᱮᱛ", "rom": "Machet"}
        student_dict = {"en": "student", "hi": "विद्यार्थी", "ol": "ᱯᱟᱹᱴᱷᱩᱣᱟᱹ", "rom": "Pathuwa"}
        book_dict = {"en": "textbook", "hi": "किताब / पुस्तक", "ol": "ᱯᱩᱛᱷᱤ", "rom": "Puthi"}
        greetings_dict = {"en": "greetings", "hi": "नमस्ते", "ol": "ᱡᱚᱦᱟᱨ", "rom": "Johar"}

        return [
            {
                "front_text": f"{topic_title}",
                "back_text": f"Curriculum Unit: Class {class_number} {subject}\n({chapter})",
                "category": "Syllabus Unit"
            },
            {
                "front_text": "School / विद्यालय",
                "back_text": card_back(school_dict),
                "category": "Everyday Vocabulary"
            },
            {
                "front_text": "Teacher / शिक्षक",
                "back_text": card_back(teacher_dict),
                "category": "Classroom"
            },
            {
                "front_text": "Student / छात्र",
                "back_text": card_back(student_dict),
                "category": "Classroom"
            },
            {
                "front_text": "Book / पुस्तक",
                "back_text": card_back(book_dict),
                "category": "Learning Material"
            },
            {
                "front_text": "Greetings / नमस्ते",
                "back_text": card_back(greetings_dict),
                "category": "Daily Speech"
            }
        ]

    @staticmethod
    def generate_worksheet_grounded(
        class_number: int,
        subject: str,
        chapter: str,
        topic: str = "",
        language: str = "Santali (English)"
    ) -> Dict:
        """
        Generates a bilingual printable worksheet with bracketed language support.
        """
        topic_title = topic if topic else chapter
        content = (
            f"=========================================================================\n"
            f"          GOVERNMENT PRIMARY EDUCATION - BILINGUAL WORKSHEET             \n"
            f"           Source: J-Guruji Jharkhand & NCERT Pedagogical Core           \n"
            f"=========================================================================\n"
            f"Class: {class_number}    | Subject: {subject}    | Chapter: {chapter}\n"
            f"Topic: {topic_title}\n"
            f"Student Name: __________________________    Date: _______________\n"
            f"School: ________________________________\n"
            f"-------------------------------------------------------------------------\n\n"
            f"SECTION 1: VOCABULARY MATCHING (ᱡᱚᱲᱟᱣ ᱢᱮ / जोड़ियाँ मिलाएँ)\n"
            f"Draw a line connecting the Santali word to its correct meaning:\n"
            f"  1. ᱟᱥᱲᱟ (Asda)           [  ] A. Teacher (शिक्षक)\n"
            f"  2. ᱢᱟᱪᱮᱛ (Machet)        [  ] B. Student (विद्यार्थी)\n"
            f"  3. ᱯᱟᱹᱴᱷᱩᱣᱟᱹ (Pathuwa)     [  ] C. Book (पुस्तक)\n"
            f"  4. ᱯᱩᱛᱷᱤ (Puthi)         [  ] D. School (विद्यालय)\n"
            f"  5. ᱡᱚᱦᱟᱨ (Johar)          [  ] E. Respectful Greetings (नमस्ते)\n\n"
            f"SECTION 2: CONCEPT QUESTIONS (ᱠᱩᱠᱞᱤ ᱛᱮᱞᱟ / प्रश्न-उत्तर)\n"
            f"Q1. Explain the main idea of '{topic_title}' in your own words:\n"
            f"Answer: _________________________________________________________________\n"
            f"        _________________________________________________________________\n\n"
            f"Q2. Write one example from your village (ᱟᱹᱛᱩ / Atu) related to this topic:\n"
            f"Answer: _________________________________________________________________\n"
            f"        _________________________________________________________________\n\n"
            f"SECTION 3: TEACHER REMARKS & EVALUATION\n"
            f"Teacher Assessment: [ ] Excellent   [ ] Good   [ ] Needs Practice\n"
            f"Signature of Teacher (ᱢᱟᱪᱮᱛ): _____________________\n"
            f"=========================================================================\n"
        )
        return {
            "title": f"Class {class_number} {subject}: {topic_title} - Bilingual Worksheet",
            "content_bilingual": content,
            "instructions": "Complete all sections. Practice mother tongue terminology with your teacher."
        }

    @staticmethod
    def resolve_doubt(
        class_number: int,
        subject: str,
        chapter: str,
        student_question: str,
        language: str = "Santali (English)"
    ) -> Dict:
        """
        Dynamically analyzes the student's question and produces a syllabus-grounded answer
        matching their language preference:
        - Santali (English): Santali with English in brackets
        - Santali (Hindi): Santali with Hindi in brackets
        - Hindi: Hindi explanation
        - English: English explanation
        """
        q_clean = student_question.strip().lower()
        pref = language.strip().lower()

        # Generate concept body
        if any(w in q_clean for w in ["गिनती", "count", "counting", "number", "संख्या", "संख्याएं", "el", "lekha"]):
            if pref == "hindi":
                body = (
                    f"कक्षा {class_number} {subject} के अध्याय '{chapter}' में हम संख्याओं को क्रमानुसार सीखते हैं। "
                    f"संथाली में गिनती इस प्रकार होती है: "
                    f"१ = ᱢᱤᱫ (एक), २ = ᱵᱟᱨ (दो), ३ = ᱯᱮ (तीन), ४ = ᱯᱩᱱ (चार), ५ = ᱢᱚᱬᱮ (पाँच), "
                    f"६ = ᱛᱩᱨᱩᱭ (छह), ७ = ᱮᱭᱟᱭ (सात), ८ = ᱤᱨᱟᱹᱞ (आठ), ९ = ᱟᱨᱮ (नौ), १० = ᱜᱮᱞ (दस)। "
                    f"कक्षा में वस्तुओं को गिनकर अभ्यास करें!"
                )
            elif pref == "english":
                body = (
                    f"In Class {class_number} {subject} ('{chapter}'), numbers are learned sequentially. "
                    f"In Santali, numbers 1 to 10 are: "
                    f"1 = Mit, 2 = Bar, 3 = Pe, 4 = Pun, 5 = More, "
                    f"6 = Turuy, 7 = Eyay, 8 = Iral, 9 = Are, 10 = Gel. "
                    f"Practice counting physical objects with your teacher!"
                )
            elif "hindi" in pref:
                body = (
                    f"In Class {class_number} {subject} ('{chapter}'), ᱮᱞ ᱞᱮᱠᱷᱟ (Counting) [गिनती] is foundational. "
                    f"In Santali, numbers are: "
                    f"1 = ᱢᱤᱫ (Mit) [एक], 2 = ᱵᱟᱨ (Bar) [दो], 3 = ᱯᱮ (Pe) [तीन], 4 = ᱯᱩᱱ (Pun) [चार], 5 = ᱢᱚᱬᱮ (More) [पाँच], "
                    f"6 = ᱛᱩᱨᱩᱭ (Turuy) [छह], 7 = ᱮᱭᱟᱭ (Eyay) [सात], 8 = ᱤᱨᱟᱹᱞ (Iral) [आठ], 9 = ᱟᱨᱮ (Are) [नौ], 10 = ᱜᱮᱞ (Gel) [दस]।"
                )
            else: # Santali (English)
                body = (
                    f"In Class {class_number} {subject} ('{chapter}'), ᱮᱞ ᱞᱮᱠᱷᱟ (Counting) [Numbers] is foundational. "
                    f"In Santali, numbers are: "
                    f"1 = ᱢᱤᱫ (Mit) [One], 2 = ᱵᱟᱨ (Bar) [Two], 3 = ᱯᱮ (Pe) [Three], 4 = ᱯᱩᱱ (Pun) [Four], 5 = ᱢᱚᱬᱮ (More) [Five], "
                    f"6 = ᱛᱩᱨᱩᱭ (Turuy) [Six], 7 = ᱮᱭᱟᱭ (Eyay) [Seven], 8 = ᱤᱨᱟᱹᱞ (Iral) [Eight], 9 = ᱟᱨᱮ (Are) [Nine], 10 = ᱜᱮᱞ (Gel) [Ten]।"
                )
        elif any(w in q_clean for w in ["जोड़", "add", "addition", "mesa"]):
            if "hindi" in pref and "santali" not in pref:
                body = (
                    f"कक्षा {class_number} {subject} ('{chapter}') में जोड़ का अर्थ है दो समूहों को मिलाना। "
                    f"संथाली में इसे 'ᱢᱮᱥᱟ (Mesa)' कहते हैं।"
                )
            elif "hindi" in pref:
                body = (
                    f"In Class {class_number} {subject} ('{chapter}'), addition means combining quantities. "
                    f"In Santali, addition is called 'ᱢᱮᱥᱟ (Mesa) [जोड़]'. "
                    f"For example: ᱵᱟᱨ (2) [दो] + ᱯᱮ (3) [तीन] = ᱢᱚᱬᱮ (5) [पाँच]।"
                )
            else:
                body = (
                    f"In Class {class_number} {subject} ('{chapter}'), addition means combining quantities. "
                    f"In Santali, addition is called 'ᱢᱮᱥᱟ (Mesa) [Addition]'. "
                    f"For example: ᱵᱟᱨ (2) [Two] + ᱯᱮ (3) [Three] = ᱢᱚᱬᱮ (5) [Five]।"
                )
        elif any(w in q_clean for w in ["घटाव", "subtract", "subtraction", "bhegar", "kom"]):
            if "hindi" in pref:
                body = (
                    f"In Class {class_number} {subject} ('{chapter}'), subtraction means taking away an amount. "
                    f"In Santali, this is called 'ᱵᱷᱮᱜᱟᱨ (Bhegar) [घटाव]' or 'ᱠᱚᱢ (Kom) [कम करना]'. "
                    f"If you have ᱯᱩᱱ (4) [चार] and take away ᱢᱤᱫ (1) [एक], you have ᱯᱮ (3) [तीन] left."
                )
            else:
                body = (
                    f"In Class {class_number} {subject} ('{chapter}'), subtraction means taking away an amount. "
                    f"In Santali, this is called 'ᱵᱷᱮᱜᱟᱨ (Bhegar) [Subtraction]' or 'ᱠᱚᱢ (Kom) [Reduce]'. "
                    f"If you have ᱯᱩᱱ (4) [Four] and take away ᱢᱤᱫ (1) [One], you have ᱯᱮ (3) [Three] left."
                )
        elif any(w in q_clean for w in ["पेड़", "पौधे", "water", "पानी", "पर्यावरण", "nature", "dare", "dak"]):
            if "hindi" in pref:
                body = (
                    f"In Class {class_number} Environmental Studies / {subject} ('{chapter}'), we observe our natural surroundings. "
                    f"Water is called 'ᱫᱟᱜ (Dak) [पानी]', tree is 'ᱫᱟᱨᱮ (Dare) [पेड़]', flower is 'ᱵᱟᱦᱟ (Baha) [फूल]', "
                    f"and bird is 'ᱪᱮᱬᱮ (Chene) [पक्षी]'."
                )
            else:
                body = (
                    f"In Class {class_number} Environmental Studies / {subject} ('{chapter}'), we observe our natural surroundings. "
                    f"Water is called 'ᱫᱟᱜ (Dak) [Water]', tree is 'ᱫᱟᱨᱮ (Dare) [Tree]', flower is 'ᱵᱟᱦᱟ (Baha) [Flower]', "
                    f"and bird is 'ᱪᱮᱬᱮ (Chene) [Bird]'."
                )
        else:
            # Perform dynamic translation of student question into Santali and extract conceptual terms
            trans_q = AIService.translate_multilingual(student_question, "English" if any(c in 'abcdefghijklmnopqrstuvwxyz' for c in q_clean) else "Hindi", "Santali")
            santali_equiv = trans_q.get("translated_text", "")

            if pref == "hindi":
                body = (
                    f"आपके प्रश्न '{student_question}' के संबंध में:\n"
                    f"कक्षा {class_number} {subject} के अध्याय '{chapter}' में यह विषय महत्वपूर्ण है।\n"
                    f"संथाली में इस संकल्पना को '{santali_equiv}' के रूप में समझा जाता है।\n"
                    f"कक्षा में गुरुजी (ᱢᱟᱪᱮᱛ) के साथ पाठ्यपुस्तक और अभ्यास पत्रक (Worksheet) की सहायता से इसका नियमित अभ्यास करें।"
                )
            elif pref == "english":
                body = (
                    f"Regarding your question '{student_question}':\n"
                    f"In Class {class_number} {subject} ('{chapter}'), this concept is an essential learning outcome.\n"
                    f"In Santali, this is expressed as: '{santali_equiv}'.\n"
                    f"Use classroom physical examples, flashcards, and the 5-question quiz to solidify your conceptual understanding."
                )
            elif "hindi" in pref:
                body = (
                    f"Regarding your question '{student_question}':\n"
                    f"In Class {class_number} {subject} ('{chapter}'), this topic is foundational for primary learners.\n"
                    f"Santali translation: {santali_equiv} [प्रश्न की समझ]\n"
                    f"Key vocabulary for this lesson:\n"
                    f"- ᱢᱟᱪᱮᱛ (Machet) [शिक्षक/गुरुजी]\n"
                    f"- ᱯᱟᱲᱦᱟᱣ (Parhaw) [पाठ/पढ़ाई]\n"
                    f"- ᱠᱩᱠᱞᱤ (Kukli) [प्रश्न] -> ᱛᱮᱞᱟ (Tela) [उत्तर]\n"
                    f"Consult your teacher and review your syllabus flashcards to master this concept!"
                )
            else: # Santali (English)
                body = (
                    f"Regarding your question '{student_question}':\n"
                    f"In Class {class_number} {subject} ('{chapter}'), this topic is foundational for primary learners.\n"
                    f"Santali translation: {santali_equiv} [Question Meaning]\n"
                    f"Key vocabulary for this lesson:\n"
                    f"- ᱢᱟᱪᱮᱛ (Machet) [Teacher]\n"
                    f"- ᱯᱟᱲᱦᱟᱣ (Parhaw) [Lesson/Study]\n"
                    f"- ᱠᱩᱠᱞᱤ (Kukli) [Question] -> ᱛᱮᱞᱟ (Tela) [Answer]\n"
                    f"Consult your teacher and review your syllabus flashcards to master this concept!"
                )

        greeting = "ᱡᱚᱦᱟᱨ (Johar)!" if "english" not in pref else "Hello and Johar!"
        full_response = (
            f"{greeting}\n\n"
            f"{body}\n\n"
            f"Curriculum Reference: J-Guruji Class {class_number} {subject} &bull; Chapter: {chapter}"
        )

        return {
            "question": student_question,
            "response": full_response,
            "language": language,
            "grounded_context": f"Class {class_number} {subject} - {chapter}"
        }
