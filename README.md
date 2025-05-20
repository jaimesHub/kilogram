# Flask API Service Starter

This is a minimal Flask API service starter based on [Google Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service).

## Getting Started

Server should run automatically when starting a workspace. To run manually, run:
```sh
./devserver.sh
```

## Folder structure

```
kilogram/ # Nơi chứa toàn bộ mã nguồn dự án. Entrypoint
├── app   # Chứa toàn bộ mã nguồn cốt lõi của ứng dụng
│   ├── __init__.py # Biến thư mục app thành một Python package. Nó có thể chứa các khởi tạo cần thiết cho package app, ví dụ như khởi tạo Flask application instance.
│   ├── controllers # Chịu trách nhiệm xử lý logic của các API endpoints. Mỗi module trong này thường tương ứng với một nhóm các chức năng liên quan.
│   │   ├── auth.py # Chứa các hàm (controllers) xử lý các API liên quan đến xác thực người dùng, chẳng hạn như /register, /login, và /logout.
│   │   └── user.py # Chứa các hàm xử lý các API liên quan đến người dùng, chẳng hạn như xem hồ sơ cá nhân, chỉnh sửa hồ sơ,... .
│   ├── models # Chứa các định nghĩa về cấu trúc dữ liệu của ứng dụng. Đây sẽ là nơi định nghĩa các models tương ứng với các bảng trong cơ sở dữ liệu (ví dụ: User, Post, Follower).
│   └── utils.py # Chứa các hàm tiện ích (utilities) được sử dụng trong toàn bộ ứng dụng. Việc tách các hàm tiện ích giúp code được tái sử dụng và tránh trùng lặp.
├── devserver.sh # Shell script sử dụng để khởi chạy server phát triển Flask một cách dễ dàng. Nó có thể bao gồm các lệnh để thiết lập môi trường và chạy main.py.
├── main.py # Điểm bắt đầu thực thi của ứng dụng Flask. Nó sẽ chứa việc khởi tạo Flask application instance, import các blueprints từ các controllers, và đăng ký chúng vào ứng dụng.
├── README.md # File Markdown chứa thông tin tổng quan về dự án, hướng dẫn cài đặt, cách chạy ứng dụng, và các thông tin hữu ích khác.
├── requirements.txt # File này liệt kê tất cả các thư viện Python mà dự án phụ thuộc vào. Nó được sử dụng bởi pip để cài đặt các dependencies cần thiết.
└── tests # Thư mục này sẽ chứa các file kiểm thử (unit tests, integration tests) để đảm bảo các phần của ứng dụng hoạt động đúng như mong đợi.