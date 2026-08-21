import json
import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"

    with app.test_client() as client:
        yield client


# ============================================================
# Helper
# ============================================================

def load_users():
    with open("users.json", "r", encoding="utf-8") as file:
        return json.load(file)


# ============================================================
# 1. Test GET /login
# ============================================================

def test_login_page(client):
    response = client.get("/login")

    assert response.status_code == 200

    # Kiểm tra các thành phần chính của trang login
    assert b"Sign in" in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data


# ============================================================
# 2. Test login thành công cho TOÀN BỘ 20 USER
# ============================================================

@pytest.mark.parametrize(
    "user",
    load_users()
)
def test_login_all_users(client, user):

    response = client.post(
        "/login",
        data={
            "username": user["username"],
            "password": user["password"]
        },
        follow_redirects=True
    )

    # Login thành công
    assert response.status_code == 200

    # Kiểm tra session
    with client.session_transaction() as session:

        assert session["user_id"] == user["id"]
        assert session["username"] == user["username"]
        assert session["name"] == user["name"]


# ============================================================
# 3. Sai password
# ============================================================

@pytest.mark.parametrize(
    "user",
    load_users()
)
def test_login_wrong_password(client, user):

    response = client.post(
        "/login",
        data={
            "username": user["username"],
            "password": "WrongPassword@999"
        }
    )

    # Không redirect vì login thất bại
    assert response.status_code == 200

    # Không được tạo session đăng nhập
    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "username" not in session


# ============================================================
# 4. Username không tồn tại
# ============================================================

@pytest.mark.parametrize(
    "username",
    [
        "unknown",
        "notexist",
        "user123",
        "admin123",
        "hello",
        "abcxyz"
    ]
)
def test_login_unknown_username(client, username):

    response = client.post(
        "/login",
        data={
            "username": username,
            "password": "Admin@123"
        }
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


# ============================================================
# 5. Username rỗng
# ============================================================

@pytest.mark.parametrize(
    "password",
    [
        "Admin@123",
        "",
        "123456",
        "password"
    ]
)
def test_login_empty_username(client, password):

    response = client.post(
        "/login",
        data={
            "username": "",
            "password": password
        }
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


# ============================================================
# 6. Password rỗng
# ============================================================

@pytest.mark.parametrize(
    "username",
    [
        user["username"]
        for user in load_users()
    ]
)
def test_login_empty_password(client, username):

    response = client.post(
        "/login",
        data={
            "username": username,
            "password": ""
        }
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


# ============================================================
# 7. Cả username và password đều rỗng
# ============================================================

def test_login_empty_username_and_password(client):

    response = client.post(
        "/login",
        data={
            "username": "",
            "password": ""
        }
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


# ============================================================
# 8. Username có khoảng trắng
# ============================================================

@pytest.mark.parametrize(
    "user",
    load_users()
)
def test_login_username_with_spaces(client, user):

    response = client.post(
        "/login",
        data={
            "username": f"  {user['username']}  ",
            "password": user["password"]
        }
    )

    # app.py hiện tại có .strip()
    # nên username có khoảng trắng đầu/cuối vẫn login được
    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session["user_id"] == user["id"]


# ============================================================
# 9. Sai username nhưng đúng password
# ============================================================

@pytest.mark.parametrize(
    "user",
    load_users()
)
def test_wrong_username_correct_password(client, user):

    response = client.post(
        "/login",
        data={
            "username": "wrong_username",
            "password": user["password"]
        }
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


# ============================================================
# 10. Đúng username nhưng password khác
# ============================================================

@pytest.mark.parametrize(
    "user",
    load_users()
)
def test_correct_username_wrong_password(client, user):

    response = client.post(
        "/login",
        data={
            "username": user["username"],
            "password": "CompletelyWrong@123"
        }
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


# ============================================================
# 11. Password có khoảng trắng
# ============================================================

@pytest.mark.parametrize(
    "user",
    load_users()
)
def test_password_with_spaces(client, user):

    response = client.post(
        "/login",
        data={
            "username": user["username"],
            "password": f" {user['password']} "
        }
    )

    # Password KHÔNG được tự động strip
    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


# ============================================================
# 12. Username phân biệt chữ hoa/chữ thường
# ============================================================

@pytest.mark.parametrize(
    "user",
    load_users()
)
def test_username_case_sensitive(client, user):

    response = client.post(
        "/login",
        data={
            "username": user["username"].upper(),
            "password": user["password"]
        }
    )

    # username hiện tại phải chính xác
    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


# ============================================================
# 13. Password phân biệt chữ hoa/chữ thường
# ============================================================

@pytest.mark.parametrize(
    "user",
    load_users()
)
def test_password_case_sensitive(client, user):

    response = client.post(
        "/login",
        data={
            "username": user["username"],
            "password": user["password"].lower()
        }
    )

    assert response.status_code == 200

    with client.session_transaction() as session:
        assert "user_id" not in session


# ============================================================
# 14. Login rồi logout
# ============================================================

def test_logout_after_login(client):

    # Login
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "Admin@123"
        }
    )

    assert response.status_code == 302

    # Kiểm tra đã login
    with client.session_transaction() as session:
        assert session["user_id"] == 1

    # Logout
    response = client.get(
        "/logout",
        follow_redirects=True
    )

    assert response.status_code == 200

    # Kiểm tra session đã bị xóa
    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "username" not in session
        assert "name" not in session


# ============================================================
# 15. Truy cập trang chủ khi chưa login
# ============================================================

def test_index_without_login(client):

    response = client.get("/")

    assert response.status_code == 302
    assert "/login" in response.location


# ============================================================
# 16. Truy cập trang chủ sau khi login
# ============================================================

def test_index_after_login(client):

    client.post(
        "/login",
        data={
            "username": "admin",
            "password": "Admin@123"
        }
    )

    response = client.get("/")

    assert response.status_code == 200
    assert b"Administrator" in response.data


# ============================================================
# 17. Login nhiều lần
# ============================================================

def test_multiple_login(client):

    # Login admin
    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "Admin@123"
        }
    )

    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session["username"] == "admin"

    # Login user khác
    response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "Test@123"
        }
    )

    assert response.status_code == 302

    # Session phải chuyển sang user mới
    with client.session_transaction() as session:
        assert session["username"] == "testuser"
        assert session["user_id"] == 2