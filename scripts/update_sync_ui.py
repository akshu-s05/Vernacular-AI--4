def update_sync_ui():
    with open('backend/static/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Update secStudentDownloads to also show offline Worksheets and Quizzes tabs
    old_downloads_ui = """      <!-- STUDENT: DOWNLOADS (OFFLINE CONTENT) -->
      <div id="secStudentDownloads" style="display: none;">
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
              <h3>Offline Downloaded Lessons</h3>
              <p style="color: var(--text-muted); font-size: 0.85rem;">Access all downloaded textbook lessons and practice quizzes without internet.</p>
            </div>
            <button class="btn btn-secondary" onclick="loadDownloadedLessons()">🔄 Refresh List</button>
          </div>
          <div id="downloadedLessonsList">
            <p style="color: var(--text-muted);">No offline lessons downloaded yet. Open any lesson and click 'Download Offline'.</p>
          </div>
        </div>
      </div>"""

    new_downloads_ui = """      <!-- STUDENT: DOWNLOADS (OFFLINE CONTENT) -->
      <div id="secStudentDownloads" style="display: none;">
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
              <h3>Offline Digital Classroom Storage</h3>
              <p style="color: var(--text-muted); font-size: 0.85rem;">Offline lessons, worksheets, flashcards, and quizzes available without active internet.</p>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <button class="btn btn-secondary" onclick="loadDownloadedLessons()">🔄 Refresh Storage</button>
              <button class="btn btn-green" onclick="triggerSync()">🔄 Synchronize</button>
            </div>
          </div>

          <div class="tabs" style="margin-bottom: 1rem;">
            <button class="tab active" id="tabDlLessons" onclick="switchDownloadTab('lessons')">📖 Saved Lessons (<span id="dlLessonsCount">0</span>)</button>
            <button class="tab" id="tabDlQuizzes" onclick="switchDownloadTab('quizzes')">🎯 Offline Quizzes (<span id="dlQuizzesCount">0</span>)</button>
            <button class="tab" id="tabDlWorksheets" onclick="switchDownloadTab('worksheets')">📝 Worksheets (<span id="dlWorksheetsCount">0</span>)</button>
          </div>

          <div id="viewDlLessons">
            <div id="downloadedLessonsList">
              <p style="color: var(--text-muted);">No offline lessons downloaded yet. Open any textbook chapter and click '💾 Download Offline'.</p>
            </div>
          </div>

          <div id="viewDlQuizzes" style="display: none;">
            <div id="downloadedQuizzesList">
              <p style="color: var(--text-muted);">Sync or practice quizzes to cache offline question sets.</p>
            </div>
          </div>

          <div id="viewDlWorksheets" style="display: none;">
            <div id="downloadedWorksheetsList">
              <p style="color: var(--text-muted);">No offline worksheets cached yet. Run Sync to pull recent class worksheets.</p>
            </div>
          </div>
        </div>
      </div>"""

    html = html.replace(old_downloads_ui, new_downloads_ui)

    # 2. Add triggerSync logic to update offline cache with quizzes and worksheets
    old_sync_js = """    async function triggerSync() {
      document.getElementById('syncText').innerText = 'Syncing...';
      const userIdent = currentUser ? currentUser.identifier : 'student_user';
      const role = currentUser ? currentUser.role : 'student';

      try {
        const res = await fetch(`${API_BASE}/sync`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_identifier: userIdent, role: role, progress_records: [] })
        });
        const data = await res.json();
        document.getElementById('syncText').innerText = `Online • Synced (${data.items_pulled} items pulled)`;
      } catch (err) {
        document.getElementById('syncText').innerText = 'Offline Mode (Local Storage)';
      }
    }"""

    new_sync_js = """    function switchDownloadTab(tab) {
      document.getElementById('tabDlLessons').classList.toggle('active', tab === 'lessons');
      document.getElementById('tabDlQuizzes').classList.toggle('active', tab === 'quizzes');
      document.getElementById('tabDlWorksheets').classList.toggle('active', tab === 'worksheets');
      document.getElementById('viewDlLessons').style.display = tab === 'lessons' ? 'block' : 'none';
      document.getElementById('viewDlQuizzes').style.display = tab === 'quizzes' ? 'block' : 'none';
      document.getElementById('viewDlWorksheets').style.display = tab === 'worksheets' ? 'block' : 'none';
    }

    async function triggerSync() {
      document.getElementById('syncText').innerText = 'Syncing...';
      const userIdent = currentUser ? currentUser.identifier : 'student_user';
      const role = currentUser ? currentUser.role : 'student';

      // Read any pending local offline progress records
      const pendingProgress = JSON.parse(localStorage.getItem('vernacular_pending_progress') || '[]');

      try {
        const res = await fetch(`${API_BASE}/sync`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_identifier: userIdent, role: role, progress_records: pendingProgress })
        });
        const data = await res.json();
        localStorage.removeItem('vernacular_pending_progress');

        // Cache offline worksheets if pulled
        if (data.offline_worksheets) {
          localStorage.setItem('vernacular_offline_worksheets', JSON.stringify(data.offline_worksheets));
        }
        // Cache offline quizzes if pulled
        if (data.offline_quizzes) {
          localStorage.setItem('vernacular_offline_quizzes', JSON.stringify(data.offline_quizzes));
        }

        document.getElementById('syncText').innerText = `Online • Synced (${data.items_pulled} items synchronized)`;
        alert(`Synchronization Complete!\n• Synchronized Items: ${data.items_pulled}\n• Offline Cache: Updated with latest lessons, worksheets, and quizzes.`);
        loadDownloadedLessons();
        if (currentUser && currentUser.role === 'student') loadStudentProgress();
        if (currentUser && currentUser.role === 'teacher') loadTeacherStats();
      } catch (err) {
        document.getElementById('syncText').innerText = 'Offline Mode (Local Storage Active)';
        alert('Network offline. Application running seamlessly from Local Database storage.');
      }
    }"""

    html = html.replace(old_sync_js, new_sync_js)

    # 3. Update loadDownloadedLessons to update counts and render offline quizzes & worksheets
    old_load_dl = """    function loadDownloadedLessons() {
      const listDiv = document.getElementById('downloadedLessonsList');
      if (!listDiv) return;
      const offlineLessons = JSON.parse(localStorage.getItem('vernacular_offline_lessons') || '[]');
      if (!offlineLessons.length) {
        listDiv.innerHTML = '<p style="color: var(--text-muted);">No offline lessons downloaded yet. Open any lesson and click 💾 Download Offline.</p>';
        return;
      }

      listDiv.innerHTML = offlineLessons.map(l => `
        <div class="card" style="background: var(--surface-subtle); margin-bottom: 0.8rem; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <strong>${l.title}</strong>
            <span class="sync-status-badge" style="background: var(--accent-green-bg); color: var(--accent-green); margin-left: 0.5rem;">Downloaded Offline</span>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">
              ${l.breadcrumb} &bull; Saved: ${l.downloaded_at}
            </div>
          </div>
          <div style="display: flex; gap: 0.5rem;">
            <button class="btn btn-secondary" onclick="viewDownloadedLesson(${l.lesson_id})">Study Offline</button>
            <button class="btn btn-secondary" style="color: #DC2626;" onclick="deleteDownloadedLesson(${l.lesson_id})">Delete</button>
          </div>
        </div>
      `).join('');
    }"""

    new_load_dl = """    function loadDownloadedLessons() {
      const listDiv = document.getElementById('downloadedLessonsList');
      const qListDiv = document.getElementById('downloadedQuizzesList');
      const wsListDiv = document.getElementById('downloadedWorksheetsList');

      const offlineLessons = JSON.parse(localStorage.getItem('vernacular_offline_lessons') || '[]');
      const offlineQuizzes = JSON.parse(localStorage.getItem('vernacular_offline_quizzes') || '[]');
      const offlineWorksheets = JSON.parse(localStorage.getItem('vernacular_offline_worksheets') || '[]');

      if (document.getElementById('dlLessonsCount')) document.getElementById('dlLessonsCount').innerText = offlineLessons.length;
      if (document.getElementById('dlQuizzesCount')) document.getElementById('dlQuizzesCount').innerText = offlineQuizzes.length;
      if (document.getElementById('dlWorksheetsCount')) document.getElementById('dlWorksheetsCount').innerText = offlineWorksheets.length;

      // 1. Lessons
      if (listDiv) {
        if (!offlineLessons.length) {
          listDiv.innerHTML = '<p style="color: var(--text-muted);">No offline lessons downloaded yet. Open any textbook chapter and click 💾 Download Offline.</p>';
        } else {
          listDiv.innerHTML = offlineLessons.map(l => `
            <div class="card" style="background: var(--surface-subtle); margin-bottom: 0.8rem; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <strong>${l.title}</strong>
                <span class="sync-status-badge" style="background: var(--accent-green-bg); color: var(--accent-green); margin-left: 0.5rem;">Offline Ready</span>
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">
                  ${l.breadcrumb} &bull; Saved: ${l.downloaded_at}
                </div>
              </div>
              <div style="display: flex; gap: 0.5rem;">
                <button class="btn btn-secondary" onclick="viewDownloadedLesson(${l.lesson_id})">Study Offline</button>
                <button class="btn btn-secondary" style="color: #DC2626;" onclick="deleteDownloadedLesson(${l.lesson_id})">Delete</button>
              </div>
            </div>
          `).join('');
        }
      }

      // 2. Quizzes
      if (qListDiv) {
        if (!offlineQuizzes.length) {
          qListDiv.innerHTML = '<p style="color: var(--text-muted);">No offline quizzes synchronized yet. Click Synchronize to pull latest offline quizzes.</p>';
        } else {
          qListDiv.innerHTML = offlineQuizzes.map(q => `
            <div class="card" style="background: var(--surface-subtle); margin-bottom: 0.8rem; display: flex; justify-content: space-between; align-items: center;">
              <div>
                <strong>${q.title}</strong>
                <span class="sync-status-badge" style="background: var(--accent-green-bg); color: var(--accent-green); margin-left: 0.5rem;">5 Questions Cached</span>
              </div>
              <button class="btn btn-green" onclick="playOfflineQuiz(${q.id})">Take Offline Quiz</button>
            </div>
          `).join('');
        }
      }

      // 3. Worksheets
      if (wsListDiv) {
        if (!offlineWorksheets.length) {
          wsListDiv.innerHTML = '<p style="color: var(--text-muted);">No offline worksheets cached yet. Click Synchronize to pull.</p>';
        } else {
          wsListDiv.innerHTML = offlineWorksheets.map(w => `
            <div class="card" style="background: var(--surface-subtle); margin-bottom: 0.8rem;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong>${w.title}</strong>
                <button class="btn btn-secondary" onclick="window.print()">🖨️ Print</button>
              </div>
              <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">${w.instructions || ''}</div>
              <pre style="margin-top: 0.5rem; background: #fff; padding: 0.8rem; border-radius: 4px; border: 1px solid var(--border); font-size: 0.85rem; white-space: pre-wrap;">${w.content_bilingual}</pre>
            </div>
          `).join('');
        }
      }
    }

    function playOfflineQuiz(quizId) {
      const offlineQuizzes = JSON.parse(localStorage.getItem('vernacular_offline_quizzes') || '[]');
      const qData = offlineQuizzes.find(q => q.id === quizId);
      if (qData) {
        currentQuizData = { quiz_id: qData.id, questions: qData.questions };
        showStudentSection('quiz');
        const qc = document.getElementById('quizContainer');
        qc.innerHTML = qData.questions.map((q, idx) => `
          <div class="card" style="background: var(--surface-subtle); margin-bottom: 1rem;">
            <p><strong>Q${idx + 1}. ${q.question_text} (Offline Mode)</strong></p>
            <div style="margin-top: 0.8rem;">
              ${['A', 'B', 'C', 'D'].map(opt => `
                <div class="quiz-option" id="opt_${q.id}_${opt}" onclick="selectQuizOption(${q.id}, '${opt}')">
                  <span><strong>${opt}.</strong> ${q['option_' + opt.toLowerCase()]}</span>
                </div>
              `).join('')}
            </div>
            <div id="expl_${q.id}" style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--text-muted); display: none;"></div>
          </div>
        `).join('');
      }
    }"""

    html = html.replace(old_load_dl, new_load_dl)

    with open('backend/static/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Static HTML UI enhanced for offline worksheets and offline quizzes!")

if __name__ == '__main__':
    update_sync_ui()
