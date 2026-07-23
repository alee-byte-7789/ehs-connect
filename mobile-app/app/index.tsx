import { Redirect } from "expo-router";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";

import { useAuth } from "../lib/auth-context";
import { useResidentMe } from "../lib/resident-queries";
import { spacing } from "../lib/theme";
import { useTheme } from "../lib/use-theme";

export default function SplashGate() {
  const { status, logout } = useAuth();
  const theme = useTheme();

  const residentQuery = useResidentMe(status === "signed-in");

  if (status === "checking" || (status === "signed-in" && residentQuery.isPending)) {
    return (
      <View style={[styles.center, { backgroundColor: theme.background }]}>
        <ActivityIndicator size="large" color={theme.primary} />
        <Text style={[styles.brand, { color: theme.textPrimary }]}>EHS Connect</Text>
      </View>
    );
  }

  if (status === "signed-out") {
    return <Redirect href="/login" />;
  }

  // Signed in, but the stored token no longer resolves to a valid account
  // (e.g. rejected after login, or revoked) — the request interceptor's
  // refresh attempt already failed by this point, so treat it as signed out.
  if (residentQuery.isError) {
    logout();
    return <Redirect href="/login" />;
  }

  if (residentQuery.data?.verification_status === "pending") {
    return <Redirect href="/pending" />;
  }

  return <Redirect href="/home" />;
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    gap: spacing.md,
  },
  brand: {
    fontSize: 20,
    fontWeight: "600",
  },
});
