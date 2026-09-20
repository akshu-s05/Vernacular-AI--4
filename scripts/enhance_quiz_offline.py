def update():
    with open('backend/static/index.html', 'r', encoding='utf-8') as f:
        text = f.read()

    old_submit = """      const res = await fetch(`${API_BASE}/quiz/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_identifier: currentUser.identifier,
          quiz_id: currentQuizData.quiz_id,
          answers: studentAnswers
        })
      });
      const data = await res.json();"""

    new_submit = """      let data = null;
      try {
        const res = await fetch(`${API_BASE}/quiz/submit`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            student_identifier: currentUser.identifier,
            quiz_id: currentQuizData.quiz_id,
            answers: studentAnswers
          })
        });
        if (res.ok) data = await res.json();
      } catch (err) {
        console.warn('Network offline, evaluating locally:', err);
      }

      // If offline, evaluate locally and queue progress for synchronization
      if (!data) {
        let correct = 0;
        const total = currentQuizData.questions.length;
        const feedback = currentQuizData.questions.map(q => {
          const sel = studentAnswers[q.id];
          const isCorr = sel === (q.correct_option || 'A');
          if (isCorr) correct++;
          return {
            question_id: q.id,
            selected_option: sel,
            correct_option: q.correct_option || 'A',
            is_correct: isCorr,
            explanation: q.explanation || 'Reviewed in offline curriculum mode.'
          };
        });
        const pct = Math.round((correct / total) * 100);
        data = {
          status: 'OFFLINE_EVALUATED',
          total_questions: total,
          correct_answers: correct,
          score_percentage: pct,
          feedback: feedback
        };

        // Queue progress in local storage
        const pending = JSON.parse(localStorage.getItem('vernacular_pending_progress') || '[]');
        pending.push({
          lesson_id: currentLessonId,
          is_completed: true,
          best_score: pct,
          recorded_at: new Date().toISOString()
        });
        localStorage.setItem('vernacular_pending_progress', JSON.stringify(pending));
      }"""

    if old_submit in text:
        text = text.replace(old_submit, new_submit)
        with open('backend/static/index.html', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Offline quiz local grading and progress queuing wired successfully!")
    else:
        print("Snippet not found")

if __name__ == '__main__':
    update()
