Feature: Basics
  Background: default
    Given the config:
      {}
    Given the history:
      1990-01-01 open Income:Test
      1990-01-01 open Assets:Cash

  Scenario: Simple example with one link
    When the transaction is processed:
      1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Description goes here ^link *"

    Then should not error
    Then the transaction should be modified to:
      1999-12-31 * "Description goes here" #NoteToTx ^link
        Income:Test  -16.18 EUR
        Assets:Cash   16.18 EUR

  Scenario: Two links
    When the transaction is processed:
      1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Description goes here ^link ^other *"

    Then should not error
    Then the transaction should be modified to:
      1999-12-31 * "Description goes here" #NoteToTx ^link ^other
        Income:Test  -16.18 EUR
        Assets:Cash   16.18 EUR
