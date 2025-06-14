from locust import HttpUser, task, between
import random

# --- Cấu hình chung ---
# Địa chỉ base URL của API backend Flask đang chạy
# Thay thế bằng URL thực tế của bạn (local, Firebase Studio, hoặc Cloud Run)
# Ví dụ: API_BASE_URL = "http://127.0.0.1:5000/api"
#        API_BASE_URL = "https://your-cloud-run-service-url/api"
API_BASE_URL = "http://127.0.0.1:3000/api" # GIẢ ĐỊNH BACKEND CHẠY TRÊN CỔNG 8080 VÀ CÓ PREFIX /api

# Danh sách các cặp username/password hợp lệ để đăng nhập (nên có nhiều để đa dạng hóa)
# Trong thực tế, bạn có thể đọc từ file hoặc tạo động
VALID_USERS = [
    {},
    # Thêm nhiều user ở đây nếu có
]

# Lưu trữ access token sau khi đăng nhập thành công
# (Trong kịch bản phức tạp hơn, mỗi user ảo nên có token riêng)
# Để đơn giản, ví dụ này có thể dùng một token chung nếu các user dùng chung token
# hoặc mỗi user tự quản lý token của mình trong on_start
#ACCESS_TOKEN = None


class InstagramUser(HttpUser):
    # Thời gian chờ giữa các task của một user ảo (tính bằng giây)
    # 'between(min, max)' sẽ chọn ngẫu nhiên một giá trị trong khoảng đó
    wait_time = between(1, 3)  # Chờ từ 1 đến 3 giây giữa các request

    # Thuộc tính host có thể được đặt ở đây hoặc truyền qua command line khi chạy Locust
    # host = API_BASE_URL # Nếu không đặt ở đây, bạn phải truyền --host khi chạy locust

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.access_token = None # Mỗi user ảo sẽ có token riêng
        self.user_credentials = random.choice(VALID_USERS) # Chọn ngẫu nhiên một user để mô phỏng

    def on_start(self):
        """
        Được gọi một lần khi một user ảo (Locust worker) bắt đầu.
        Thường dùng để đăng nhập và lấy access token.
        """
        if not VALID_USERS:
            print("ERROR: VALID_USERS list is empty in locustfile.py. Cannot login.")
            self.environment.runner.quit() # Dừng locust nếu không có user để test
            return

        print(f"User starting with credentials: {self.user_credentials['username']}")
        
        try:
            response = self.client.post(
                f"{API_BASE_URL}/auth/login", # Endpoint đăng nhập
                json={
                    "username": self.user_credentials["username"],
                    "password": self.user_credentials["password"]
                }
            )
            response.raise_for_status() # Sẽ raise exception nếu status code là 4xx hoặc 5xx
            
            json_response = response.json()
            if json_response.get("success") and json_response.get("data", {}).get("access_token"):
                self.access_token = json_response["data"]["access_token"]
                print(f"Login successful for {self.user_credentials['username']}, token obtained.")
            else:
                print(f"Login failed for {self.user_credentials['username']}: No access_token in response or success is false. Response: {json_response}")
                # Cân nhắc việc dừng user này hoặc cho phép nó tiếp tục mà không có token
                # self.environment.runner.quit() # Hoặc không làm gì và các task sau sẽ thất bại do thiếu token
        except Exception as e:
            print(f"Login request failed for {self.user_credentials['username']}: {e}")
            # self.environment.runner.quit()

    # Các "tasks" là những hành động mà user ảo sẽ thực hiện
    # Bạn có thể gán trọng số cho các task bằng cách thêm số vào decorator @task(weight)
    # Task có weight cao hơn sẽ được chọn thực hiện thường xuyên hơn.

    @task(10) # Ví dụ: Xem News Feed có tần suất cao nhất
    def view_news_feed(self):
        if not self.access_token:
            # print(f"User {self.user_credentials['username']} has no access token, skipping view_news_feed.")
            return # Bỏ qua task này nếu chưa đăng nhập thành công

        headers = {"Authorization": f"Bearer {self.access_token}"}
        # Đặt tên cho request để nhóm các request tương tự trong báo cáo của Locust
        self.client.get(f"{API_BASE_URL}/posts/newsfeed", headers=headers, name="/post/newsfeed (View News Feed)")
        # print(f"User {self.user_credentials['username']} viewed news feed.")


    @task(3) # Ví dụ: Xem hồ sơ cá nhân của chính mình
    def view_own_profile(self):
        if not self.access_token:
            return
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        self.client.get(f"{API_BASE_URL}/users/profile", headers=headers, name="/user/profile (View Own Profile)")

    @task(1) # Ví dụ: Xem hồ sơ của một người dùng ngẫu nhiên khác (cần danh sách user ID)
    def view_other_user_profile(self):
        if not self.access_token:
            return
        
        # Giả sử bạn có một danh sách các user ID khác để xem
        # Trong thực tế, bạn có thể lấy ID này từ một API khác hoặc định nghĩa sẵn
        other_user_ids = ["1", "2", "3", "another_user_id_from_db"] # Thay thế bằng user ID thật
        if not other_user_ids:
            return
            
        target_user_id = random.choice(other_user_ids)
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        # Endpoint này trong project mẫu là /api/user//profile
        self.client.get(f"{API_BASE_URL}/users/{target_user_id}/profile", headers=headers, name="/user/{user_id}/profile (View Other Profile)")

    # Thêm các task khác ở đây, ví dụ:
    # @task(2)
    # def create_post(self):
    #     if not self.access_token:
    #         return
    #     headers = {"Authorization": f"Bearer {self.access_token}"}
    #     post_data = {
    #         "caption": f"Locust test post at {random.randint(1,1000)}",
    #         "media_url": "https://example.com/some_image.jpg" # Hoặc URL thật
    #     }
    #     self.client.post(f"{API_BASE_URL}/post", json=post_data, headers=headers, name="/post (Create Post)")

    # @task(1)
    # def like_random_post(self):
    #     if not self.access_token:
    #         return
    #     # Cần danh sách post_id để like ngẫu nhiên
    #     post_ids_to_like = ["1", "2", "another_post_id"] # Thay thế bằng post ID thật
    #     if not post_ids_to_like:
    #         return
    #     target_post_id = random.choice(post_ids_to_like)
    #     headers = {"Authorization": f"Bearer {self.access_token}"}
    #     self.client.post(f"{API_BASE_URL}/post/{target_post_id}/like", headers=headers, name="/post/{post_id}/like (Like Post)")

# Nếu bạn muốn chạy Locust ở chế độ headless (không có UI web), bạn có thể bỏ comment phần này
# import logging
# locust.runners.logger.setLevel(logging.INFO) # Set log level