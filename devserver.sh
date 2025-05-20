#!/bin/sh
source .venv/bin/activate
export NAME=James_Bro
export DATABASE_URL=mysql+pymysql://root:@localhost:3306/kilogram

export GOOGLE_APPLICATION_CREDENTIALS=./credentials/kilogram-backend-c8031c5797be.json

# python -m flask --app main run --debug
python main.py # run on PORT 3000