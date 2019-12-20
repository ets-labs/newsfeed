@api
Feature: Newsfeed API tests

  Background: Clear all events and subscriptions
    Given delete all from "newsfeed/123/events/"
    And delete all from "newsfeed/124/subscriptions/"
    And delete all from "newsfeed/123/subscriptions/"

  Scenario: Check microservice status
    When get request to "status/" is received
    Then response status should be 200
    And response should contain "OK" status

  Scenario: Verify documentation
    When get request to "docs/" is received
    Then response status should be 200
    And response should contain documentation

  Scenario: Get empty result if there are no events
    When get request to "newsfeed/123/events/" is received
    Then response status should be 200
    And response should contain empty result

  Scenario: Get events
    Given post request to "newsfeed/123/events/" is received with body
      | key       | value      |
      | field_1   | some_data  |
      | field_2   | other_data |
      | field_etc | etc_data   |
    When get request to "newsfeed/123/events/" is received
    Then response status should be 200
    And response should include the event

  Scenario: Add events
    When post request to "newsfeed/123/events/" is received with body
      | key       | value      |
      | field_1   | some_data  |
      | field_2   | other_data |
      | field_etc | etc_data   |
    Then response status should be 202
    And response should include the event

  Scenario: Delete event
    Given post request to "newsfeed/123/events/" is received with body
      | key       | value      |
      | field_1   | some_data  |
      | field_2   | other_data |
      | field_etc | etc_data   |
    When delete request to "newsfeed/123/events/" with event id is received
    Then response status should be 204
    And this event should be absent

  Scenario: Get subscriptions
    Given post request to "newsfeed/123/subscriptions/" is received
      | key            | value |
      | to_newsfeed_id | 124   |
    When get request to "newsfeed/123/subscriptions/" is received
    Then response status should be 200
    And response should include the subscription

  Scenario: Add subscriptions
    When post request to "newsfeed/123/subscriptions/" is received
      | key            | value |
      | to_newsfeed_id | 124   |
    Then response status should be 200
    And response should include the subscription

  Scenario: Delete subscription
    Given post request to "newsfeed/123/subscriptions/" is received
      | key            | value |
      | to_newsfeed_id | 124   |
    When send delete request to "newsfeed/123/subscriptions/" with subscription id
    Then response status should be 204
    And get request to "newsfeed/123/subscriptions/" is received
    And response should contain empty result

  Scenario: Get subscribers if there are no subscriptions
    When get request to "newsfeed/1213/subscribers/subscriptions/" is received
    Then response status should be 200
    And response should contain empty result

  Scenario: Get event if subscription was deleted
    When post request to "newsfeed/123/events/" is received with body
      | key       | value      |
      | field_1   | some_data  |
      | field_2   | other_data |
      | field_etc | etc_data   |
    And post request to "newsfeed/124/subscriptions/" is received
      | key            | value |
      | to_newsfeed_id | 123   |
    And delete request to "newsfeed/123/subscriptions/" with event id is received
    And get request to "newsfeed/123/events/" is received
    Then response status should be 200
    And response should include the event


    # Negative test cases

  Scenario: Add events if there is no data key
    When post request to "newsfeed/123/events/" is received without data key
      | key       |
      | field_1   |
      | field_2   |
      | field_etc |
    Then response status should be 400

  Scenario: Add events with empty data
    When post request to "newsfeed/123/events/" is received with empty fields
    Then response status should be 400

  Scenario: Add events in incorrect format
    When post request to "newsfeed/123/events/" is received in incorrect type
      | key       | value      |
      | field_1   | some_data  |
      | field_2   | other_data |
      | field_etc | etc_data   |
    Then response status should be 400

  Scenario: Add subscription if there is no data key
    When post request to "newsfeed/123/subscriptions/" is received without data key
      | key       |
      | field_1   |
      | field_2   |
      | field_etc |
    Then response status should be 400

  Scenario: Add subscription with empty data
    When post request to "newsfeed/123/subscriptions/" is received with empty fields
    Then response status should be 400

  Scenario: Add subscription in incorrect format
    When post request to "newsfeed/123/subscriptions/" is received in incorrect type
      | key       | value      |
      | field_1   | some_data  |
      | field_2   | other_data |
      | field_etc | etc_data   |
    Then response status should be 400
