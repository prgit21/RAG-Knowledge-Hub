#!/bin/bash

# Start root-config shell
echo "Starting root-config ..."
npm run start &

# Starting Angular MFE's
(cd dashboard && npm run serve:single-spa:dashboard) &
(cd angular-app && npm run serve:single-spa:angular-app) &

# Starting React Parcel
(cd react-app && npm run start) &

# Start python backend
echo "Starting FastAPI backend..."
(cd python-backend && uvicorn app.main:app --reload --port 8000) &

wait
