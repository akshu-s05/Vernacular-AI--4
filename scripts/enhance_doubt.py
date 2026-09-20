def update():
    with open('backend/ai_services.py', 'r', encoding='utf-8') as f:
        text = f.read()

    old_code = """        else:
            trans_sample = AIService.translate_multilingual(student_question, "Hindi", "Santali")
            body = (
                f"Regarding your specific question about '{student_question}' in Class {class_number} {subject} ('{chapter}'):\\n\\n"
                f"Syllabus Guidance:\\n"
                f"This unit is structured according to J-Guruji Jharkhand guidelines to help you learn clearly. "
                f"Whenever you have doubts, speak with your ᱢᱟᱪᱮᱛ (Machet) [Teacher] in class (ᱟᱥᱲᱟ). "
                f"Practicing the 5-question quiz and flashcards will make this topic easy!"
            )"""

    new_code = """        else:
            # Perform dynamic translation of student question into Santali and extract conceptual terms
            trans_q = AIService.translate_multilingual(student_question, "English" if any(c in 'abcdefghijklmnopqrstuvwxyz' for c in q_clean) else "Hindi", "Santali")
            santali_equiv = trans_q.get("translated_text", "")

            if pref == "hindi":
                body = (
                    f"आपके प्रश्न '{student_question}' के संबंध में:\\n"
                    f"कक्षा {class_number} {subject} के अध्याय '{chapter}' में यह विषय महत्वपूर्ण है।\\n"
                    f"संथाली में इस संकल्पना को '{santali_equiv}' के रूप में समझा जाता है।\\n"
                    f"कक्षा में गुरुजी (ᱢᱟᱪᱮᱛ) के साथ पाठ्यपुस्तक और अभ्यास पत्रक (Worksheet) की सहायता से इसका नियमित अभ्यास करें।"
                )
            elif pref == "english":
                body = (
                    f"Regarding your question '{student_question}':\\n"
                    f"In Class {class_number} {subject} ('{chapter}'), this concept is an essential learning outcome.\\n"
                    f"In Santali, this is expressed as: '{santali_equiv}'.\\n"
                    f"Use classroom physical examples, flashcards, and the 5-question quiz to solidify your conceptual understanding."
                )
            elif "hindi" in pref:
                body = (
                    f"Regarding your question '{student_question}':\\n"
                    f"In Class {class_number} {subject} ('{chapter}'), this topic is foundational for primary learners.\\n"
                    f"Santali translation: {santali_equiv} [प्रश्न की समझ]\\n"
                    f"Key vocabulary for this lesson:\\n"
                    f"- ᱢᱟᱪᱮᱛ (Machet) [शिक्षक/गुरुजी]\\n"
                    f"- ᱯᱟᱲᱦᱟᱣ (Parhaw) [पाठ/पढ़ाई]\\n"
                    f"- ᱠᱩᱠᱞᱤ (Kukli) [प्रश्न] -> ᱛᱮᱞᱟ (Tela) [उत्तर]\\n"
                    f"Consult your teacher and review your syllabus flashcards to master this concept!"
                )
            else: # Santali (English)
                body = (
                    f"Regarding your question '{student_question}':\\n"
                    f"In Class {class_number} {subject} ('{chapter}'), this topic is foundational for primary learners.\\n"
                    f"Santali translation: {santali_equiv} [Question Meaning]\\n"
                    f"Key vocabulary for this lesson:\\n"
                    f"- ᱢᱟᱪᱮᱛ (Machet) [Teacher]\\n"
                    f"- ᱯᱟᱲᱦᱟᱣ (Parhaw) [Lesson/Study]\\n"
                    f"- ᱠᱩᱠᱞᱤ (Kukli) [Question] -> ᱛᱮᱞᱟ (Tela) [Answer]\\n"
                    f"Consult your teacher and review your syllabus flashcards to master this concept!"
                )"""

    if old_code in text:
        text = text.replace(old_code, new_code)
        with open('backend/ai_services.py', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Enhanced resolve_doubt applied successfully!")
    else:
        print("Pattern not matched!")

if __name__ == '__main__':
    update()
