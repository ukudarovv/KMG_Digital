import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Палитра KMG — перенесена из src/styles/variables.css веб-версии.
abstract class KmgColors {
  static const green900 = Color(0xFF032B1D);
  static const green800 = Color(0xFF064C2E);
  static const green700 = Color(0xFF0A582F);
  static const green600 = Color(0xFF0B6B38);
  static const green500 = Color(0xFF0F7A3F);
  static const green400 = Color(0xFF1A9D55);
  static const green300 = Color(0xFF7CE0A2);
  static const green100 = Color(0xFFE8F7EE);

  static const navy900 = Color(0xFF041525);
  static const navy800 = Color(0xFF071F35);
  static const navy700 = Color(0xFF0C2D4A);
  static const navy600 = Color(0xFF1A3D5C);

  static const white = Color(0xFFFFFFFF);
  static const gray50 = Color(0xFFF8FAFC);
  static const gray100 = Color(0xFFF1F5F9);
  static const gray200 = Color(0xFFE2E8F0);
  static const gray400 = Color(0xFF94A3B8);
  static const gray600 = Color(0xFF475569);
  static const gray800 = Color(0xFF1E293B);

  static const danger = Color(0xFFDC2626);
  static const warning = Color(0xFFD97706);
}

ThemeData buildKmgTheme() {
  final base = ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: KmgColors.green600,
      primary: KmgColors.green600,
      secondary: KmgColors.navy800,
      surface: KmgColors.gray50,
    ),
    scaffoldBackgroundColor: KmgColors.gray50,
  );

  return base.copyWith(
    textTheme: GoogleFonts.interTextTheme(base.textTheme),
    appBarTheme: const AppBarTheme(
      backgroundColor: KmgColors.navy800,
      foregroundColor: KmgColors.white,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: KmgColors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: KmgColors.gray200),
      ),
      margin: EdgeInsets.zero,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: KmgColors.green600,
        foregroundColor: KmgColors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: KmgColors.green700,
        side: const BorderSide(color: KmgColors.green600),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
      ),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: KmgColors.green600,
      foregroundColor: KmgColors.white,
    ),
    chipTheme: base.chipTheme.copyWith(
      backgroundColor: KmgColors.green100,
      labelStyle: const TextStyle(color: KmgColors.green800),
    ),
  );
}
