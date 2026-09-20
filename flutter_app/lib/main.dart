import 'package:flutter/material.dart';
import 'services/api_service.dart';

void main() {
  runApp(const VernacularAIApp());
}

class VernacularAIApp extends StatelessWidget {
  const VernacularAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Vernacular AI Pedagogy',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF854D0E),
          primary: const Color(0xFF854D0E),
        ),
        scaffoldBackgroundColor: const Color(0xFFFBF9F5),
        useMaterial3: true,
      ),
      home: const AuthScreen(),
    );
  }
}

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  bool isTeacher = false;
  bool isRegister = false;

  final TextEditingController idController = TextEditingController();
  final TextEditingController pwdController = TextEditingController();
  final TextEditingController nameController = TextEditingController();
  final TextEditingController schoolController = TextEditingController();

  int selectedClass = 3;
  String selectedLanguage = 'Santali (English)';

  bool isLoading = false;
  String errorMessage = '';

  Future<void> submitAuth() async {
    setState(() {
      isLoading = true;
      errorMessage = '';
    });

    final id = idController.text.trim();
    final pwd = pwdController.text.trim();
    final name = nameController.text.trim();
    final school = schoolController.text.trim();

    if (id.isEmpty || pwd.isEmpty) {
      setState(() {
        isLoading = false;
        errorMessage = 'Please enter both Login ID and password.';
      });
      return;
    }

    try {
      if (isTeacher) {
        if (isRegister) {
          final res = await ApiService.registerTeacher(name, school, id, pwd, selectedLanguage);
          navigateToDashboard(res['user']);
        } else {
          final res = await ApiService.loginTeacher(id, pwd);
          navigateToDashboard(res['user']);
        }
      } else {
        if (isRegister) {
          final res = await ApiService.registerStudent(name, school, id, pwd, selectedClass, selectedLanguage);
          navigateToDashboard(res['user']);
        } else {
          final res = await ApiService.loginStudent(id, pwd);
          navigateToDashboard(res['user']);
        }
      }
    } catch (e) {
      setState(() {
        errorMessage = e.toString().replaceAll('Exception:', '').trim();
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  void navigateToDashboard(Map<String, dynamic> user) {
    if (isTeacher) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => TeacherHomeScreen(user: user)),
      );
    } else {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => StudentHomeScreen(user: user)),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 480),
            child: Card(
              elevation: 4,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.school, size: 54, color: Color(0xFF854D0E)),
                    const SizedBox(height: 8),
                    const Text(
                      'Welcome',
                      style: TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: Color(0xFF854D0E)),
                    ),
                    const Text(
                      'AI Vernacular Pedagogy • Primary Digital Classroom',
                      style: TextStyle(fontSize: 13, color: Colors.grey),
                    ),
                    const SizedBox(height: 24),
                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: !isTeacher ? const Color(0xFF166534) : Colors.grey[200],
                              foregroundColor: !isTeacher ? Colors.white : Colors.black87,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                            ),
                            onPressed: () => setState(() {
                              isTeacher = false;
                              errorMessage = '';
                            }),
                            child: const Text('Student Login', style: TextStyle(fontWeight: FontWeight.bold)),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: isTeacher ? const Color(0xFF854D0E) : Colors.grey[200],
                              foregroundColor: isTeacher ? Colors.white : Colors.black87,
                              padding: const EdgeInsets.symmetric(vertical: 12),
                            ),
                            onPressed: () => setState(() {
                              isTeacher = true;
                              errorMessage = '';
                            }),
                            child: const Text('Teacher Login', style: TextStyle(fontWeight: FontWeight.bold)),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        TextButton(
                          onPressed: () => setState(() => isRegister = false),
                          child: Text(
                            'Sign In',
                            style: TextStyle(
                              fontWeight: !isRegister ? FontWeight.bold : FontWeight.normal,
                              color: !isRegister ? const Color(0xFF854D0E) : Colors.grey,
                            ),
                          ),
                        ),
                        const Text('•'),
                        TextButton(
                          onPressed: () => setState(() => isRegister = true),
                          child: Text(
                            'Register Account',
                            style: TextStyle(
                              fontWeight: isRegister ? FontWeight.bold : FontWeight.normal,
                              color: isRegister ? const Color(0xFF854D0E) : Colors.grey,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    if (isRegister) ...[
                      TextField(
                        controller: nameController,
                        decoration: const InputDecoration(labelText: 'Full Name', border: OutlineInputBorder()),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: schoolController,
                        decoration: const InputDecoration(labelText: 'School / Institution', border: OutlineInputBorder()),
                      ),
                      const SizedBox(height: 12),
                      if (!isTeacher) ...[
                        DropdownButtonFormField<int>(
                          value: selectedClass,
                          decoration: const InputDecoration(labelText: 'Class / Grade', border: OutlineInputBorder()),
                          items: [1, 2, 3, 4, 5]
                              .map((c) => DropdownMenuItem(value: c, child: Text('Class $c')))
                              .toList(),
                          onChanged: (v) => setState(() => selectedClass = v ?? 3),
                        ),
                        const SizedBox(height: 12),
                        DropdownButtonFormField<String>(
                          value: selectedLanguage,
                          decoration: const InputDecoration(labelText: 'Language Preference', border: OutlineInputBorder()),
                          items: ['Santali (English)', 'Santali (Hindi)', 'Hindi', 'English']
                              .map((l) => DropdownMenuItem(value: l, child: Text(l)))
                              .toList(),
                          onChanged: (v) => setState(() => selectedLanguage = v ?? 'Santali (English)'),
                        ),
                        const SizedBox(height: 12),
                      ],
                    ],
                    TextField(
                      controller: idController,
                      decoration: InputDecoration(
                        labelText: isTeacher ? 'Teacher ID / Login ID' : 'Student ID / Login ID',
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: pwdController,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Password',
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    if (errorMessage.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Text(errorMessage, style: const TextStyle(color: Colors.red, fontSize: 13)),
                      ),
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: isTeacher ? const Color(0xFF854D0E) : const Color(0xFF166534),
                          foregroundColor: Colors.white,
                        ),
                        onPressed: isLoading ? null : submitAuth,
                        child: isLoading
                            ? const CircularProgressIndicator(color: Colors.white)
                            : Text(isRegister ? 'Register' : 'Login'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// Teacher Dashboard
class TeacherHomeScreen extends StatefulWidget {
  final Map<String, dynamic> user;
  const TeacherHomeScreen({super.key, required this.user});

  @override
  State<TeacherHomeScreen> createState() => _TeacherHomeScreenState();
}

class _TeacherHomeScreenState extends State<TeacherHomeScreen> {
  Map<String, dynamic> stats = {
    'lessons_prepared': 0,
    'drafts': 0,
    'published': 0,
    'pending_sync': 0
  };

  @override
  void initState() {
    super.initState();
    loadStats();
  }

  Future<void> loadStats() async {
    try {
      final s = await ApiService.getTeacherStats(widget.user['identifier']);
      setState(() {
        stats = s;
      });
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Welcome ${widget.user['name']}'),
        backgroundColor: const Color(0xFF854D0E),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () => Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const AuthScreen())),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            color: const Color(0xFFFEF3C7),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Teacher ID: ${widget.user['identifier']}', style: const TextStyle(fontWeight: FontWeight.bold)),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(color: const Color(0xFFDCFCE7), borderRadius: BorderRadius.circular(12)),
                        child: const Text('Online', style: TextStyle(color: Color(0xFF166534), fontWeight: FontWeight.bold, fontSize: 12)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text('School: ${widget.user['school'] ?? 'Govt Primary School'}'),
                  Text('Language: English (Instruction Mode)'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Text('Statistics', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Row(
            children: [
              _buildStatCard('Lessons Prepared', stats['lessons_prepared'].toString(), const Color(0xFF854D0E)),
              const SizedBox(width: 8),
              _buildStatCard('Drafts', stats['drafts'].toString(), const Color(0xFFD97706)),
              const SizedBox(width: 8),
              _buildStatCard('Published', stats['published'].toString(), const Color(0xFF166534)),
              const SizedBox(width: 8),
              _buildStatCard('Pending Sync', stats['pending_sync'].toString(), const Color(0xFF2563EB)),
            ],
          ),
          const SizedBox(height: 20),
          const Text('Navigation', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          _buildNavTile(Icons.dashboard, 'Dashboard', 'Overview and metrics'),
          _buildNavTile(Icons.menu_book, 'My Lessons', 'View draft and published lessons'),
          _buildNavTile(Icons.add_circle, 'Create Lesson', 'Syllabus-grounded lesson generator'),
          _buildNavTile(Icons.upload_file, 'Upload Content', 'Map documents strictly to J-Guruji'),
          _buildNavTile(Icons.translate, 'Translate', 'English/Hindi to Santali translation'),
          _buildNavTile(Icons.mic, 'Voice Translation', 'Speech-to-text and Santali synthesis'),
          _buildNavTile(Icons.assignment, 'Worksheets', 'Mother-tongue printable worksheets'),
          _buildNavTile(Icons.style, 'Flashcards', 'Bilingual vocabulary cards'),
          _buildNavTile(Icons.smart_toy, 'AI Assistant', 'Grounded quiz and pedagogy assistant'),
          _buildNavTile(Icons.offline_pin, 'Offline Content', 'Manage local cache storage'),
          _buildNavTile(Icons.sync, 'Sync', 'Synchronize with cloud backend'),
          _buildNavTile(Icons.person, 'Profile', 'Update teacher credentials'),
          _buildNavTile(Icons.logout, 'Logout', 'End authenticated session', isLogout: true),
        ],
      ),
    );
  }

  Widget _buildStatCard(String label, String value, Color color) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 6),
          child: Column(
            children: [
              Text(value, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: color)),
              const SizedBox(height: 4),
              Text(label, textAlign: TextAlign.center, style: const TextStyle(fontSize: 11, color: Colors.grey)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildNavTile(IconData icon, String title, String subtitle, {bool isLogout = false}) {
    return ListTile(
      leading: Icon(icon, color: isLogout ? Colors.red : const Color(0xFF854D0E)),
      title: Text(title, style: TextStyle(fontWeight: FontWeight.w600, color: isLogout ? Colors.red : Colors.black87)),
      subtitle: Text(subtitle, style: const TextStyle(fontSize: 12)),
      trailing: const Icon(Icons.chevron_right, size: 18),
      onTap: () {
        if (isLogout) {
          Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const AuthScreen()));
        } else {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Switched to $title')));
        }
      },
    );
  }
}

// Student Dashboard
class StudentHomeScreen extends StatelessWidget {
  final Map<String, dynamic> user;
  const StudentHomeScreen({super.key, required this.user});

  @override
  Widget build(BuildContext context) {
    final cls = user['class_number'] ?? 3;
    final lang = user['preferred_language'] ?? 'Santali (English)';
    final school = user['school'] ?? 'Government Primary School';

    return Scaffold(
      appBar: AppBar(
        title: Text('Welcome ${user['name']}'),
        backgroundColor: const Color(0xFF166534),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () => Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const AuthScreen())),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            color: const Color(0xFFDCFCE7),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Grade: Class $cls', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
                        child: const Text('Online', style: TextStyle(color: Color(0xFF166534), fontWeight: FontWeight.bold, fontSize: 12)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text('School: $school'),
                  Text('Language: $lang'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
          const Text('Your Digital Classroom', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 10,
            crossAxisSpacing: 10,
            childAspectRatio: 2.2,
            children: [
              _buildStudentButton(context, Icons.menu_book, 'Continue Learning', 'Resume active lesson'),
              _buildStudentButton(context, Icons.subject, 'Subjects', 'J-Guruji curriculum'),
              _buildStudentButton(context, Icons.insights, 'Progress', 'Scores & achievements'),
              _buildStudentButton(context, Icons.live_help, 'Ask Doubt', 'AI & voice assistant'),
              _buildStudentButton(context, Icons.download_done, 'Downloads', 'Offline saved lessons'),
              _buildStudentButton(context, Icons.sync, 'Sync', 'Cloud synchronization'),
              _buildStudentButton(context, Icons.person, 'Profile', 'Language & settings'),
              _buildStudentButton(context, Icons.logout, 'Logout', 'Exit safely', isLogout: true),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStudentButton(BuildContext context, IconData icon, String title, String subtitle, {bool isLogout = false}) {
    return InkWell(
      onTap: () {
        if (isLogout) {
          Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const AuthScreen()));
        } else {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Opened $title')));
        }
      },
      borderRadius: BorderRadius.circular(12),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade300),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Row(
          children: [
            Icon(icon, color: isLogout ? Colors.red : const Color(0xFF166534), size: 30),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(title, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: isLogout ? Colors.red : Colors.black87)),
                  Text(subtitle, style: const TextStyle(fontSize: 10, color: Colors.grey), overflow: TextOverflow.ellipsis),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
