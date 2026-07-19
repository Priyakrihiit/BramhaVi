import 'package:flutter/material.dart';
import 'course_repository.dart';

class CourseExplorerScreen extends StatefulWidget {
  final CourseRepository courseRepository;

  const CourseExplorerScreen({super.key, required this.courseRepository});

  @override
  State<CourseExplorerScreen> createState() => _CourseExplorerScreenState();
}

class _CourseExplorerScreenState extends State<CourseExplorerScreen> {
  late Future<List<Course>> _coursesFuture;

  @override
  void initState() {
    super.initState();
    _coursesFuture = widget.courseRepository.fetchCourses();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Explore Courses'),
      ),
      body: FutureBuilder<List<Course>>(
        future: _coursesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return const Center(child: Text('Error loading courses.'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No courses found.'));
          }

          final courses = snapshot.data!;
          return ListView.builder(
            itemCount: courses.length,
            itemBuilder: (context, index) {
              final course = courses[index];
              return ListTile(
                title: Text(course.title),
                subtitle: Text(course.slug),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {
                  // Navigate to details screen
                },
              );
            },
          );
        },
      ),
    );
  }
}
