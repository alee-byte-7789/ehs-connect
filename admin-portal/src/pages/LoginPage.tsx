import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { Button } from "../components/Button";
import { extractApiErrorMessage } from "../lib/api-client";
import { useAuth } from "../lib/auth-context";

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Enter your password"),
});

type FormValues = z.infer<typeof schema>;

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (values: FormValues) => {
    setServerError(null);
    setSubmitting(true);
    try {
      await login(values);
      navigate("/", { replace: true });
    } catch (err) {
      setServerError(extractApiErrorMessage(err, "Login failed. Check your credentials."));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[color:var(--color-surface)] px-4">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="w-full max-w-sm rounded-2xl border border-[color:var(--color-border)] bg-white p-8 shadow-sm"
      >
        <h1 className="mb-1 text-2xl font-semibold text-[color:var(--color-text-primary)]">EHS Connect</h1>
        <p className="mb-6 text-sm text-[color:var(--color-text-secondary)]">Housing Office Admin Portal</p>

        <label className="mb-1 block text-sm font-medium text-[color:var(--color-text-secondary)]">Email</label>
        <Controller
          control={control}
          name="email"
          render={({ field }) => (
            <input
              {...field}
              type="email"
              autoComplete="username"
              className="mb-1 w-full rounded-lg border border-[color:var(--color-border)] px-3 py-2 text-sm outline-none focus:border-[color:var(--color-primary)]"
            />
          )}
        />
        {errors.email && <p className="mb-3 text-xs text-[color:var(--color-danger)]">{errors.email.message}</p>}

        <label className="mb-1 mt-3 block text-sm font-medium text-[color:var(--color-text-secondary)]">Password</label>
        <Controller
          control={control}
          name="password"
          render={({ field }) => (
            <input
              {...field}
              type="password"
              autoComplete="current-password"
              className="mb-1 w-full rounded-lg border border-[color:var(--color-border)] px-3 py-2 text-sm outline-none focus:border-[color:var(--color-primary)]"
            />
          )}
        />
        {errors.password && <p className="mb-3 text-xs text-[color:var(--color-danger)]">{errors.password.message}</p>}

        {serverError && <p className="mb-3 text-center text-sm text-[color:var(--color-danger)]">{serverError}</p>}

        <Button type="submit" className="mt-4 w-full" loading={submitting}>
          Log in
        </Button>
      </form>
    </div>
  );
}
