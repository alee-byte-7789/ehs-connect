import { router } from "expo-router";
import { StyleSheet, Text } from "react-native";

import { AppButton } from "../components/AppButton";
import { ScreenContainer } from "../components/ScreenContainer";
import { useAuth } from "../lib/auth-context";
import { spacing } from "../lib/theme";
import { useTheme } from "../lib/use-theme";

export default function PendingScreen() {
  const { logout } = useAuth();
  const theme = useTheme();

  const handleLogout = async () => {
    await logout();
    router.replace("/login");
  };

  return (
    <ScreenContainer scroll={false}>
      <Text style={[styles.title, { color: theme.textPrimary }]}>Verification pending</Text>
      <Text style={[styles.body, { color: theme.textSecondary }]}>
        Thanks for registering. The Housing Office reviews every new resident
        before granting access — you'll be able to log in as soon as your
        registration is approved.
      </Text>
      <Text style={[styles.body, { color: theme.textSecondary }]}>
        This usually takes 1-2 business days. Check back by logging in again.
      </Text>
      <AppButton label="Log out" variant="secondary" onPress={handleLogout} />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: 24,
    fontWeight: "600",
    marginBottom: spacing.md,
  },
  body: {
    fontSize: 15,
    lineHeight: 22,
    marginBottom: spacing.md,
  },
});
