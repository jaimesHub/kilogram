# Flask API Service Starter

This is a minimal Flask API service starter based on [Google Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service).

## Getting Started

Server should run automatically when starting a workspace. To run manually, run:
```sh
./devserver.sh
```

## Folder structure

```
kilogram/
├── app
│   ├── __init__.py
│   ├── controllers
│   │   ├── auth.py
│   │   └── user.py
│   ├── models
│   └── utils.py
├── devserver.sh
├── main.py
├── README.md
├── requirements.txt
└── tests
```