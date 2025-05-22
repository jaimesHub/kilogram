# Bước 1: Chọn một image cơ sở (base image)
# Sử dụng image Python 3.9 phiên bản "slim" (nhẹ hơn) làm nền tảng.
FROM python:3.9-slim

# Bước 2: Đặt thư mục làm việc bên trong container
# Tất cả các lệnh tiếp theo sẽ được thực thi trong ngữ cảnh của thư mục /app.
WORKDIR /app

# Bước 3: Sao chép file requirements.txt và cài đặt các thư viện
# Sao chép file requirements.txt từ máy thật vào thư mục /app trong container.
COPY requirements.txt .
# Chạy lệnh pip install để cài đặt các thư viện được liệt kê trong requirements.txt.
# --no-cache-dir giúp giảm kích thước image bằng cách không lưu cache của pip.
RUN pip install --no-cache-dir -r requirements.txt

# Bước 4: Sao chép toàn bộ mã nguồn của ứng dụng vào container
# Sao chép tất cả các file và thư mục từ thư mục hiện tại của máy thật (.)
# vào thư mục /app bên trong container.
# Lưu ý: Nên COPY requirements.txt và RUN pip install trước khi COPY toàn bộ code
# để tận dụng cơ chế caching của Docker. Nếu code thay đổi nhưng requirements.txt không đổi,
# Docker sẽ không cần chạy lại bước pip install.
COPY . .

# Bước 5: Thiết lập các biến môi trường (tùy chọn, có thể ghi đè khi chạy)
# Đặt biến môi trường DATABASE_URL với một giá trị mặc định.
# Giá trị này sẽ được sử dụng nếu không có giá trị nào khác được cung cấp khi chạy container.
# Trong thực tế, đây thường là localhost để phát triển, nhưng sẽ được ghi đè
# để trỏ tới Cloud SQL hoặc service db trong Docker Compose.
ENV DATABASE_URL=mysql+pymysql://root:@localhost:3306/kilogram
# Đặt biến môi trường cho Flask biết file chính của ứng dụng.
ENV FLASK_APP=main

# Bước 6: Khai báo cổng mà ứng dụng sẽ lắng nghe bên trong container
# Lệnh EXPOSE không thực sự "mở" cổng, mà chỉ là một hình thức tài liệu hóa,
# thông báo rằng container này dự kiến sẽ lắng nghe trên cổng 5000.
# Việc ánh xạ cổng thực tế ra máy host sẽ được thực hiện bằng cờ -p khi chạy container.
EXPOSE 5000

# Bước 7: Lệnh để khởi chạy ứng dụng khi container bắt đầu
# Sử dụng Gunicorn làm WSGI server để chạy ứng dụng Flask.
# --bind 0.0.0.0:5000: Gunicorn sẽ lắng nghe trên tất cả các network interface
# bên trong container ở cổng 5000.
# main:app: Chỉ định Gunicorn chạy đối tượng 'app' từ file 'main.py'.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]