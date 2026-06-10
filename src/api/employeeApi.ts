import { httpClient } from "./httpClient";

export type Department = {
  id: number;
  code: string;
  name: string;
  description?: string | null;
  competencies?: string | null;
  is_active: boolean;
};

export type DepartmentPayload = {
  code: string;
  name: string;
  description?: string | null;
  competencies?: string | null;
  is_active?: boolean;
};

export type Employee = {
  id: number;
  bitrix_user_id?: number | null;
  full_name: string;
  email?: string | null;
  position?: string | null;
  department?: string | null;
  department_id?: number | null;
  candidate_id?: number | null;
  manager_name?: string | null;
  start_date: string;
  language: string;
  status: string;
};

export type EmployeePayload = {
  bitrix_user_id?: number | null;
  full_name: string;
  email?: string | null;
  position?: string | null;
  department_id?: number | null;
  manager_name?: string | null;
  start_date: string;
  language?: string;
  status?: string;
};

export const employeeApi = {
  async getAll() {
    const response = await httpClient.get<Employee[]>("/employees");
    return response.data;
  },

  async getById(employeeId: number) {
    const response = await httpClient.get<Employee>(`/employees/${employeeId}`);
    return response.data;
  },

  async create(payload: EmployeePayload) {
    const response = await httpClient.post<Employee>("/hr/employees", payload);
    return response.data;
  },

  async update(employeeId: number, payload: Partial<EmployeePayload>) {
    const response = await httpClient.patch<Employee>(
      `/hr/employees/${employeeId}`,
      payload
    );
    return response.data;
  },

  async getDepartments() {
    const response = await httpClient.get<Department[]>("/hr/departments");
    return response.data;
  },

  async createDepartment(payload: DepartmentPayload) {
    const response = await httpClient.post<Department>(
      "/hr/departments",
      payload
    );
    return response.data;
  },

  async updateDepartment(
    departmentId: number,
    payload: Partial<DepartmentPayload>
  ) {
    const response = await httpClient.patch<Department>(
      `/hr/departments/${departmentId}`,
      payload
    );
    return response.data;
  },
};
