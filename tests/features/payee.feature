Feature: Basics
  Background: default
    Given the config:
      {}
    Given the history:
      1990-01-01 open Income:Test
      1990-01-01 open Assets:Cash

  Scenario: Simple example
    When the transaction is processed:
      1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Workshop | Description goes here *"

    Then should not error
    Then the transaction should be modified to:
      1999-12-31 * "Workshop" "Description goes here" #NoteToTx
        Income:Test  -16.18 EUR
        Assets:Cash   16.18 EUR

  Scenario: Payee with spaces and special characters
    When the transaction is processed:
      1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Vecā tēva darbnīca! | Description goes here *"

    Then should not error
    Then the transaction should be modified to:
      1999-12-31 * "Vecā tēva darbnīca!" "Description goes here" #NoteToTx
        Income:Test  -16.18 EUR
        Assets:Cash   16.18 EUR

  Scenario: With more pipes inside narration
    When the transaction is processed:
      1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Workshop | Weir|d description | goes here *"

    Then should not error
    Then the transaction should be modified to:
      1999-12-31 * "Workshop" "Weir|d description | goes here" #NoteToTx
        Income:Test  -16.18 EUR
        Assets:Cash   16.18 EUR
