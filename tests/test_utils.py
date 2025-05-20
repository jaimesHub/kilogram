import unittest

# Importing allowed_file function from our utils module
from app.utils import allowed_file

# The TestUtils class contains test cases for utils module
class TestUtils(unittest.TestCase):

    # Test case 1: Phần mở rộng hợp lệ, chữ thường
    def test_allowed_extension_lower(self):
        self.assertTrue(allowed_file("image.jpg"), "Test failed for image.jpg")
        self.assertTrue(allowed_file("photo.png"), "Test failed for photo.png")
        self.assertTrue(allowed_file("animation.gif"), "Test failed for animation.gif")
        self.assertTrue(allowed_file("picture.jpeg"), "Test failed for picture.jpeg")

    # Test case 2: Phần mở rộng hợp lệ, chữ hoa/hỗn hợp
    def test_allowed_extension_upper(self):
        self.assertTrue(allowed_file("image.JPG"), "Test failed for image.JPG")
        self.assertTrue(allowed_file("photo.PnG"), "Test failed for photo.PnG")
        self.assertTrue(allowed_file("animation.GIF"), "Test failed for animation.GIF")
        self.assertTrue(allowed_file("picture.jPeG"), "Test failed for picture.jPeG")

    # Test case 3: Phần mở rộng không hợp lệ
    def test_disallowed_extension(self):
        self.assertFalse(allowed_file("document.pdf"), "Test failed for document.pdf")
        self.assertFalse(allowed_file("archive.zip"), "Test failed for archive.zip")
        self.assertFalse(allowed_file("script.py"), "Test failed for script.py")
        # Thêm trường hợp đuôi file trông giống nhưng không khớp hoàn toàn
        self.assertFalse(allowed_file("image.jpgx"), "Test failed for image.jpgx")

    # Test case 4: Tên file có nhiều dấu chấm
    def test_multiple_dots(self):
        self.assertTrue(allowed_file("image.backup.jpg"), "Test failed for image.backup.jpg")
        self.assertFalse(allowed_file("archive.tar.gz"), "Test failed for archive.tar.gz")
        self.assertTrue(allowed_file("photo.old.png"), "Test failed for photo.old.png")

    # Test case 5: Tên file không có phần mở rộng
    def test_no_extension(self):
        self.assertFalse(allowed_file("myfile"), "Test failed for 'myfile'")
        self.assertFalse(allowed_file("image"), "Test failed for 'image'")

    # Test case 6: Tên file chỉ có phần mở rộng (bắt đầu bằng dấu chấm)
    def test_only_extension(self):
        # Hàm allowed_file yêu cầu phải có ký tự trước dấu chấm cuối cùng
        self.assertFalse(allowed_file(".jpg"), "Test failed for '.jpg'")
        self.assertFalse(allowed_file(".png"), "Test failed for '.png'")

    # Test case 7: Tên file ẩn (ví dụ: .bashrc)
    def test_hidden_file(self):
        # Phần mở rộng được xác định là 'bashrc', không hợp lệ
        self.assertFalse(allowed_file(".bashrc"), "Test failed for '.bashrc'")
        self.assertFalse(allowed_file(".gitconfig"), "Test failed for '.gitconfig'")

    # Test case 8: Chuỗi rỗng hoặc tên file chỉ có dấu chấm
    def test_empty_or_dot_filename(self):
        self.assertFalse(allowed_file(""), "Test failed for empty string")
        self.assertFalse(allowed_file("."), "Test failed for '.'")

# Cho phép chạy file test trực tiếp
if __name__ == '__main__':
    unittest.main()