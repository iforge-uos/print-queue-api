from print_api import create_app
from conftest import check_response


def test_config():
    assert not create_app().testing
    assert create_app("testing").testing


def test_451(app, client):
    response = client.make_request('get', "/api/v1/misc/legal")
    check_response(res=response, exp_status_code=451, exp_details=None, exp_extra_info="Pipis Room")


def test_418(app, client):
    response = client.make_request('get', "/api/v1/misc/toast")
    check_response(res=response, exp_status_code=418, exp_details=None, exp_extra_info="sweet cheeks")
