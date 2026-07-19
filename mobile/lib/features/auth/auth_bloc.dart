import 'package:flutter_bloc/flutter_bloc.dart';
import 'auth_repository.dart';

abstract class AuthEvent {}
class LoginRequested extends AuthEvent {
  final String email;
  final String password;
  LoginRequested(this.email, this.password);
}
class LogoutRequested extends AuthEvent {}
class AppStarted extends AuthEvent {}

abstract class AuthState {}
class AuthInitial extends AuthState {}
class AuthLoading extends AuthState {}
class Authenticated extends AuthState {}
class Unauthenticated extends AuthState {}
class AuthFailure extends AuthState {
  final String message;
  AuthFailure(this.message);
}

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository authRepository;

  AuthBloc(this.authRepository) : super(AuthInitial()) {
    on<AppStarted>((event, emit) async {
      final isAuthed = await authRepository.isAuthenticated();
      if (isAuthed) {
        emit(Authenticated());
      } else {
        emit(Unauthenticated());
      }
    });

    on<LoginRequested>((event, emit) async {
      emit(AuthLoading());
      final success = await authRepository.login(event.email, event.password);
      if (success) {
        emit(Authenticated());
      } else {
        emit(AuthFailure('Invalid credentials'));
      }
    });

    on<LogoutRequested>((event, emit) async {
      emit(AuthLoading());
      await authRepository.logout();
      emit(Unauthenticated());
    });
  }
}
