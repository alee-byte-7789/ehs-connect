/**
 * Types mirroring backend/app/schemas/*.py and backend/app/models/enums.py.
 * Same source of truth as mobile-app/lib/types.ts — keep all three in sync.
 */

export type ResidentType = "owner" | "tenant";
export type VerificationStatus = "pending" | "approved" | "rejected";
export type AdminRole = "housing_office" | "it_admin" | "super_admin";

export interface ResidentOut {
  id: number;
  resident_code: string | null;
  house_id: number;
  full_name: string;
  phone: string;
  email: string | null;
  resident_type: ResidentType;
  is_employee: boolean;
  employee_number: string | null;
  verification_status: VerificationStatus;
  created_at: string;
}

export interface AdminOut {
  id: number;
  full_name: string;
  email: string;
  role: AdminRole;
  created_at: string;
}

export interface AdminLoginRequest {
  email: string;
  password: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegistrationApprovedOut {
  message: string;
  resident: ResidentOut;
}

export interface RegistrationRejectedOut {
  message: string;
  resident_id: number;
}
