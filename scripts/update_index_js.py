import sys

def run():
    with open('backend/static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update setupUserSession to populate Teacher and Student home labels accurately and load stats
    old_session_fn = """    function setupUserSession() {
      document.getElementById('authView').style.display = 'none';
      document.getElementById('logoutBtn').style.display = 'inline-flex';
      document.getElementById('userNameBadge').innerText = `Welcome, ${currentUser.name}`;

      if (currentUser.role === 'teacher') {
        document.getElementById('teacherPortal').style.display = 'block';
        document.getElementById('studentPortal').style.display = 'none';
        document.getElementById('teacherHomeWelcome').innerText = `Welcome, ${currentUser.name}`;
        document.getElementById('teacherHomeSchool').innerText = `${currentUser.school || 'Government Primary School'} • Primary Pedagogy Division`;
        showTeacherSection('home');
        loadTeacherSubjects();
        loadTeacherPublishedLessons();
      } else {
        document.getElementById('teacherPortal').style.display = 'none';
        document.getElementById('studentPortal').style.display = 'block';
        document.getElementById('studentHomeWelcome').innerText = `Welcome, ${currentUser.name}!`;
        document.getElementById('studentHomeClass').innerText = `Class ${currentGrade}`;
        document.getElementById('studentHomeLang').innerText = currentUser.preferred_language || 'Santali (English)';
        document.getElementById('studentClassBadge').innerText = `Class ${currentGrade}`;
        showStudentSection('home');
        loadStudentSubjects();
        loadStudentContinueLearning();
        loadStudentProgress();
      }
    }"""

    new_session_fn = """    function setupUserSession() {
      document.getElementById('authView').style.display = 'none';
      document.getElementById('logoutBtn').style.display = 'inline-flex';
      document.getElementById('userNameBadge').innerText = `Welcome, ${currentUser.name}`;

      if (currentUser.role === 'teacher') {
        document.getElementById('teacherPortal').style.display = 'block';
        document.getElementById('studentPortal').style.display = 'none';
        document.getElementById('teacherHomeWelcome').innerText = `Welcome ${currentUser.name}`;
        if (document.getElementById('teacherHomeId')) document.getElementById('teacherHomeId').innerText = currentUser.identifier;
        if (document.getElementById('teacherHomeSchool')) document.getElementById('teacherHomeSchool').innerText = currentUser.school || 'Government Primary School';
        if (document.getElementById('teacherHomeLang')) document.getElementById('teacherHomeLang').innerText = currentUser.preferred_language || 'English';
        showTeacherSection('home');
        loadTeacherStats();
        loadTeacherSubjects();
        loadTeacherPublishedLessons();
      } else {
        document.getElementById('teacherPortal').style.display = 'none';
        document.getElementById('studentPortal').style.display = 'block';
        document.getElementById('studentHomeWelcome').innerText = `Welcome ${currentUser.name}`;
        document.getElementById('studentHomeClass').innerText = `Class ${currentGrade}`;
        if (document.getElementById('studentHomeSchool')) document.getElementById('studentHomeSchool').innerText = currentUser.school || 'Government Primary School';
        document.getElementById('studentHomeLang').innerText = currentUser.preferred_language || 'Santali (English)';
        document.getElementById('studentClassBadge').innerText = `Class ${currentGrade}`;
        showStudentSection('home');
        loadStudentSubjects();
        loadStudentContinueLearning();
        loadStudentProgress();
        loadDownloadedLessons();
      }
    }"""

    content = content.replace(old_session_fn, new_session_fn)

    # 2. Update showTeacherSection & showStudentSection to handle all 13 and 8 sections respectively
    old_nav_sections = """    // --- NAVIGATION SECTIONS ---
    function showTeacherSection(sec) {
      document.querySelectorAll('#teacherPortal .tabs .tab').forEach(t => t.classList.remove('active'));
      if (event && event.target && event.target.classList.contains('tab')) {
        event.target.classList.add('active');
      }

      const ids = ['secTeacherHome', 'secTeacherCreate', 'secTeacherLessons', 'secTeacherUpload', 'secTeacherTranslate', 'secTeacherVoice', 'secTeacherAI', 'secTeacherWorksheets'];
      ids.forEach(id => document.getElementById(id).style.display = 'none');

      if (sec === 'home') document.getElementById('secTeacherHome').style.display = 'block';
      if (sec === 'create') document.getElementById('secTeacherCreate').style.display = 'block';
      if (sec === 'lessons') { document.getElementById('secTeacherLessons').style.display = 'block'; loadTeacherPublishedLessons(); }
      if (sec === 'upload') document.getElementById('secTeacherUpload').style.display = 'block';
      if (sec === 'translate') document.getElementById('secTeacherTranslate').style.display = 'block';
      if (sec === 'voice') document.getElementById('secTeacherVoice').style.display = 'block';
      if (sec === 'ai') document.getElementById('secTeacherAI').style.display = 'block';
      if (sec === 'worksheets') document.getElementById('secTeacherWorksheets').style.display = 'block';
    }

    function showStudentSection(sec) {
      document.querySelectorAll('#studentPortal .tabs .tab').forEach(t => t.classList.remove('active'));
      if (event && event.target && event.target.classList.contains('tab')) {
        event.target.classList.add('active');
      }

      const ids = ['secStudentHome', 'secStudentLearn', 'secStudentSubjects', 'secStudentQuiz', 'secStudentFlashcards', 'secStudentDoubts', 'secStudentProgress'];
      ids.forEach(id => document.getElementById(id).style.display = 'none');

      if (sec === 'home') document.getElementById('secStudentHome').style.display = 'block';
      if (sec === 'learn') document.getElementById('secStudentLearn').style.display = 'block';
      if (sec === 'subjects') { document.getElementById('secStudentSubjects').style.display = 'block'; loadStudentSubjects(); }
      if (sec === 'quiz') { document.getElementById('secStudentQuiz').style.display = 'block'; loadLessonQuiz(); }
      if (sec === 'flashcards') { document.getElementById('secStudentFlashcards').style.display = 'block'; loadStudentFlashcards(); }
      if (sec === 'doubts') document.getElementById('secStudentDoubts').style.display = 'block';
      if (sec === 'progress') { document.getElementById('secStudentProgress').style.display = 'block'; loadStudentProgress(); }
    }"""

    new_nav_sections = """    // --- NAVIGATION SECTIONS ---
    function showTeacherSection(sec) {
      document.querySelectorAll('#teacherPortal .tabs .tab').forEach(t => t.classList.remove('active'));
      if (window.event && window.event.target && window.event.target.classList.contains('tab')) {
        window.event.target.classList.add('active');
      }

      const ids = ['secTeacherHome', 'secTeacherCreate', 'secTeacherLessons', 'secTeacherUpload', 'secTeacherTranslate', 'secTeacherVoice', 'secTeacherAI', 'secTeacherWorksheets', 'secTeacherOffline'];
      ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
      });

      if (sec === 'home') { document.getElementById('secTeacherHome').style.display = 'block'; loadTeacherStats(); }
      if (sec === 'create') document.getElementById('secTeacherCreate').style.display = 'block';
      if (sec === 'lessons') { document.getElementById('secTeacherLessons').style.display = 'block'; loadTeacherPublishedLessons(); }
      if (sec === 'upload') document.getElementById('secTeacherUpload').style.display = 'block';
      if (sec === 'translate') document.getElementById('secTeacherTranslate').style.display = 'block';
      if (sec === 'voice') document.getElementById('secTeacherVoice').style.display = 'block';
      if (sec === 'worksheets') document.getElementById('secTeacherWorksheets').style.display = 'block';
      if (sec === 'flashcards') { showTeacherSection('ai'); generateFlashcardsForLesson(); }
      if (sec === 'ai') document.getElementById('secTeacherAI').style.display = 'block';
      if (sec === 'offline') {
        const el = document.getElementById('secTeacherOffline');
        if (el) el.style.display = 'block';
        updateTeacherOfflineStats();
      }
    }

    function showStudentSection(sec) {
      document.querySelectorAll('#studentPortal .tabs .tab').forEach(t => t.classList.remove('active'));
      if (window.event && window.event.target && window.event.target.classList.contains('tab')) {
        window.event.target.classList.add('active');
      }

      const ids = ['secStudentHome', 'secStudentLearn', 'secStudentSubjects', 'secStudentQuiz', 'secStudentFlashcards', 'secStudentDoubts', 'secStudentProgress', 'secStudentDownloads'];
      ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
      });

      if (sec === 'home') document.getElementById('secStudentHome').style.display = 'block';
      if (sec === 'learn') document.getElementById('secStudentLearn').style.display = 'block';
      if (sec === 'subjects') { document.getElementById('secStudentSubjects').style.display = 'block'; loadStudentSubjects(); }
      if (sec === 'quiz') { document.getElementById('secStudentQuiz').style.display = 'block'; loadLessonQuiz(); }
      if (sec === 'flashcards') { document.getElementById('secStudentFlashcards').style.display = 'block'; loadStudentFlashcards(); }
      if (sec === 'doubts') document.getElementById('secStudentDoubts').style.display = 'block';
      if (sec === 'progress') { document.getElementById('secStudentProgress').style.display = 'block'; loadStudentProgress(); }
      if (sec === 'downloads') {
        const dl = document.getElementById('secStudentDownloads');
        if (dl) dl.style.display = 'block';
        loadDownloadedLessons();
      }
    }"""

    content = content.replace(old_nav_sections, new_nav_sections)

    # 3. Add Profile, Stats, and Offline Download functions before triggerSync()
    extra_js = """    // --- TEACHER STATS & OFFLINE ---
    async function loadTeacherStats() {
      if (!currentUser || currentUser.role !== 'teacher') return;
      try {
        const res = await fetch(`${API_BASE}/teacher/stats?identifier=${currentUser.identifier}`);
        if (res.ok) {
          const stats = await res.json();
          if (document.getElementById('statLessonsPrepared')) document.getElementById('statLessonsPrepared').innerText = stats.lessons_prepared;
          if (document.getElementById('statDrafts')) document.getElementById('statDrafts').innerText = stats.drafts;
          if (document.getElementById('statPublished')) document.getElementById('statPublished').innerText = stats.published;
          if (document.getElementById('statPendingSync')) document.getElementById('statPendingSync').innerText = stats.pending_sync;
        }
      } catch (err) {
        console.warn('Teacher stats offline:', err);
      }
    }

    function updateTeacherOfflineStats() {
      const offlineLessons = JSON.parse(localStorage.getItem('vernacular_offline_lessons') || '[]');
      const queuedActions = JSON.parse(localStorage.getItem('vernacular_sync_queue') || '[]');
      if (document.getElementById('cachedLessonsCount')) document.getElementById('cachedLessonsCount').innerText = offlineLessons.length;
      if (document.getElementById('queuedActionsCount')) document.getElementById('queuedActionsCount').innerText = queuedActions.length;
    }

    // --- PROFILE MODAL MANAGEMENT ---
    function openProfileModal() {
      if (!currentUser) return;
      document.getElementById('profileNameInput').value = currentUser.name || '';
      document.getElementById('profileSchoolInput').value = currentUser.school || '';
      document.getElementById('profileLangSelect').value = currentUser.preferred_language || 'Santali (English)';
      
      const isStudent = currentUser.role === 'student';
      document.getElementById('profileClassGroup').style.display = isStudent ? 'block' : 'none';
      if (isStudent) {
        document.getElementById('profileClassSelect').value = currentGrade || 3;
      }
      document.getElementById('profileModal').style.display = 'flex';
    }

    function closeProfileModal() {
      document.getElementById('profileModal').style.display = 'none';
    }

    async function saveUserProfile() {
      if (!currentUser) return;
      const name = document.getElementById('profileNameInput').value.trim();
      const school = document.getElementById('profileSchoolInput').value.trim();
      const lang = document.getElementById('profileLangSelect').value;
      const cls = parseInt(document.getElementById('profileClassSelect').value);

      const endpoint = currentUser.role === 'teacher' ? `${API_BASE}/teacher/profile` : `${API_BASE}/student/profile`;
      try {
        const res = await fetch(`${endpoint}?identifier=${currentUser.identifier}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: name,
            school: school,
            preferred_language: lang,
            class_number: cls
          })
        });
        if (res.ok) {
          const data = await res.json();
          currentUser.name = data.user.name;
          currentUser.school = data.user.school;
          currentUser.preferred_language = data.user.preferred_language;
          if (data.user.class_number) currentGrade = data.user.class_number;

          document.getElementById('userNameBadge').innerText = `Welcome, ${currentUser.name}`;
          if (currentUser.role === 'teacher') {
            document.getElementById('teacherHomeWelcome').innerText = `Welcome ${currentUser.name}`;
            if (document.getElementById('teacherHomeSchool')) document.getElementById('teacherHomeSchool').innerText = currentUser.school;
            if (document.getElementById('teacherHomeLang')) document.getElementById('teacherHomeLang').innerText = currentUser.preferred_language;
          } else {
            document.getElementById('studentHomeWelcome').innerText = `Welcome ${currentUser.name}`;
            document.getElementById('studentHomeClass').innerText = `Class ${currentGrade}`;
            if (document.getElementById('studentHomeSchool')) document.getElementById('studentHomeSchool').innerText = currentUser.school;
            document.getElementById('studentHomeLang').innerText = currentUser.preferred_language;
            document.getElementById('studentClassBadge').innerText = `Class ${currentGrade}`;
          }
          closeProfileModal();
          alert('Profile updated successfully!');
        } else {
          alert('Failed to update profile.');
        }
      } catch (err) {
        alert('Network error updating profile: ' + err);
      }
    }

    // --- STUDENT OFFLINE DOWNLOADS & LOCALSTORAGE ---
    function downloadActiveLesson() {
      const lessonTitle = document.getElementById('activeLessonTitle').innerText;
      const breadcrumb = document.getElementById('activeLessonBreadcrumb').innerText;
      const body = document.getElementById('activeLessonBody').innerText;
      const santali = document.getElementById('activeLessonSantali').innerText;

      const item = {
        lesson_id: currentLessonId,
        title: lessonTitle,
        breadcrumb: breadcrumb,
        body: body,
        santali: santali,
        downloaded_at: new Date().toLocaleDateString(),
        class_number: currentGrade
      };

      let offlineLessons = JSON.parse(localStorage.getItem('vernacular_offline_lessons') || '[]');
      const existingIdx = offlineLessons.findIndex(l => l.lesson_id === currentLessonId && l.class_number === currentGrade);
      if (existingIdx >= 0) {
        offlineLessons[existingIdx] = item;
      } else {
        offlineLessons.push(item);
      }

      localStorage.setItem('vernacular_offline_lessons', JSON.stringify(offlineLessons));
      alert(`Lesson '${lessonTitle}' saved to local offline database! You can view it anytime without internet under Downloads.`);
      loadDownloadedLessons();
    }

    function loadDownloadedLessons() {
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
    }

    function viewDownloadedLesson(lesId) {
      const offlineLessons = JSON.parse(localStorage.getItem('vernacular_offline_lessons') || '[]');
      const item = offlineLessons.find(l => l.lesson_id === lesId);
      if (item) {
        currentLessonId = item.lesson_id;
        document.getElementById('activeLessonTitle').innerText = item.title;
        document.getElementById('activeLessonBreadcrumb').innerText = item.breadcrumb + ' (Offline Cached)';
        document.getElementById('activeLessonBody').innerText = item.body;
        document.getElementById('activeLessonSantali').innerText = item.santali;
        showStudentSection('learn');
      }
    }

    function deleteDownloadedLesson(lesId) {
      let offlineLessons = JSON.parse(localStorage.getItem('vernacular_offline_lessons') || '[]');
      offlineLessons = offlineLessons.filter(l => l.lesson_id !== lesId);
      localStorage.setItem('vernacular_offline_lessons', JSON.stringify(offlineLessons));
      loadDownloadedLessons();
    }
"""

    content = content.replace('    async function triggerSync() {', extra_js + '\n    async function triggerSync() {')

    with open('backend/static/index.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("JavaScript handlers and offline local database logic successfully wired!")

if __name__ == '__main__':
    run()
