import { ActivityIndicator, Pressable, StyleSheet, Text } from "react-native";

import { radii, spacing } from "../lib/theme";
import { useTheme } from "../lib/use-theme";

interface AppButtonProps {
  label: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  variant?: "primary" | "secondary";
}

export function AppButton({ label, onPress, loading, disabled, variant = "primary" }: AppButtonProps) {
  const theme = useTheme();
  const isDisabled = disabled || loading;

  return (
    <Pressable
      onPress={onPress}
      disabled={isDisabled}
      style={({ pressed }) => [
        styles.base,
        {
          backgroundColor: variant === "primary" ? theme.primary : "transparent",
          borderColor: theme.primary,
          borderWidth: variant === "secondary" ? 1.5 : 0,
          opacity: isDisabled ? 0.6 : pressed ? 0.85 : 1,
        },
      ]}
    >
      {loading ? (
        <ActivityIndicator color={variant === "primary" ? "#FFFFFF" : theme.primary} />
      ) : (
        <Text
          style={[
            styles.label,
            { color: variant === "primary" ? "#FFFFFF" : theme.primary },
          ]}
        >
          {label}
        </Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: radii.md,
    paddingVertical: spacing.md,
    alignItems: "center",
    justifyContent: "center",
    minHeight: 52,
  },
  label: {
    fontSize: 16,
    fontWeight: "600",
  },
});
