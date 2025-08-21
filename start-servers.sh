#!/bin/bash

# Start PostgreSQL database
echo "Starting PostgreSQL database..."
docker compose up -d db

# Start Angular shell
echo "Starting Angular shell ..."
npm run start &

# Starting Angular MFE's
cd dashboard && npm run serve:single-spa:dashboard &  
cd angular-app && npm run serve:single-spa:angular-app &

# Starting React Parcel
cd react-app && npm run start &  

# # Start Node.js Backend
# echo "Starting Node.js backend..."
cd node-backend && nodemon server.js & 

# Start python backend
echo "Starting FastAPI backend..."
cd python-backend && uvicorn app.main:app --reload --port 3000 &

wait
