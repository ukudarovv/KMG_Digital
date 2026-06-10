import 'package:flutter_test/flutter_test.dart';

import 'package:kmg_mobile/features/digital_buddy/buddy_messages.dart';

void main() {
  group('detectClientLanguage', () {
    test('распознаёт казахский по специфичным символам', () {
      expect(detectClientLanguage('Қауіпсіздік ережелері қандай?'), 'kk');
    });

    test('распознаёт казахский по словам', () {
      expect(detectClientLanguage('рахмет'), 'kk');
    });

    test('по умолчанию русский', () {
      expect(detectClientLanguage('Какие правила пропускного режима?'), 'ru');
    });
  });
}
