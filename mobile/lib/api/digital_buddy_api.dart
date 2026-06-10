import '../core/network/api_client.dart';
import '../models/buddy.dart';

/// Порт src/api/digitalBuddyApi.ts.
class DigitalBuddyApi {
  const DigitalBuddyApi();

  Future<BuddyStatus> getStatus() async {
    final response = await apiClient.get('/digital-buddy/status');
    return BuddyStatus.fromJson(response.data as Map<String, dynamic>);
  }

  Future<BuddyAnswer> askQuestion(
    int employeeId,
    String question, {
    String? language,
  }) async {
    final response = await apiClient.post(
      '/digital-buddy/ask',
      data: {
        'employee_id': employeeId,
        'question': question,
        'language': ?language,
      },
    );
    return BuddyAnswer.fromJson(response.data as Map<String, dynamic>);
  }
}

const digitalBuddyApi = DigitalBuddyApi();
