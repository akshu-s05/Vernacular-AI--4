import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000';

  static Future<Map<String, dynamic>> loginTeacher(String id, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/teacher/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'identifier': id, 'password': password}),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Login failed');
  }

  static Future<Map<String, dynamic>> registerTeacher(
    String name,
    String school,
    String id,
    String password,
    String preferredLanguage,
  ) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/teacher/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'school': school,
        'teacher_id': id,
        'password': password,
        'preferred_language': preferredLanguage,
      }),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Registration failed');
  }

  static Future<Map<String, dynamic>> loginStudent(String id, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/student/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'identifier': id, 'password': password}),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Login failed');
  }

  static Future<Map<String, dynamic>> registerStudent(
    String name,
    String school,
    String id,
    String password,
    int classNumber,
    String preferredLanguage,
  ) async {
    final res = await http.post(
      Uri.parse('$baseUrl/auth/student/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'school': school,
        'student_id': id,
        'password': password,
        'class_number': classNumber,
        'preferred_language': preferredLanguage,
      }),
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception(jsonDecode(res.body)['detail'] ?? 'Registration failed');
  }

  static Future<Map<String, dynamic>> getCurriculum(int gradeNumber) async {
    final res = await http.get(Uri.parse('$baseUrl/curriculum/$gradeNumber'));
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('Failed to load curriculum for Class $gradeNumber');
  }

  static Future<List<dynamic>> getChapters(int subjectId) async {
    final res = await http.get(Uri.parse('$baseUrl/chapters/$subjectId'));
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('Failed to load chapters');
  }

  static Future<List<dynamic>> getSubtopics(int chapterId) async {
    final res = await http.get(Uri.parse('$baseUrl/subtopics/$chapterId'));
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    throw Exception('Failed to load lessons/subtopics');
  }

  static Future<Map<String, dynamic>> translateText(String text, String src, String tgt) async {
    final res = await http.post(
      Uri.parse('$baseUrl/translate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'text': text, 'source_language': src, 'target_language': tgt}),
    );
    return jsonDecode(res.body);
  }

  static Future<Map<String, dynamic>> getTeacherStats(String identifier) async {
    final res = await http.get(Uri.parse('$baseUrl/teacher/stats?identifier=$identifier'));
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    return {'lessons_prepared': 0, 'drafts': 0, 'published': 0, 'pending_sync': 0};
  }
}
