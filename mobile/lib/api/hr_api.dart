import '../core/network/api_client.dart';
import '../models/hr_detail.dart';

/// Только getEmployeeDetail из src/api/hrApi.ts — для экрана «Закрепление».
class HrApi {
  const HrApi();

  Future<HrEmployeeDetail> getEmployeeDetail(int employeeId) async {
    final response = await apiClient.get('/hr/employees/$employeeId/detail');
    return HrEmployeeDetail.fromJson(response.data as Map<String, dynamic>);
  }
}

const hrApi = HrApi();
