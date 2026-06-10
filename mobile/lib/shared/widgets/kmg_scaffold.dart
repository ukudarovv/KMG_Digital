import 'package:flutter/material.dart';

import '../../features/digital_buddy/buddy_chat_sheet.dart';

/// Scaffold с плавающей кнопкой Digital Buddy — ассистент доступен
/// на всех экранах, как на сайте.
class KmgScaffold extends StatelessWidget {
  final PreferredSizeWidget? appBar;
  final Widget body;

  const KmgScaffold({super.key, this.appBar, required this.body});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: appBar,
      body: body,
      floatingActionButton: FloatingActionButton.extended(
        heroTag: null,
        onPressed: () => showBuddyChat(context),
        icon: const Icon(Icons.smart_toy_outlined),
        label: const Text('Buddy'),
      ),
    );
  }
}
