import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'core/theme/kmg_theme.dart';
import 'features/adaptation/adaptation_screen.dart';
import 'features/engagement/engagement_screen.dart';
import 'features/home/home_screen.dart';
import 'features/introduction/introduction_screen.dart';
import 'features/retention/retention_screen.dart';

final _router = GoRouter(
  routes: [
    GoRoute(path: '/', builder: (_, _) => const HomeScreen()),
    GoRoute(
        path: '/introduction',
        builder: (_, _) => const IntroductionScreen()),
    GoRoute(
        path: '/engagement', builder: (_, _) => const EngagementScreen()),
    GoRoute(
        path: '/adaptation', builder: (_, _) => const AdaptationScreen()),
    GoRoute(path: '/retention', builder: (_, _) => const RetentionScreen()),
  ],
);

class KmgApp extends StatelessWidget {
  const KmgApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'KMG Digital Onboarding',
      debugShowCheckedModeBanner: false,
      theme: buildKmgTheme(),
      routerConfig: _router,
    );
  }
}
