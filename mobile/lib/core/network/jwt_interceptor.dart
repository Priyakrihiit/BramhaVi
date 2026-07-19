import 'package:dio/ dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class JwtInterceptor extends Interceptor {
  final _storage = const FlutterSecureStorage();

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _storage.read(key: 'access_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    return super.onRequest(options, handler);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Logic for dynamic token refreshes can be integrated here.
    }
    return super.onError(err, handler);
  }
}
