import '../core/network/api_client.dart';
import '../models/survey.dart';

/// Порт src/api/surveyApi.ts.
class SurveyApi {
  const SurveyApi();

  Future<SurveySummary> getSummary(int employeeId) async {
    final response = await apiClient.get('/surveys/employees/$employeeId/summary');
    return SurveySummary.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> createSurvey(int employeeId, SurveyCreatePayload payload) async {
    await apiClient.post(
      '/surveys/employees/$employeeId',
      data: payload.toJson(),
    );
  }
}

const surveyApi = SurveyApi();
