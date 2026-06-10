import 'package:flutter/material.dart';

import '../../api/digital_buddy_api.dart';
import '../../core/config/app_config.dart';
import '../../core/theme/kmg_theme.dart';
import '../../models/buddy.dart';
import 'buddy_messages.dart';

/// Открывает чат Digital Buddy поверх любого экрана (аналог
/// DigitalBuddyWidget + DigitalBuddyChat на сайте).
Future<void> showBuddyChat(BuildContext context) {
  return showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => const _BuddyChatSheet(),
  );
}

class _ChatMessage {
  final bool fromBuddy;
  final String text;
  final String? source;
  final String? section;

  const _ChatMessage({
    required this.fromBuddy,
    required this.text,
    this.source,
    this.section,
  });
}

class _BuddyChatSheet extends StatefulWidget {
  const _BuddyChatSheet();

  @override
  State<_BuddyChatSheet> createState() => _BuddyChatSheetState();
}

class _BuddyChatSheetState extends State<_BuddyChatSheet> {
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final List<_ChatMessage> _messages = [
    _ChatMessage(fromBuddy: true, text: buddyWelcomeMessages['ru']!),
  ];

  String _language = 'ru';
  bool _isLoading = false;
  BuddyStatus? _status;

  @override
  void initState() {
    super.initState();
    _loadStatus();
  }

  Future<void> _loadStatus() async {
    try {
      final status = await digitalBuddyApi.getStatus();
      if (mounted) {
        setState(() => _status = status);
      }
    } catch (_) {
      // Статус LLM не критичен для чата.
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 250),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _send() async {
    final question = _controller.text.trim();
    if (question.isEmpty || _isLoading) {
      return;
    }

    final language = detectClientLanguage(question);

    setState(() {
      _language = language;
      _messages.add(_ChatMessage(fromBuddy: false, text: question));
      _isLoading = true;
    });
    _controller.clear();
    _scrollToBottom();

    try {
      final answer = await digitalBuddyApi.askQuestion(
        AppConfig.demoEmployeeId,
        question,
        language: language,
      );

      if (!mounted) return;
      setState(() {
        _messages.add(_ChatMessage(
          fromBuddy: true,
          text: answer.answer,
          source: answer.source ?? answer.documentCode,
          section: answer.section,
        ));
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _messages.add(_ChatMessage(
          fromBuddy: true,
          text: buddyErrorMessages[_language]!,
        ));
      });
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
        _scrollToBottom();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      expand: false,
      builder: (context, _) {
        return Container(
          decoration: const BoxDecoration(
            color: KmgColors.gray50,
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          padding: EdgeInsets.only(bottom: bottomInset),
          child: Column(
            children: [
              _buildHeader(),
              Expanded(
                child: ListView.separated(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: _messages.length + (_isLoading ? 1 : 0),
                  separatorBuilder: (_, _) => const SizedBox(height: 10),
                  itemBuilder: (context, index) {
                    if (index == _messages.length) {
                      return _buildLoadingBubble();
                    }
                    return _buildMessageBubble(_messages[index]);
                  },
                ),
              ),
              _buildInputBar(),
            ],
          ),
        );
      },
    );
  }

  Widget _buildHeader() {
    final status = _status;
    final statusText = status == null
        ? null
        : status.modelReady
            ? 'Локальная модель: ${status.llmModel}'
            : buddySubtitle[_language];

    return Container(
      padding: const EdgeInsets.fromLTRB(20, 14, 12, 14),
      decoration: const BoxDecoration(
        color: KmgColors.navy800,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Row(
        children: [
          const CircleAvatar(
            backgroundColor: KmgColors.green500,
            child: Icon(Icons.smart_toy_outlined, color: KmgColors.white),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  buddyName,
                  style: TextStyle(
                    color: KmgColors.white,
                    fontWeight: FontWeight.w700,
                    fontSize: 16,
                  ),
                ),
                Text(
                  statusText ?? buddySubtitle[_language]!,
                  style: const TextStyle(
                    color: KmgColors.green300,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, color: KmgColors.white),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(_ChatMessage message) {
    final isBuddy = message.fromBuddy;

    return Align(
      alignment: isBuddy ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 320),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: isBuddy ? KmgColors.white : KmgColors.green600,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isBuddy ? 4 : 16),
            bottomRight: Radius.circular(isBuddy ? 16 : 4),
          ),
          border: isBuddy ? Border.all(color: KmgColors.gray200) : null,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              message.text,
              style: TextStyle(
                color: isBuddy ? KmgColors.gray800 : KmgColors.white,
                fontSize: 14,
                height: 1.45,
              ),
            ),
            if (message.source != null) ...[
              const SizedBox(height: 8),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: KmgColors.green100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  message.section != null
                      ? 'Источник: ${message.source} · ${message.section}'
                      : 'Источник: ${message.source}',
                  style: const TextStyle(
                    fontSize: 11.5,
                    color: KmgColors.green800,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildLoadingBubble() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: KmgColors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: KmgColors.gray200),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            ),
            const SizedBox(width: 10),
            Text(
              buddyLoadingMessages[_language]!,
              style: const TextStyle(fontSize: 13, color: KmgColors.gray600),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
      decoration: const BoxDecoration(
        color: KmgColors.white,
        border: Border(top: BorderSide(color: KmgColors.gray200)),
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                minLines: 1,
                maxLines: 4,
                textInputAction: TextInputAction.send,
                onSubmitted: (_) => _send(),
                decoration: InputDecoration(
                  hintText: buddyInputPlaceholders[_language],
                  filled: true,
                  fillColor: KmgColors.gray100,
                  contentPadding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 10),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            IconButton.filled(
              onPressed: _isLoading ? null : _send,
              style: IconButton.styleFrom(
                backgroundColor: KmgColors.green600,
                foregroundColor: KmgColors.white,
              ),
              icon: const Icon(Icons.send),
            ),
          ],
        ),
      ),
    );
  }
}
