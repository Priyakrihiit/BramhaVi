import 'package:dio/dio.dart';

class Course {
  final String id;
  final String title;
  final String slug;

  Course({required this.id, required this.title, required this.slug});

  factory Course.fromJson(Map<String, dynamic> json) {
    return Course(
      id: json['id'],
      title: json['title'],
      slug: json['slug'],
    );
  }
}

class CourseRepository {
  final Dio _dio;

  CourseRepository(this._dio);

  Future<List<Course>> fetchCourses() async {
    try {
      final response = await _dio.get('lms/courses/');
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => Course.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      return [];
    }
  }
}
