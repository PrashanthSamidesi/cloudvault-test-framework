import requests


def test_api_GET():
    response = requests.get("https://jsonplaceholder.typicode.com/posts/1")
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200


def test_api_POST():
    data = {
        "title": "foo",
        "body": "bar",
        "userId": 100
    }
    response = requests.post("https://jsonplaceholder.typicode.com/posts",
                             json=data)
    print(response.status_code)
    print(response.json())
    assert response.status_code == 201
    assert response.json()["userId"] == 100


def test_api_PUT():
    data = {
        "id": 1,
        "title": "foo",
        "body": "bar",
        "userId": 1
    }
    response = requests.put("https://jsonplaceholder.typicode.com/posts/1",
                            json=data)
    print(response.status_code)
    print(response.json())
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_api_DELETE():
    response = requests.delete("https://jsonplaceholder.typicode.com/posts/1")
    print(response.status_code)
    assert response.status_code == 200


def test_api_LOGIN():
    login = {
        "username": "emilys",
        "password": "emilyspass"
    }
    response = requests.post("https://dummyjson.com/auth/login", json=login)
    assert response.status_code == 200
    assert "accessToken" in response.json()

    accessToken = response.json()["accessToken"]
    headers = {
        "Authorization": f"Bearer {accessToken}"
    }

    response = requests.get("https://dummyjson.com/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "emilys"
    assert "email" in response.json()
