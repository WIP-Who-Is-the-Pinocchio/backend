from src.admin.auth.auth_manager import AuthManager
from src.database.models import Admin
from src.database.repositories.admin_repository import AdminRepository


def test_admin_signup_success(client, mocker):
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

    body = {
        "login_name": "login_ID",
        "password": "wip-password",
        "nickname": "pinocchio",
    }
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
    check_uniqueness_mock_function = mocker.patch.object(
        AdminRepository, "check_uniqueness", return_value=True
    )
    hash_password_mock_function = mocker.patch.object(
        AuthManager, "hash_password", return_value="hashed"
    )
    create_admin_model_spy = mocker.spy(Admin, "create")

    body = {
        "login_name": "login_ID",
        "password": "short",
        "nickname": "pinocchio",
    }
    response = client.post("/admin/api/v1/auth/signup", json=body)

    check_uniqueness_mock_function.assert_not_called()
    hash_password_mock_function.assert_not_called()
    create_admin_model_spy.assert_not_called()

    assert response.status_code == 400
    assert (
        response.json()["detail"] == "The password must be at least 8 characters long."
    )


def test_admin_signup_with_duplicated_data(client, mocker):
    check_uniqueness_mock_function = mocker.patch.object(
        AdminRepository, "check_uniqueness", return_value=False
    )
    hash_password_mock_function = mocker.patch.object(
        AuthManager, "hash_password", return_value="hashed"
    )
    create_admin_model_spy = mocker.spy(Admin, "create")

    body = {
        "login_name": "login_ID",
        "password": "wip-password",
        "nickname": "pinocchio",
    }
    response = client.post("/admin/api/v1/auth/signup", json=body)

    check_uniqueness_mock_function.assert_called_once()
    hash_password_mock_function.assert_not_called()
    create_admin_model_spy.assert_not_called()

    assert response.status_code == 409
    assert response.json()["detail"] == "Both login_name and nickname should be unique."
