import json


def mocked_requests_post(*args, **kwargs):
    with open('tests/fixtures/bad_auth.json', 'r') as f:
        bad_auth = json.load(f)

    with open('tests/fixtures/list_sites.json', 'r') as f:
        list_sites = json.load(f)

    with open('tests/fixtures/site_status.json', 'r') as f:
        site_status = json.load(f)

    with open('tests/fixtures/site_status_no_acl.json', 'r') as f:
        no_acl = json.load(f)

    with open('tests/fixtures/site_status_no_black_white_lists.json',
              'r') as f:
        no_bwl = json.load(f)

    class MockResponse:
        url = None

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://my.incapsula.com/api/prov/v1/sites/list' \
            and kwargs['data']['api_key'] == 'key' \
            and kwargs['data']['api_id'] == 'id':
        return MockResponse(bad_auth, 200)
    if args[0] == 'https://my.incapsula.com/api/prov/v1/sites/list' \
            and kwargs['data']['api_key'] == 'test_key' \
            and kwargs['data']['api_id'] == 'test_id':
        return MockResponse(list_sites, 200)
    if args[0] == 'https://my.incapsula.com/api/prov/v1/sites/status':
        return MockResponse(site_status, 200)
    if args[0] == 'https://my.incapsula.com/api/prov/v1/sites/configure/acl':
        kwargs['data']['res_message'] = 'OK'
        return MockResponse(kwargs['data'], 200)
    if args[0] == 'https://superbeef.com/sites/list':
        resp = MockResponse(None, 404)
        resp.url = 'https://superbeef.com/sites/list'
        return resp
    if args[0] == 'noacl/sites/status':
        return MockResponse(no_acl, 200)
    if args[0] == 'nobwl/sites/status':
        return MockResponse(no_bwl, 200)

