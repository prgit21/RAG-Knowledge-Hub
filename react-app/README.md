# React Chat Micro-frontend

## Runtime configuration

The chatbot reads its backend origin from the following sources (highest priority first):

1. `window.__APP_CONFIG__.apiUrl`
2. `REACT_APP_API_URL` (injected at build time via Webpack's `DefinePlugin`)
3. `http://localhost:8000` when `NODE_ENV !== "production"`

Set `REACT_APP_API_URL` during CI/CD builds so that the bundled assets talk to the correct backend. Example:

```bash
REACT_APP_API_URL=https://api.example.com npm run build:webpack
```

When serving prebuilt assets you can also inject a runtime override by defining `window.__APP_CONFIG__ = { apiUrl: "https://api.example.com" };` before loading the bundle.
