import json

from scheduler_service.manage import app
from tests import const


def test_user():
    _, resp = app.test_client.post(const.user_url,
                                   data=json.dumps({
                                       "name": "test",
                                       "password": "password",
                                       "email": "test@test.com"
                                   }))
    assert resp.status == 200

    _, resp = app.test_client.get(const.auth_token_url,
                                  params={
                                      "name": "test",
                                      "password": "00000000"
                                  })
    assert resp.status == 401

    _, resp = app.test_client.get(const.auth_token_url,
                                  params={
                                      "email": "test@test.com",
                                      "password": "password"
                                  })
    assert resp.status == 200

    _, resp = app.test_client.get(const.auth_token_url,
                                  params={
                                      "name": "test",
                                      "password": "password"
                                  })
    assert resp.status == 200

    token = resp.json['token']
    headers = {"Authorization": token}


    _, resp = app.test_client.get(const.user_url, headers=headers)
    assert resp.status == 200

    _, resp = app.test_client.patch(const.user_url,
                                    headers=headers,
                                    json={
                                        "name": "test1",
                                        "email": "test1@test.com"
                                    })
    assert resp.status == 200
    assert resp.json['email'] == 'test1@test.com'
    assert resp.json['name'] == 'test1'

    _, resp = app.test_client.delete(const.user_url, headers=headers)
    assert resp.status == 200


def test_401():
    _, resp = app.test_client.get(const.user_url)
    assert resp.status == 401

    _, resp == app.test_client.get(const.auth_token_url,
                                   params={
                                       'name': 'test10',
                                       'password': 'password'
                                   })
    assert resp.status == 401


def test_400():
    _, resp = app.test_client.get(const.auth_token_url,
                                  params={'password': 'password'})
    assert resp.status == 400
