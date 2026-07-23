import { StyleSheet, Text, TextInput, TextInputProps, View } from "react-native";

import { radii, spacing } from "../lib/theme";
import { useTheme } from "../lib/use-theme";

interface AppTextFieldProps extends TextInputProps {
  label: string;
  error?: string;
}

export function AppTextField({ label, error, style, ...inputProps }: AppTextFieldProps) {
  const theme = useTheme();

  return (
    <View style={styles.container}>
      <Text style={[styles.label, { color: theme.textSecondary }]}>{label}</Text>
      <TextInput
        placeholderTextColor={theme.textSecondary}
        style={[
          styles.input,
          {
            borderColor: error ? theme.danger : theme.border,
            color: theme.textPrimary,
            backgroundColor: theme.surface,
          },
          style,
        ]}
        {...inputProps}
      />
      {error ? <Text style={[styles.error, { color: theme.danger }]}>{error}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing.md,
  },
  label: {
    fontSize: 13,
    fontWeight: "500",
    marginBottom: spacing.xs,
  },
  input: {
    borderWidth: 1,
    borderRadius: radii.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm + 4,
    fontSize: 16,
  },
  error: {
    fontSize: 12,
    marginTop: spacing.xs,
  },
});
