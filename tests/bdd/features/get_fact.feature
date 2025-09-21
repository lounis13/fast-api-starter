Feature: Get a random fact
  As an API consumer
  I want to retrieve a random fact
  So that I can see the system works end-to-end

  Scenario: Retrieve a random fact successfully
    Given the API is running
    And the fact use case is stubbed to return a fixed value
    When I call GET /v1/facts/random
    Then the response status should be 200
    And the response should contain the fixed fact
