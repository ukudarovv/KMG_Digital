import { BrowserRouter, Navigate, Route, Routes, useParams } from "react-router-dom";
import { Layout } from "./components/Layout/Layout";
import { HRAdminLayout } from "./components/HRAdminLayout/HRAdminLayout";
import { HomePage } from "./pages/HomePage";
import { IntroductionPage } from "./pages/IntroductionPage";
import { EngagementPage } from "./pages/EngagementPage";
import { AdaptationPage } from "./pages/AdaptationPage";
import { RetentionPage } from "./pages/RetentionPage";
import { HRDashboardPage } from "./pages/HRDashboardPage";
import { EmployeeDetailPage } from "./pages/EmployeeDetailPage";
import { EmployeesListPage } from "./pages/hr/EmployeesListPage";
import { EmployeeFormPage } from "./pages/hr/EmployeeFormPage";
import { DocumentsListPage } from "./pages/hr/DocumentsListPage";
import { DocumentNewPage } from "./pages/hr/DocumentNewPage";
import { DocumentDetailPage } from "./pages/hr/DocumentDetailPage";
import { RecruitingListPage } from "./pages/hr/RecruitingListPage";
import { RecruitingAnalyzePage } from "./pages/hr/RecruitingAnalyzePage";
import { RecruitingCandidatePage } from "./pages/hr/RecruitingCandidatePage";
import { HRSettingsPage } from "./pages/hr/HRSettingsPage";

function LegacyEmployeeRedirect() {
  const { id } = useParams();
  return <Navigate to={`/hr/employees/${id}`} replace />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/hr/*"
          element={
            <HRAdminLayout>
              <Routes>
                <Route index element={<HRDashboardPage />} />
                <Route path="employees" element={<EmployeesListPage />} />
                <Route path="employees/new" element={<EmployeeFormPage />} />
                <Route
                  path="employees/:id/edit"
                  element={<EmployeeFormPage />}
                />
                <Route path="employees/:id" element={<EmployeeDetailPage />} />
                <Route path="documents" element={<DocumentsListPage />} />
                <Route path="documents/new" element={<DocumentNewPage />} />
                <Route path="documents/:id" element={<DocumentDetailPage />} />
                <Route path="recruiting" element={<RecruitingListPage />} />
                <Route
                  path="recruiting/analyze"
                  element={<RecruitingAnalyzePage />}
                />
                <Route
                  path="recruiting/candidates/:id"
                  element={<RecruitingCandidatePage />}
                />
                <Route path="settings" element={<HRSettingsPage />} />
              </Routes>
            </HRAdminLayout>
          }
        />

        <Route path="/hr-dashboard" element={<Navigate to="/hr" replace />} />
        <Route
          path="/hr-dashboard/employee/:id"
          element={<LegacyEmployeeRedirect />}
        />

        <Route
          path="/*"
          element={
            <Layout>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/introduction" element={<IntroductionPage />} />
                <Route path="/engagement" element={<EngagementPage />} />
                <Route path="/adaptation" element={<AdaptationPage />} />
                <Route path="/retention" element={<RetentionPage />} />
              </Routes>
            </Layout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
