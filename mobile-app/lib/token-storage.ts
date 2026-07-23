import AsyncStorage from "@react-native-async-storage/async-storage";

const ACCESS_TOKEN_KEY = "ehs_access_token";
const REFRESH_TOKEN_KEY = "ehs_refresh_token";

export const tokenStorage = {
  async getAccessToken(): Promise<string | null> {
    return AsyncStorage.getItem(ACCESS_TOKEN_KEY);
  },
  async getRefreshToken(): Promise<string | null> {
    return AsyncStorage.getItem(REFRESH_TOKEN_KEY);
  },
  async setTokens(accessToken: string, refreshToken: string): Promise<void> {
    await AsyncStorage.setMany({
      [ACCESS_TOKEN_KEY]: accessToken,
      [REFRESH_TOKEN_KEY]: refreshToken,
    });
  },
  async clear(): Promise<void> {
    await AsyncStorage.removeMany([ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY]);
  },
};
