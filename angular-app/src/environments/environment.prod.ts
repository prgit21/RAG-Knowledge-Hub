import { LOCAL_API_URL, resolveApiUrl } from './runtime-config';

export const environment = {
  production: true,
  apiUrl: resolveApiUrl(LOCAL_API_URL),
};
