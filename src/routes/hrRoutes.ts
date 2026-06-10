export const HR_ROUTES = {
  dashboard: "/hr",
  employees: "/hr/employees",
  employeeNew: "/hr/employees/new",
  employee: (id: number | string) => `/hr/employees/${id}`,
  employeeEdit: (id: number | string) => `/hr/employees/${id}/edit`,
  documents: "/hr/documents",
  documentNew: "/hr/documents/new",
  document: (id: number | string) => `/hr/documents/${id}`,
  recruiting: "/hr/recruiting",
  recruitingAnalyze: "/hr/recruiting/analyze",
  candidate: (id: number | string) => `/hr/recruiting/candidates/${id}`,
  settings: "/hr/settings",
} as const;
