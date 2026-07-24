import { zodResolver } from "@hookform/resolvers/zod";
import { router } from "expo-router";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { z } from "zod";

import { AppButton } from "../components/AppButton";
import { AppTextField } from "../components/AppTextField";
import { ScreenContainer } from "../components/ScreenContainer";
import { extractApiErrorMessage } from "../lib/api-client";
import { useAuth } from "../lib/auth-context";
import { radii, spacing } from "../lib/theme";
import { useTheme } from "../lib/use-theme";

/**
 * Mirrors backend/app/schemas/auth.py's RegisterRequest validator exactly:
 * - is_awc_employee=true requires employee_number
 * - is_tenant=true requires all four owner_* fields
 * These two questions are independent — an AWC employee can also be a
 * tenant (e.g. an employee who rents rather than owns). Both questions are
 * always asked; the fields shown depend on each answer independently, not
 * on each other.
 */
const schema = z
  .object({
    full_name: z.string().min(2, "Enter your full name"),
    house_number: z.string().min(1, "Enter your house number, e.g. B-026"),
    mobile_number: z.string().min(7, "Enter a valid mobile number"),
    email: z.string().email("Enter a valid email").optional().or(z.literal("")),
    password: z.string().min(8, "At least 8 characters"),
    is_awc_employee: z.boolean(),
    employee_number: z.string().optional(),
    is_tenant: z.boolean(),
    owner_house_number: z.string().optional(),
    owner_name: z.string().optional(),
    owner_cnic: z.string().optional(),
    owner_mobile_number: z.string().optional(),
  })
  .superRefine((values, ctx) => {
    if (values.is_awc_employee && !values.employee_number?.trim()) {
      ctx.addIssue({ code: "custom", path: ["employee_number"], message: "Employee number is required" });
    }
    if (values.is_tenant) {
      (["owner_house_number", "owner_name", "owner_cnic", "owner_mobile_number"] as const).forEach((field) => {
        if (!values[field]?.trim()) {
          ctx.addIssue({ code: "custom", path: [field], message: "Required" });
        }
      });
    }
  });

type FormValues = z.infer<typeof schema>;

const STEP_LABELS = ["Basic info", "Employment / tenancy", "Review"];

export default function RegisterScreen() {
  const { register: registerResident } = useAuth();
  const theme = useTheme();
  const [step, setStep] = useState(0);
  const [serverError, setServerError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const {
    control,
    handleSubmit,
    trigger,
    watch,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      full_name: "",
      house_number: "",
      mobile_number: "",
      email: "",
      password: "",
      is_awc_employee: false,
      employee_number: "",
      is_tenant: false,
      owner_house_number: "",
      owner_name: "",
      owner_cnic: "",
      owner_mobile_number: "",
    },
  });

  const isEmployee = watch("is_awc_employee");
  const isTenant = watch("is_tenant");
  const values = watch();

  const goNext = async () => {
    const step2Fields: (keyof FormValues)[] = [
      ...(isEmployee ? (["employee_number"] as const) : []),
      ...(isTenant
        ? (["owner_house_number", "owner_name", "owner_cnic", "owner_mobile_number"] as const)
        : []),
    ];
    const fieldsForStep: (keyof FormValues)[][] = [
      ["full_name", "house_number", "mobile_number", "email", "password"],
      step2Fields,
    ];
    const valid = await trigger(fieldsForStep[step]);
    if (valid) setStep((s) => s + 1);
  };

  const onSubmit = async (data: FormValues) => {
    setServerError(null);
    setSubmitting(true);
    let registered = false;
    try {
      await registerResident({
        full_name: data.full_name,
        house_number: data.house_number,
        mobile_number: data.mobile_number,
        email: data.email || undefined,
        password: data.password,
        is_awc_employee: data.is_awc_employee,
        employee_number: data.is_awc_employee ? data.employee_number : undefined,
        is_tenant: data.is_tenant,
        owner_house_number: data.is_tenant ? data.owner_house_number : undefined,
        owner_name: data.is_tenant ? data.owner_name : undefined,
        owner_cnic: data.is_tenant ? data.owner_cnic : undefined,
        owner_mobile_number: data.is_tenant ? data.owner_mobile_number : undefined,
      });
      registered = true;
    } catch (err) {
      setServerError(extractApiErrorMessage(err, "Registration failed. Please check your details."));
    } finally {
      setSubmitting(false);
    }
    // Deliberately outside the try/catch above: registration already
    // succeeded at this point (the resident row exists in the DB), so a
    // problem with navigation itself must never be mislabeled as a
    // registration failure — that would tell the user their data was
    // lost when it wasn't.
    if (registered) {
      router.replace("/pending");
    }
  };

  return (
    <ScreenContainer>
      <Text style={[styles.title, { color: theme.textPrimary }]}>Register your house</Text>
      <Text style={[styles.stepIndicator, { color: theme.textSecondary }]}>
        Step {step + 1} of 3 — {STEP_LABELS[step]}
      </Text>

      {step === 0 && (
        <>
          <Controller
            control={control}
            name="full_name"
            render={({ field }) => (
              <AppTextField label="Full name" value={field.value} onChangeText={field.onChange} error={errors.full_name?.message} />
            )}
          />
          <Controller
            control={control}
            name="house_number"
            render={({ field }) => (
              <AppTextField
                label="House number (e.g. B-026)"
                autoCapitalize="characters"
                value={field.value}
                onChangeText={field.onChange}
                error={errors.house_number?.message}
              />
            )}
          />
          <Controller
            control={control}
            name="mobile_number"
            render={({ field }) => (
              <AppTextField label="Mobile number" keyboardType="phone-pad" value={field.value} onChangeText={field.onChange} error={errors.mobile_number?.message} />
            )}
          />
          <Controller
            control={control}
            name="email"
            render={({ field }) => (
              <AppTextField label="Email (optional)" autoCapitalize="none" keyboardType="email-address" value={field.value} onChangeText={field.onChange} error={errors.email?.message} />
            )}
          />
          <Controller
            control={control}
            name="password"
            render={({ field }) => (
              <AppTextField label="Password" secureTextEntry value={field.value} onChangeText={field.onChange} error={errors.password?.message} />
            )}
          />
        </>
      )}

      {step === 1 && (
        <>
          <QuestionToggle
            question="Are you an AWC Employee?"
            control={control}
            name="is_awc_employee"
          />

          {isEmployee && (
            <Controller
              control={control}
              name="employee_number"
              render={({ field }) => (
                <AppTextField label="Employee number" value={field.value} onChangeText={field.onChange} error={errors.employee_number?.message} />
              )}
            />
          )}

          <QuestionToggle
            question="Are you a tenant?"
            control={control}
            name="is_tenant"
          />

          {isTenant && (
            <>
              <Controller
                control={control}
                    name="owner_house_number"
                    render={({ field }) => (
                      <AppTextField label="Owner's house number" value={field.value} onChangeText={field.onChange} error={errors.owner_house_number?.message} />
                    )}
                  />
                  <Controller
                    control={control}
                    name="owner_name"
                    render={({ field }) => (
                      <AppTextField label="Owner's name" value={field.value} onChangeText={field.onChange} error={errors.owner_name?.message} />
                    )}
                  />
                  <Controller
                    control={control}
                    name="owner_cnic"
                    render={({ field }) => (
                      <AppTextField label="Owner's CNIC" value={field.value} onChangeText={field.onChange} error={errors.owner_cnic?.message} />
                    )}
                  />
                  <Controller
                    control={control}
                    name="owner_mobile_number"
                    render={({ field }) => (
                      <AppTextField label="Owner's mobile number" keyboardType="phone-pad" value={field.value} onChangeText={field.onChange} error={errors.owner_mobile_number?.message} />
                    )}
                  />
                </>
              )}
        </>
      )}

      {step === 2 && (
        <View style={[styles.reviewCard, { backgroundColor: theme.surface, borderColor: theme.border }]}>
          <ReviewRow label="Name" value={values.full_name} theme={theme} />
          <ReviewRow label="House" value={values.house_number} theme={theme} />
          <ReviewRow label="Mobile" value={values.mobile_number} theme={theme} />
          <ReviewRow label="AWC employee" value={values.is_awc_employee ? "Yes" : "No"} theme={theme} />
          {values.is_awc_employee && <ReviewRow label="Employee #" value={values.employee_number} theme={theme} />}
          <ReviewRow label="Tenant" value={values.is_tenant ? "Yes" : "No"} theme={theme} />
          {values.is_tenant && <ReviewRow label="Owner" value={values.owner_name} theme={theme} />}
        </View>
      )}

      {serverError ? <Text style={[styles.serverError, { color: theme.danger }]}>{serverError}</Text> : null}

      <View style={styles.navRow}>
        {step > 0 && <AppButton label="Back" variant="secondary" onPress={() => setStep((s) => s - 1)} />}
        {step < 2 && <AppButton label="Next" onPress={goNext} />}
        {step === 2 && <AppButton label="Submit registration" onPress={handleSubmit(onSubmit)} loading={submitting} />}
      </View>
    </ScreenContainer>
  );
}

function QuestionToggle({
  question,
  control,
  name,
}: {
  question: string;
  control: any;
  name: "is_awc_employee" | "is_tenant";
}) {
  const theme = useTheme();
  return (
    <Controller
      control={control}
      name={name}
      render={({ field }) => (
        <View style={{ marginBottom: spacing.lg }}>
          <Text style={[styles.question, { color: theme.textPrimary }]}>{question}</Text>
          <View style={styles.toggleRow}>
            {[true, false].map((option) => (
              <Pressable
                key={String(option)}
                onPress={() => field.onChange(option)}
                style={[
                  styles.toggleOption,
                  {
                    borderColor: field.value === option ? theme.primary : theme.border,
                    backgroundColor: field.value === option ? theme.primary : "transparent",
                  },
                ]}
              >
                <Text style={{ color: field.value === option ? "#FFFFFF" : theme.textPrimary, fontWeight: "600" }}>
                  {option ? "Yes" : "No"}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>
      )}
    />
  );
}

function ReviewRow({ label, value, theme }: { label: string; value?: string; theme: ReturnType<typeof useTheme> }) {
  return (
    <View style={styles.reviewRow}>
      <Text style={{ color: theme.textSecondary, fontSize: 13 }}>{label}</Text>
      <Text style={{ color: theme.textPrimary, fontSize: 15, fontWeight: "500" }}>{value || "—"}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  title: { fontSize: 26, fontWeight: "600", marginBottom: spacing.xs },
  stepIndicator: { fontSize: 13, marginBottom: spacing.lg },
  question: { fontSize: 15, fontWeight: "500", marginBottom: spacing.sm },
  toggleRow: { flexDirection: "row", gap: spacing.sm },
  toggleOption: {
    flex: 1,
    borderWidth: 1.5,
    borderRadius: radii.md,
    paddingVertical: spacing.sm + 4,
    alignItems: "center",
  },
  reviewCard: {
    borderWidth: 1,
    borderRadius: radii.md,
    padding: spacing.md,
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  reviewRow: { flexDirection: "row", justifyContent: "space-between" },
  serverError: { fontSize: 13, marginBottom: spacing.md, textAlign: "center" },
  navRow: { flexDirection: "row", gap: spacing.md, marginTop: spacing.md },
});
