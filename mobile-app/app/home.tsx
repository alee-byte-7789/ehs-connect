import { router } from "expo-router";
import { StyleSheet, Text, View } from "react-native";

import { AppButton } from "../components/AppButton";
import { ScreenContainer } from "../components/ScreenContainer";
import { useAuth } from "../lib/auth-context";
import { useResidentMe } from "../lib/resident-queries";
import { spacing, radii } from "../lib/theme";
import { useTheme } from "../lib/use-theme";

export default function HomeScreen() {
  const { logout } = useAuth();
  const theme = useTheme();
  const { data: resident } = useResidentMe(true);

  const handleLogout = async () => {
    await logout();
    router.replace("/login");
  };

  return (
    <ScreenContainer>
      <Text style={[styles.greeting, { color: theme.textPrimary }]}>
        Hi, {resident?.full_name?.split(" ")[0] ?? "there"}
      </Text>

      <View style={[styles.card, { backgroundColor: theme.surface, borderColor: theme.border }]}>
        <Text style={[styles.cardLabel, { color: theme.textSecondary }]}>Resident ID</Text>
        <Text style={[styles.cardValue, { color: theme.textPrimary }]}>
          {resident?.resident_code ?? "—"}
        </Text>
      </View>

      <View style={[styles.card, { backgroundColor: theme.surface, borderColor: theme.border }]}>
        <Text style={[styles.cardLabel, { color: theme.textSecondary }]}>Status</Text>
        <Text style={[styles.cardValue, { color: theme.primary }]}>
          {resident?.verification_status ?? "—"}
        </Text>
      </View>

      <Text style={[styles.comingSoon, { color: theme.textSecondary }]}>
        Complaints, feedback, and emergency contacts land here once their
        backend modules are built — this dashboard is wired to your real
        account already, so nothing here is a placeholder.
      </Text>

      <AppButton label="Log out" variant="secondary" onPress={handleLogout} />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  greeting: {
    fontSize: 26,
    fontWeight: "600",
    marginBottom: spacing.lg,
  },
  card: {
    borderRadius: radii.md,
    borderWidth: 1,
    padding: spacing.md,
    marginBottom: spacing.md,
  },
  cardLabel: {
    fontSize: 13,
    marginBottom: spacing.xs,
  },
  cardValue: {
    fontSize: 18,
    fontWeight: "600",
  },
  comingSoon: {
    fontSize: 13,
    lineHeight: 19,
    marginTop: spacing.sm,
    marginBottom: spacing.lg,
  },
});
