import { useColorScheme } from "react-native";

import { colors } from "./theme";

export function useTheme() {
  const scheme = useColorScheme();
  return scheme === "dark" ? colors.dark : colors.light;
}
