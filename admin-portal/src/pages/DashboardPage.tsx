import { useState } from "react";

import { Button } from "../components/Button";
import { StatusBadge } from "../components/StatusBadge";
import { useAuth } from "../lib/auth-context";
import { useAdminMe } from "../lib/registration-queries";
import {
  useApproveRegistration,
  usePendingRegistrations,
  useRejectRegistration,
} from "../lib/registration-queries";
import { extractApiErrorMessage } from "../lib/api-client";

export function DashboardPage() {
  const { logout } = useAuth();
  const { data: admin } = useAdminMe(true);
  const { data: pending, isLoading, isError } = usePendingRegistrations();
  const approve = useApproveRegistration();
  const reject = useRejectRegistration();
  const [actionError, setActionError] = useState<string | null>(null);
  const [actingOn, setActingOn] = useState<number | null>(null);

  const handleApprove = async (residentId: number) => {
    setActionError(null);
    setActingOn(residentId);
    try {
      await approve.mutateAsync(residentId);
    } catch (err) {
      setActionError(extractApiErrorMessage(err, "Could not approve this registration."));
    } finally {
      setActingOn(null);
    }
  };

  const handleReject = async (residentId: number) => {
    setActionError(null);
    setActingOn(residentId);
    try {
      await reject.mutateAsync(residentId);
    } catch (err) {
      setActionError(extractApiErrorMessage(err, "Could not reject this registration."));
    } finally {
      setActingOn(null);
    }
  };

  return (
    <div className="min-h-screen bg-[color:var(--color-surface)]">
      <header className="flex items-center justify-between border-b border-[color:var(--color-border)] bg-white px-6 py-4">
        <div>
          <h1 className="text-lg font-semibold text-[color:var(--color-text-primary)]">EHS Connect Admin</h1>
          {admin && (
            <p className="text-xs text-[color:var(--color-text-secondary)]">
              {admin.full_name} · {admin.role.replace("_", " ")}
            </p>
          )}
        </div>
        <Button variant="secondary" onClick={logout}>
          Log out
        </Button>
      </header>

      <main className="mx-auto max-w-4xl px-6 py-8">
        <h2 className="mb-4 text-base font-semibold text-[color:var(--color-text-primary)]">
          Pending Registrations
        </h2>

        {actionError && (
          <p className="mb-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-[color:var(--color-danger)]">
            {actionError}
          </p>
        )}

        {isLoading && <p className="text-sm text-[color:var(--color-text-secondary)]">Loading...</p>}
        {isError && (
          <p className="text-sm text-[color:var(--color-danger)]">
            Could not load pending registrations. Your session may have expired — try logging in again.
          </p>
        )}

        {pending && pending.length === 0 && (
          <p className="text-sm text-[color:var(--color-text-secondary)]">
            No pending registrations right now — all caught up.
          </p>
        )}

        {pending && pending.length > 0 && (
          <div className="overflow-hidden rounded-xl border border-[color:var(--color-border)] bg-white">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-[color:var(--color-border)] bg-[color:var(--color-surface)] text-xs uppercase text-[color:var(--color-text-secondary)]">
                <tr>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Phone</th>
                  <th className="px-4 py-3">Type</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {pending.map((resident) => (
                  <tr key={resident.id} className="border-b border-[color:var(--color-border)] last:border-0">
                    <td className="px-4 py-3 font-medium text-[color:var(--color-text-primary)]">
                      {resident.full_name}
                    </td>
                    <td className="px-4 py-3 text-[color:var(--color-text-secondary)]">{resident.phone}</td>
                    <td className="px-4 py-3 text-[color:var(--color-text-secondary)] capitalize">
                      {resident.resident_type}
                      {resident.is_employee && " · Employee"}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={resident.verification_status} />
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-2">
                        <Button
                          variant="primary"
                          className="!px-3 !py-1.5 text-xs"
                          loading={actingOn === resident.id && approve.isPending}
                          disabled={actingOn !== null}
                          onClick={() => handleApprove(resident.id)}
                        >
                          Approve
                        </Button>
                        <Button
                          variant="danger"
                          className="!px-3 !py-1.5 text-xs"
                          loading={actingOn === resident.id && reject.isPending}
                          disabled={actingOn !== null}
                          onClick={() => handleReject(resident.id)}
                        >
                          Reject
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
