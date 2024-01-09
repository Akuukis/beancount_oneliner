Feature: Basics
  Background: default
    Given the config:
      {}
    Given the history:
      1990-01-01 open Income:Test
      1990-01-01 open Assets:Cash

  Scenario: Parse simple example
    When the transaction is processed:
      1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Description goes here *"

    Then should not error
    Then the transaction should be modified to:
      1999-12-31 * "Description goes here" #NoteToTx
        Income:Test  -16.18 EUR
        Assets:Cash   16.18 EUR
