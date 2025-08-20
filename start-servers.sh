#!/bin/bash

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

#start python backend
# echo "Starting FastAPI backend..."
# cd python-backend && uvicorn app.main:app --reload --port 3000 &

wait
