export interface AppRuntimeConfig {
  apiUrl?: string;
}

declare global {
  interface Window {
    __APP_CONFIG__?: AppRuntimeConfig;
  }
}

export const LOCAL_API_URL = "http://localhost:8000/api";

export function getRuntimeApiUrl(): string | undefined {
  if (typeof window === "undefined") {
    return undefined;
  }

  return window.__APP_CONFIG__?.apiUrl;
}

export function resolveApiUrl(defaultUrl: string = LOCAL_API_URL): string {
  const runtimeApiUrl = getRuntimeApiUrl();
  return runtimeApiUrl && runtimeApiUrl.trim().length > 0
    ? runtimeApiUrl
    : defaultUrl;
}

export {};
