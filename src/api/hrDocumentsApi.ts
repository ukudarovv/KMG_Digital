import { httpClient } from "./httpClient";

export type HrDocumentStatus =
  | "draft"
  | "in_review"
  | "approved"
  | "rejected"
  | "signed"
  | "archived";

export type HrDocument = {
  id: number;
  title: string;
  doc_type: string;
  status: HrDocumentStatus;
  current_version_no: number;
  owner_employee_id?: number | null;
  owner_employee_name?: string | null;
  created_at: string;
  updated_at: string;
};

export type HrDocumentVersion = {
  id: number;
  version_no: number;
  file_name: string;
  uploaded_by?: string | null;
  comment?: string | null;
  created_at: string;
};

export type HrWorkflowStep = {
  id: number;
  step_order: number;
  role: string;
  approver_name?: string | null;
};

export type HrWorkflow = {
  id: number;
  name: string;
  description?: string | null;
  is_active: boolean;
  steps: HrWorkflowStep[];
};

export type HrApproval = {
  id: number;
  step_order: number;
  decision: "approved" | "rejected" | "signed";
  actor?: string | null;
  comment?: string | null;
  created_at: string;
};

export type HrDocumentDetail = HrDocument & {
  versions: HrDocumentVersion[];
  workflow_name?: string | null;
  current_step_order?: number | null;
  current_step_role?: string | null;
  workflow_steps: HrWorkflowStep[];
  approvals: HrApproval[];
};

export type DecisionPayload = {
  actor?: string;
  comment?: string;
};

export const hrDocumentsApi = {
  async getAll(filters?: { status?: string; employee_id?: number }) {
    const response = await httpClient.get<HrDocument[]>("/hr/documents", {
      params: filters,
    });
    return response.data;
  },

  async getById(documentId: number) {
    const response = await httpClient.get<HrDocumentDetail>(
      `/hr/documents/${documentId}`
    );
    return response.data;
  },

  async create(params: {
    title: string;
    doc_type: string;
    owner_employee_id?: number | null;
    uploaded_by?: string;
    comment?: string;
    file: File;
  }) {
    const formData = new FormData();
    formData.append("title", params.title);
    formData.append("doc_type", params.doc_type);
    if (params.owner_employee_id) {
      formData.append("owner_employee_id", String(params.owner_employee_id));
    }
    if (params.uploaded_by) {
      formData.append("uploaded_by", params.uploaded_by);
    }
    if (params.comment) {
      formData.append("comment", params.comment);
    }
    formData.append("file", params.file);

    const response = await httpClient.post<HrDocumentDetail>(
      "/hr/documents",
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return response.data;
  },

  async addVersion(
    documentId: number,
    params: { file: File; uploaded_by?: string; comment?: string }
  ) {
    const formData = new FormData();
    if (params.uploaded_by) {
      formData.append("uploaded_by", params.uploaded_by);
    }
    if (params.comment) {
      formData.append("comment", params.comment);
    }
    formData.append("file", params.file);

    const response = await httpClient.post<HrDocumentDetail>(
      `/hr/documents/${documentId}/versions`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return response.data;
  },

  fileUrl(documentId: number, versionNo: number) {
    const base =
      import.meta.env.VITE_API_URL || "http://127.0.0.1:8010/api";
    return `${base}/hr/documents/${documentId}/versions/${versionNo}/file`;
  },

  async submit(documentId: number, workflowId: number) {
    const response = await httpClient.post<HrDocumentDetail>(
      `/hr/documents/${documentId}/submit`,
      { workflow_id: workflowId }
    );
    return response.data;
  },

  async approve(documentId: number, payload: DecisionPayload) {
    const response = await httpClient.post<HrDocumentDetail>(
      `/hr/documents/${documentId}/approve`,
      payload
    );
    return response.data;
  },

  async reject(documentId: number, payload: DecisionPayload) {
    const response = await httpClient.post<HrDocumentDetail>(
      `/hr/documents/${documentId}/reject`,
      payload
    );
    return response.data;
  },

  async sign(documentId: number, payload: DecisionPayload) {
    const response = await httpClient.post<HrDocumentDetail>(
      `/hr/documents/${documentId}/sign`,
      payload
    );
    return response.data;
  },

  async archive(documentId: number) {
    const response = await httpClient.post<HrDocumentDetail>(
      `/hr/documents/${documentId}/archive`
    );
    return response.data;
  },

  async getWorkflows() {
    const response = await httpClient.get<HrWorkflow[]>(
      "/hr/documents/workflows"
    );
    return response.data;
  },

  async createWorkflow(payload: {
    name: string;
    description?: string;
    steps: { step_order: number; role: string; approver_name?: string }[];
  }) {
    const response = await httpClient.post<HrWorkflow>(
      "/hr/documents/workflows",
      payload
    );
    return response.data;
  },
};
