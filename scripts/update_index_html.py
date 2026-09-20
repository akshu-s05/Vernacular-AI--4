import sys

def run():
    with open('backend/static/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Teacher offline section
    teacher_offline_html = """      <!-- TEACHER: OFFLINE CONTENT -->
      <div id="secTeacherOffline" style="display: none;">
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3>Offline Local Storage & Cache Management</h3>
            <span class="sync-status-badge" style="background: var(--accent-green-bg); color: var(--accent-green);">Local SQLite & Web Storage Active</span>
          </div>
          <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem;">
            Teachers can author lessons, browse cached J-Guruji chapters, and prepare worksheets without active internet connectivity. All modifications queue automatically for cloud synchronization.
          </p>
          <div class="grid-3" style="margin-bottom: 1rem;">
            <div class="card" style="background: var(--surface-subtle);">
              <h4>Cached Lessons</h4>
              <p style="font-size: 1.5rem; font-weight: 700; color: var(--primary); margin-top: 0.5rem;" id="cachedLessonsCount">0</p>
            </div>
            <div class="card" style="background: var(--surface-subtle);">
              <h4>Queued Offline Actions</h4>
              <p style="font-size: 1.5rem; font-weight: 700; color: #D97706; margin-top: 0.5rem;" id="queuedActionsCount">0</p>
            </div>
            <div class="card" style="background: var(--surface-subtle);">
              <h4>Storage Engine</h4>
              <p style="font-size: 1rem; font-weight: 600; color: var(--accent-green); margin-top: 0.5rem;">IndexedDB / LocalStorage</p>
            </div>
          </div>
          <button class="btn" onclick="triggerSync()">Run Cloud Synchronization Now</button>
        </div>
      </div>
"""

    if 'id="secTeacherOffline"' not in content:
        content = content.replace('      <!-- TEACHER: WORKSHEETS -->', teacher_offline_html + '\n      <!-- TEACHER: WORKSHEETS -->')

    # 2. Update Student portal tabs and header
    old_student_tabs = """    <!-- STUDENT PORTAL -->
    <div id="studentPortal" style="display: none;">
      <div class="tabs">
        <button class="tab active" onclick="showStudentSection('home')">🏠 Student Home</button>
        <button class="tab" onclick="showStudentSection('learn')">Continue Learning</button>
        <button class="tab" onclick="showStudentSection('subjects')">Browse Curriculum</button>
        <button class="tab" onclick="showStudentSection('quiz')">Lesson Quiz</button>
        <button class="tab" onclick="showStudentSection('flashcards')">Flashcards</button>
        <button class="tab" onclick="showStudentSection('doubts')">Ask Doubt</button>
        <button class="tab" onclick="showStudentSection('progress')">My Progress</button>
      </div>"""

    new_student_tabs = """    <!-- STUDENT PORTAL -->
    <div id="studentPortal" style="display: none;">
      <div class="tabs">
        <button class="tab active" onclick="showStudentSection('home')">Dashboard</button>
        <button class="tab" onclick="showStudentSection('learn')">Continue Learning</button>
        <button class="tab" onclick="showStudentSection('subjects')">Subjects</button>
        <button class="tab" onclick="showStudentSection('progress')">Progress</button>
        <button class="tab" onclick="showStudentSection('doubts')">Ask Doubt</button>
        <button class="tab" onclick="showStudentSection('downloads')">Downloads</button>
        <button class="tab" onclick="triggerSync()">Sync</button>
        <button class="tab" onclick="openProfileModal()">Profile</button>
        <button class="tab" onclick="logout()">Logout</button>
      </div>"""

    content = content.replace(old_student_tabs, new_student_tabs)

    # 3. Update Student Home header and 8 buttons
    old_student_home = """      <!-- STUDENT HOMEPAGE / DASHBOARD -->
      <div id="secStudentHome">
        <div class="hero-card">
          <h2 id="studentHomeWelcome">Welcome, Student!</h2>
          <p style="color: #78350F; margin-top: 0.4rem; font-size: 0.95rem;">
            Your Class: <strong id="studentHomeClass">Class 3</strong> &bull; Language: <strong id="studentHomeLang">Santali (English)</strong>
          </p>
          <p style="margin-top: 0.8rem; font-size: 0.9rem; color: #92400E;">
            Learn subjects in your mother tongue with lessons, audio read-aloud, interactive flashcards, and quizzes!
          </p>
        </div>

        <div class="grid-3" style="margin-bottom: 1.5rem;">
          <div class="card" style="cursor: pointer;" onclick="showStudentSection('learn')">
            <span style="font-size: 2rem;">📖</span>
            <h4 style="margin-top: 0.5rem;">Continue Learning</h4>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.3rem;">Resume your active textbook chapter with mother-tongue audio.</p>
          </div>
          <div class="card" style="cursor: pointer;" onclick="showStudentSection('quiz')">
            <span style="font-size: 2rem;">🎯</span>
            <h4 style="margin-top: 0.5rem;">Practice 5-Question Quiz</h4>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.3rem;">Test your understanding with instant feedback.</p>
          </div>
          <div class="card" style="cursor: pointer;" onclick="showStudentSection('doubts')">
            <span style="font-size: 2rem;">💡</span>
            <h4 style="margin-top: 0.5rem;">Ask AI Doubt Assistant</h4>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.3rem;">Type or speak your questions in Hindi or Santali.</p>
          </div>
        </div>
      </div>"""

    new_student_home = """      <!-- STUDENT HOMEPAGE / DASHBOARD -->
      <div id="secStudentHome">
        <div class="hero-card">
          <h2 id="studentHomeWelcome">Welcome Student</h2>
          <div style="margin-top: 0.5rem; font-size: 0.95rem; color: #78350F; display: flex; gap: 1.5rem; flex-wrap: wrap;">
            <span>Grade: <strong id="studentHomeClass">Class 3</strong></span>
            <span>School: <strong id="studentHomeSchool">Government Primary School</strong></span>
            <span>Language: <strong id="studentHomeLang">Santali (English)</strong></span>
            <span class="sync-status-badge" id="studentOnlineBadge" style="background: var(--accent-green-bg); color: var(--accent-green);">Online</span>
          </div>
          <p style="margin-top: 0.8rem; font-size: 0.9rem; color: #92400E;">
            Welcome to your digital classroom. Learn foundational subjects in your mother tongue with lessons, spoken audio, flashcards, and quizzes.
          </p>
        </div>

        <h3 style="margin-bottom: 0.8rem;">Classroom Navigation</h3>
        <div class="grid-4" style="margin-bottom: 1.5rem;">
          <div class="card" style="cursor: pointer; text-align: center; padding: 1.2rem;" onclick="showStudentSection('learn')">
            <span style="font-size: 2.2rem;">📖</span>
            <h4 style="margin-top: 0.5rem;">Continue Learning</h4>
            <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.2rem;">Resume active lesson</p>
          </div>
          <div class="card" style="cursor: pointer; text-align: center; padding: 1.2rem;" onclick="showStudentSection('subjects')">
            <span style="font-size: 2.2rem;">📚</span>
            <h4 style="margin-top: 0.5rem;">Subjects</h4>
            <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.2rem;">J-Guruji curriculum</p>
          </div>
          <div class="card" style="cursor: pointer; text-align: center; padding: 1.2rem;" onclick="showStudentSection('progress')">
            <span style="font-size: 2.2rem;">📊</span>
            <h4 style="margin-top: 0.5rem;">Progress</h4>
            <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.2rem;">Scores & achievements</p>
          </div>
          <div class="card" style="cursor: pointer; text-align: center; padding: 1.2rem;" onclick="showStudentSection('doubts')">
            <span style="font-size: 2.2rem;">💡</span>
            <h4 style="margin-top: 0.5rem;">Ask Doubt</h4>
            <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.2rem;">Voice & AI assistant</p>
          </div>
          <div class="card" style="cursor: pointer; text-align: center; padding: 1.2rem;" onclick="showStudentSection('downloads')">
            <span style="font-size: 2.2rem;">💾</span>
            <h4 style="margin-top: 0.5rem;">Downloads</h4>
            <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.2rem;">Offline cached lessons</p>
          </div>
          <div class="card" style="cursor: pointer; text-align: center; padding: 1.2rem;" onclick="triggerSync()">
            <span style="font-size: 2.2rem;">🔄</span>
            <h4 style="margin-top: 0.5rem;">Sync</h4>
            <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.2rem;">Cloud synchronization</p>
          </div>
          <div class="card" style="cursor: pointer; text-align: center; padding: 1.2rem;" onclick="openProfileModal()">
            <span style="font-size: 2.2rem;">👤</span>
            <h4 style="margin-top: 0.5rem;">Profile</h4>
            <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.2rem;">Manage preferences</p>
          </div>
          <div class="card" style="cursor: pointer; text-align: center; padding: 1.2rem;" onclick="logout()">
            <span style="font-size: 2.2rem;">🚪</span>
            <h4 style="margin-top: 0.5rem;">Logout</h4>
            <p style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.2rem;">Exit session safely</p>
          </div>
        </div>
      </div>"""

    content = content.replace(old_student_home, new_student_home)

    # 4. Add Download Lesson button to Continue Learning
    old_speak_btn = '<button class="btn btn-green" onclick="speakCurrentLesson()">🔊 Play Audio (Santali)</button>'
    new_speak_btn = """<div style="display: flex; gap: 0.5rem;">
              <button class="btn btn-secondary" onclick="downloadActiveLesson()">💾 Download Offline</button>
              <button class="btn btn-green" onclick="speakCurrentLesson()">🔊 Play Audio (Santali)</button>
            </div>"""
    content = content.replace(old_speak_btn, new_speak_btn)

    # 5. Add Downloads Section right after Progress section
    student_downloads_html = """      <!-- STUDENT: DOWNLOADS (OFFLINE CONTENT) -->
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
      </div>
"""
    if 'id="secStudentDownloads"' not in content:
        content = content.replace('      <!-- STUDENT: PROGRESS -->', student_downloads_html + '\n      <!-- STUDENT: PROGRESS -->')

    # 6. Add Profile Modal right before </body>
    profile_modal_html = """  <!-- PROFILE MODAL -->
  <div id="profileModal" class="modal">
    <div class="modal-content">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3 id="profileModalTitle">User Profile</h3>
        <button class="btn btn-secondary" style="padding: 0.2rem 0.6rem; cursor: pointer;" onclick="closeProfileModal()">&times;</button>
      </div>
      <label>Full Name</label>
      <input type="text" id="profileNameInput">
      <label>School / Institution</label>
      <input type="text" id="profileSchoolInput">
      <div id="profileClassGroup" style="display: none;">
        <label>Class / Grade</label>
        <select id="profileClassSelect">
          <option value="1">Class 1</option>
          <option value="2">Class 2</option>
          <option value="3">Class 3</option>
          <option value="4">Class 4</option>
          <option value="5">Class 5</option>
        </select>
      </div>
      <label>Language Preference</label>
      <select id="profileLangSelect">
        <option value="Santali (English)">Santali (English)</option>
        <option value="Santali (Hindi)">Santali (Hindi)</option>
        <option value="Hindi">Hindi</option>
        <option value="English">English</option>
      </select>
      <div style="margin-top: 1.5rem; display: flex; justify-content: flex-end; gap: 0.5rem;">
        <button class="btn btn-secondary" onclick="closeProfileModal()">Cancel</button>
        <button class="btn btn-green" onclick="saveUserProfile()">Save Changes</button>
      </div>
    </div>
  </div>
"""
    if 'id="profileModal"' not in content:
        content = content.replace('</body>', profile_modal_html + '\n</body>')

    with open('backend/static/index.html', 'w', encoding='utf-8') as f:
        f.write(content)

    print("index.html successfully updated!")

if __name__ == '__main__':
    run()
