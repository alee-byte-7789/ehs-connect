/**
 * Types mirroring backend/app/schemas/*.py and backend/app/models/enums.py.
 * Keep these in lockstep with the backend contracts — this is the single
 * source of truth for what the mobile app expects the API to send/accept.
 */

export type ResidentType = "owner" | "tenant";
export type VerificationStatus = "pending" | "approved" | "rejected";

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

export interface RegisterRequest {
  full_name: string;
  house_number: string;
  mobile_number: string;
  email?: string;
  password: string;
  is_awc_employee: boolean;
  employee_number?: string;
  is_tenant?: boolean;
  owner_house_number?: string;
  owner_name?: string;
  owner_cnic?: string;
  owner_mobile_number?: string;
}

export interface RegisterResponse {
  message: string;
  resident_id: number;
  verification_status: VerificationStatus;
}

export interface LoginRequest {
  identifier: string;
  password: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ApiErrorBody {
  detail?: string | { msg: string }[];
}
