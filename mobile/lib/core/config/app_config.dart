import 'dart:io' show Platform;

import 'package:flutter/foundation.dart' show kIsWeb, kReleaseMode;

/// Конфигурация API. URL можно переопределить при сборке:
/// flutter run --dart-define=API_URL=https://api.kmg.aqlant.com/api
class AppConfig {
  static const String _envApiUrl = String.fromEnvironment('API_URL');

  /// Продакшн-API (домен указывает на 194.32.141.90).
  static const String productionApiUrl = 'https://api.kmg.aqlant.com/api';

  /// Release-сборка по умолчанию ходит на продакшн-домен.
  /// Debug: Android-эмулятор видит хост-машину как 10.0.2.2,
  /// iOS-симулятор и desktop — как 127.0.0.1.
  static String get apiBaseUrl {
    if (_envApiUrl.isNotEmpty) {
      return _envApiUrl;
    }

    if (kReleaseMode) {
      return productionApiUrl;
    }

    // Web в Chrome: localhost и 127.0.0.1 — разные origin для CORS.
    if (kIsWeb) {
      return 'http://localhost:8010/api';
    }

    if (Platform.isAndroid) {
      return 'http://10.0.2.2:8010/api';
    }

    return 'http://127.0.0.1:8010/api';
  }

  /// Демо-сотрудник (как EMPLOYEE_ID = 1 на сайте).
  static const int demoEmployeeId = 1;
}
