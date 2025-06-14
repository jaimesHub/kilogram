#!/bin/sh
source .venv/bin/activate
export NAME=James_Bro
export DATABASE_URL=mysql+pymysql://root:@localhost:3306/kilogram

export GOOGLE_APPLICATION_CREDENTIALS=./credentials/kilogram-backend-c8031c5797be.json

# python -m flask --app main run --debug
python main.py # run on PORT 3000
# gunicorn --bind 0.0.0.0:3000 main:app # FOR LOCUST

# API Testing manually
# curl -X POST "http://localhost:3000/api/auth/register" \
#      -H "Content-Type: application/json" \
#      -d '{"username":"test_user_5","password":"password123","fullname":"Test User 5","email":"test5@example.com"}'

# curl -X POST "http://localhost:3000/api/auth/login" \
#      -H "Content-Type: application/json" \
#      -d '{"username":"test_user_3","password":"password123"}'

# curl -X GET "http://localhost:3000/api/auth/me" \
#      -H "Content-Type: application/json" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# curl -X PUT "http://localhost:3000/api/users/profile" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
#      -H "Content-Type: application/json" \
#      -d '{"fullname":"New Full Name","bio":"This is my new bio"}'

# curl -X GET "http://localhost:3000/api/users/5/profile" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# curl -X GET "http://localhost:3000/api/users/profile" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# curl -X POST "http://localhost:3000/api/users/5/follow" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# curl -X DELETE "http://localhost:3000/api/users/5/follow" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# curl --location 'https://localhost:3000/api/posts' \
# -H 'Content-Type: application/json' \
# -H 'Authorization: YOUR_ACCESS_TOKEN' \
# -d '{"image_url": "image4.jpg","caption": "great photos"}'

# curl --location 'https://localhost:3000/api/posts/10' \
# -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'

# curl -X GET "http://localhost:3000/api/users/1/posts" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# curl -X POST "http://localhost:3000/api/posts/2/like" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# curl -X DELETE "http://localhost:3000/api/posts/2/like" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# curl -X GET "http://localhost:3000/api/posts/newsfeed" \
#      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# curl -X GET 'http://localhost:3000/api/users/search?username=test_user_' \
# -H "Authorization: Bearer YOUR_ACCESS_TOKEN"