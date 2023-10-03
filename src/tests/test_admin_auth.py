from datetime import datetime

from admin.auth.auth_manager import AuthManager
from database.models import Admin
from database.repositories.admin_repository import AdminRepository


def test_admin_signup_success(client, mocker):
    body = {
        "login_name": "login_ID",
        "password": "wip-password",
        "nickname": "pinocchio",
    }

    check_uniqueness_mock_function = mocker.patch.object(
        AdminRepository, "check_uniqueness", return_value=True
    )
    hash_password_mock_function = mocker.patch.object(
        AuthManager, "hash_password", return_value="hashed"
    )
    create_admin_model_spy = mocker.spy(Admin, "create")
    mocker.patch.object(
        AdminRepository,
        "create_admin",
        return_value=Admin(
            id=1, login_name="login_ID", password="hashed", nickname="pinocchio"
        ),
    )

    response = client.post("/admin/api/v1/auth/signup", json=body)

    check_uniqueness_mock_function.assert_called_once()
    hash_password_mock_function.assert_called_once_with(body["password"])
    create_admin_model_spy.assert_called_once_with(
        body["login_name"], "hashed", body["nickname"]
    )

    assert create_admin_model_spy.spy_return.id is None
    assert create_admin_model_spy.spy_return.login_name == body["login_name"]
    assert create_admin_model_spy.spy_return.password == "hashed"
    assert create_admin_model_spy.spy_return.nickname == body["nickname"]

    assert response.status_code == 201
    assert response.json()["data"] == {
        "id": 1,
        "login_name": body["login_name"],
        "nickname": body["nickname"],
    }
    assert response.json()["message"] == "Created new admin account successfully."


def test_admin_signup_with_short_password(client, mocker):
    body = {
        "login_name": "login_ID",
        "password": "short",
        "nickname": "pinocchio",
    }

    check_uniqueness_mock_function = mocker.patch.object(
        AdminRepository, "check_uniqueness", return_value=True
    )
    hash_password_mock_function = mocker.patch.object(
        AuthManager, "hash_password", return_value="hashed"
    )
    create_admin_model_spy = mocker.spy(Admin, "create")

    response = client.post("/admin/api/v1/auth/signup", json=body)

    check_uniqueness_mock_function.assert_not_called()
    hash_password_mock_function.assert_not_called()
    create_admin_model_spy.assert_not_called()

    assert response.status_code == 400
    assert (
        response.json()["detail"] == "The password must be at least 8 characters long."
    )


def test_admin_signup_with_duplicated_data(client, mocker):
    body = {
        "login_name": "login_ID",
        "password": "wip-password",
        "nickname": "pinocchio",
    }

    check_uniqueness_mock_function = mocker.patch.object(
        AdminRepository, "check_uniqueness", return_value=False
    )
    hash_password_mock_function = mocker.patch.object(
        AuthManager, "hash_password", return_value="hashed"
    )
    create_admin_model_spy = mocker.spy(Admin, "create")

    response = client.post("/admin/api/v1/auth/signup", json=body)

    check_uniqueness_mock_function.assert_called_once()
    hash_password_mock_function.assert_not_called()
    create_admin_model_spy.assert_not_called()

    assert response.status_code == 409
    assert response.json()["detail"] == "Both login_name and nickname should be unique."


def test_admin_login_success(client, mocker):
    database = {
        "id": 1,
        "login_name": "login_ID",
        "password": "hashed",
        "nickname": "pinocchio",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    body = {
        "login_name": "login_ID",
        "password": "wip-password",
    }

    get_admin_mock_function = mocker.patch.object(
        AdminRepository,
        "get_admin",
        return_value=Admin(
            id=database["id"],
            login_name=database["login_name"],
            password=database["password"],
            nickname=database["nickname"],
        ),
    )
    verify_password_mock_function = mocker.patch.object(
        AuthManager, "verify_password", return_value=True
    )

    response = client.post("/admin/api/v1/auth/login", json=body)

    get_admin_mock_function.assert_called_once_with(body["login_name"])
    verify_password_mock_function.assert_called_once_with(
        body["password"], database["password"]
    )

    assert response.status_code == 200
    assert response.json()["data"]["admin"] == {
        "id": database["id"],
        "login_name": database["login_name"],
        "nickname": database["nickname"],
    }
    assert response.json()["data"]["access_token"] is not None
    assert response.json()["message"] == "Login success response with access token"


def test_admin_login_with_wrong_login_name(client, mocker):
    database = {
        "id": 1,
        "login_name": "login_ID",
        "password": "hashed",
        "nickname": "pinocchio",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    body = {
        "login_name": "wrong_login_ID",
        "password": "wip-password",
    }

    get_admin_mock_function = mocker.patch.object(
        AdminRepository,
        "get_admin",
        return_value=None,
    )
    verify_password_mock_function = mocker.patch.object(
        AuthManager, "verify_password", return_value=True
    )
    create_access_token_mock_function = mocker.patch.object(
        AuthManager, "create_access_token", return_value="jwt_token"
    )

    response = client.post("/admin/api/v1/auth/login", json=body)

    get_admin_mock_function.assert_called_once_with(body["login_name"])
    verify_password_mock_function.assert_not_called()
    create_access_token_mock_function.assert_not_called()

    assert response.status_code == 404
    assert response.json()["detail"] == "Login name not found."


def test_admin_login_with_wrong_password(client, mocker):
    database = {
        "id": 1,
        "login_name": "login_ID",
        "password": "hashed",
        "nickname": "pinocchio",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    body = {
        "login_name": "login_ID",
        "password": "wrong-wip-password",
    }

    get_admin_mock_function = mocker.patch.object(
        AdminRepository,
        "get_admin",
        return_value=Admin(
            id=database["id"],
            login_name=database["login_name"],
            password=database["password"],
            nickname=database["nickname"],
        ),
    )
    verify_password_mock_function = mocker.patch.object(
        AuthManager, "verify_password", return_value=False
    )
    create_access_token_mock_function = mocker.patch.object(
        AuthManager, "create_access_token", return_value="jwt_token"
    )

    response = client.post("/admin/api/v1/auth/login", json=body)

    get_admin_mock_function.assert_called_once_with(body["login_name"])
    verify_password_mock_function.assert_called_once_with(
        body["password"], database["password"]
    )
    create_access_token_mock_function.assert_not_called()

    assert response.status_code == 401
    assert response.json()["detail"] == "Not Authorized"
