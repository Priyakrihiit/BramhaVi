import 'package:dio/dio.dart';
import 'jwt_interceptor.dart';

class ApiClient {
  late final Dio dio;

  ApiClient({String baseUrl = 'http://127.0.0.1:8000/api/v1/'}) {
    dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );
    dio.interceptors.add(JwtInterceptor());
    dio.interceptors.add(LogInterceptor(requestBody: true, responseBody: true));
  }
}
