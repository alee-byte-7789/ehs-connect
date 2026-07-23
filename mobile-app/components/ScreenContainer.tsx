import { ReactNode } from "react";
import { KeyboardAvoidingView, Platform, ScrollView, StyleSheet } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { spacing } from "../lib/theme";
import { useTheme } from "../lib/use-theme";

export function ScreenContainer({ children, scroll = true }: { children: ReactNode; scroll?: boolean }) {
  const theme = useTheme();
  const Content = scroll ? ScrollView : (props: { children: ReactNode }) => <>{props.children}</>;

  return (
    <SafeAreaView style={[styles.flex, { backgroundColor: theme.background }]}>
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <Content contentContainerStyle={styles.content} style={styles.flex}>
          {children}
        </Content>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1 },
  content: {
    flexGrow: 1,
    padding: spacing.lg,
  },
});
