import json

from behave import *
from hamcrest import *
import requests


base_url = "http://127.0.0.1:8000/api/"


@given('delete all from "{endpoint}"')
def get_current_id(context, endpoint):
    context.response = requests.get(base_url + endpoint)
    response_json = context.response.json()
    current_list = response_json["results"]
    if current_list is not None:
        for item in current_list:
            current_id = item["id"]
            context.response = requests.delete(base_url+endpoint+current_id+"/")


@when('get request to "{endpoint}" is received')
@then('get request to "{endpoint}" is received')
def step_impl(context, endpoint):
    context.response = requests.get(base_url + endpoint)


@then('response status should be {status}')
def step_impl(context, status):
    assert_that(context.response.status_code, equal_to(int(status)))


@then('response should contain "OK" status')
def step_impl(context):
    response_json = context.response.json()
    assert_that(response_json["status"], contains_string("OK"))


@then('response should contain documentation')
def step_impl(context):
    assert context.response is not None


@then('response should contain empty result')
@given('response should contain empty result')
def step_impl(context):
    response_json = context.response.json()
    assert_that(response_json["results"], empty())


@given('post request to "{endpoint}" is received with body')
@when('post request to "{endpoint}" is received with body')
def step_impl(context, endpoint):
    data = json.dumps({"data": {row['key']: row['value'] for row in context.table}})
    context.response = requests.post(url=base_url + endpoint, data=data)
    context.event_id = context.response.json()["id"]


@given('post request to "{endpoint}" is received')
@when('post request to "{endpoint}" is received')
def step_impl(context, endpoint):
    data_subscription = json.dumps({row['key']: row['value'] for row in context.table})
    context.response = requests.post(url=base_url + endpoint, data=data_subscription)
    context.subscription_id = context.response.json()["id"]


@then('response should include the event')
def step_impl(context):
    response_json = context.response.json()
    if "results" in response_json:
        response_json = (context.response.json())["results"][0]
    else:
        response_json = context.response.json()
        assert len(context.event_id) == 36
        assert isinstance(response_json["newsfeed_id"], str)
        assert isinstance(response_json["first_seen_at"], int)
        assert response_json["parent_fqid"] is None
        assert_that(response_json["child_fqids"], empty())
        assert response_json["published_at"] is None


@then('response should include the subscription')
def step_impl(context):
    response_json = context.response.json()
    if "results" in response_json:
        response_json = (context.response.json())["results"][0]
    else:
        response_json = context.response.json()
        assert len(context.subscription_id) == 36
        assert response_json["newsfeed_id"] == "123"
        assert isinstance(response_json["subscribed_at"], int)


@when('delete request to "{endpoint}" with event id is received')
def step_impl(context, endpoint):
    context.response = requests.delete(base_url+endpoint+context.event_id+"/")


@then('this event should be absent')
def step_impl(context):
    response_json = context.response.text
    assert_that(response_json, empty())


@when('send delete request to "{endpoint}" with subscription id')
def step_impl(context, endpoint):
    context.response = requests.delete(base_url+endpoint+context.subscription_id+"/")


@when('post request to "{endpoint}" is received without data key')
def step_impl(context, endpoint):
    data = json.dumps([{"data": [row['key'] for row in context.table]}])
    context.response = requests.post(url=base_url + endpoint, data=data)


@when('post request to "{endpoint}" is received with empty fields')
def step_impl(context, endpoint):
    data = json.dumps({})
    context.response = requests.post(url=base_url + endpoint, data=data)


@when('post request to "{endpoint}" is received in incorrect type')
def step_impl(context, endpoint):
    data = json.dumps([{"data": {row['key']: row['value'] for row in context.table}}])
    context.response = requests.post(url=base_url + endpoint, data=data)
