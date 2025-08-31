Feature: Basics
  Background: default
    Given the config:
      {}
    Given the history:
      1990-01-01 open Income:Test
      1990-01-01 open Assets:Cash

  Scenario: Simple example with one tag
    When the transaction is processed:
      1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Description goes here *" #tag

    Then should not error
    Then the transaction should be modified to:
      1999-12-31 * "Description goes here" #NoteToTx #tag
        Income:Test  -16.18 EUR
        Assets:Cash   16.18 EUR

  Scenario: Two tags
    When the transaction is processed:
      1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Description goes here *" #tag #second

    Then should not error
    Then the transaction should be modified to:
      1999-12-31 * "Description goes here" #NoteToTx #tag #second
        Income:Test  -16.18 EUR
        Assets:Cash   16.18 EUR

  Scenario: Two tags backward-compatible from beancount 2
    When the transaction is processed:
      1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Description goes here #tag #second *"

    Then should not error
    Then the transaction should be modified to:
      1999-12-31 * "Description goes here" #NoteToTx #tag #second
        Income:Test  -16.18 EUR
        Assets:Cash   16.18 EUR

  Scenario: Three tags mixed backward-compatible from beancount 2
    When the transaction is processed:
      1999-12-31 note Assets:Cash "Income:Test -16.18 EUR * Description goes here #tag #second *" #third

    Then should not error
    Then the transaction should be modified to:
      1999-12-31 * "Description goes here" #NoteToTx #tag #second #third
        Income:Test  -16.18 EUR
        Assets:Cash   16.18 EUR
