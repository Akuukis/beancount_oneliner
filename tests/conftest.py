# pylint: disable=missing-function-docstring,implicit-str-concat
from pytest import fixture
from pytest_bdd import given, when, then, parsers

from beancount.core.compare import hash_entry
from beancount.loader import load_string
from beancount.parser import printer
from beancount_plugin_utils import test_utils
from context import oneliner


@fixture
def input_txns():
    """
    A list of parsed entries after processing history and transaction WITHOUT the plugin.
    """
    return []


@fixture
def output_txns():
    """
    A list of parsed entries after processing history and transaction WITH the plugin.
    """
    return []


@fixture
def errors():
    """
    A list of errors, if any, after processing history and transaction WITH the plugin.
    """
    return []


@given(parsers.parse("the config:" "{config}"), target_fixture="config")
def given_config(config):
    config_sanitized = config.strip() + '"\n'
    return config_sanitized


@given(parsers.parse("the history:" "{history}"), target_fixture="history")
def given_history(history):
    history_sanitized = history.strip() + "\n"
    return history_sanitized


@when(parsers.parse("transactions are processed:" "{input_txn_text}"))
@when(parsers.parse("the transaction is processed:" "{input_txn_text}"))
def is_processed(input_txns, errors, config, input_txn_text, history, output_txns):
    config_pad = "\n" * config.count("\n")
    input_txns[:], _, _ = load_string(config_pad + history + input_txn_text)
    print("\nInput (full & raw):\n------------------------------------------------")
    full_text = 'plugin "beancount_oneliner.oneliner" "' + config + history + input_txn_text
    print(full_text + "\n")
    output_txns[:], errors[:], _ = load_string(full_text)
    print("\nOutput (Transactions):\n------------------------------------------------\n")
    for txn in output_txns:
        print(printer.format_entry(txn))
    print("\nOutput (Errors):\n------------------------------------------------\n")
    for error in errors:
        print(printer.format_error(error))


@then(parsers.parse("the transaction should be modified to:" "{correctly_modified_txn_text}"))
def original_txn_modified(input_txns, output_txns, config, history, correctly_modified_txn_text):
    # Get modified original transaction from output of plugin
    # The modified originial transaction will be the last in the list of output transactions
    try:
        modified_lineno = output_txns[-1].meta["lineno"]
        modified_filename = output_txns[-1].meta["filename"]
        modified_txn = test_utils.strip_flaky_meta(output_txns[-1])
    except IndexError as error:
        raise error
    # Get correctly modified original transaction from feature file
    try:
        config_pad = "\n" * config.count("\n")
        correctly_modified_txn_full = load_string(config_pad + history + correctly_modified_txn_text)[0][-1]
        expected_lineno = correctly_modified_txn_full.meta["lineno"]
        expected_filename = correctly_modified_txn_full.meta["filename"]
        correctly_modified_txn = test_utils.strip_flaky_meta(correctly_modified_txn_full)
    except IndexError as error:
        raise error

    print(" ; RECEIVED:\n", printer.format_entry(modified_txn))
    print(" ; EXPECTED:\n", printer.format_entry(correctly_modified_txn))

    # Compare strings instead of hashes because that's an easy way to exclude filename & lineno meta.

    try:
        print("RECEIVED:\n", modified_txn)
        print("EXPECTED:\n", correctly_modified_txn)
        assert hash_entry(modified_txn) == hash_entry(correctly_modified_txn)
    except AssertionError as e:
        # Rethrow as a nicely formatted diff
        assert printer.format_entry(modified_txn).strip() == correctly_modified_txn_text.strip()
        # But in case strings matches..
        raise AssertionError("Transactions do not match although their printed output is equal. See log output.") from e

    try:
        assert modified_lineno == expected_lineno
    except AssertionError as e:
        raise AssertionError("Transactions do not match only in their line numbers.") from e

    try:
        assert modified_filename == expected_filename
    except AssertionError as e:
        raise AssertionError("Transactions do not match only in their filenames.") from e


@then(parsers.parse("the original transaction should not be modified"))
def tx_not_modified(input_txns, output_txns):
    original_txn = test_utils.strip_flaky_meta(input_txns[-1])
    modified_txn = test_utils.strip_flaky_meta(output_txns[-1])
    try:
        assert hash_entry(original_txn) == hash_entry(modified_txn)
    except AssertionError as e:
        print("RECEIVED:", modified_txn)
        print("EXPECTED:", original_txn)
        # Rethrow as a nicely formatted diff
        assert printer.format_entry(modified_txn) == printer.format_entry(original_txn)
        # But in case strings matches..
        raise AssertionError("Transactions do not match although their printed output is equal. See log output.") from e


@then(parsers.parse("should not error"))
def not_error(errors):
    assert len(errors) == 0


@then(parsers.parse("should produce plugin error:" "{exception_text}"))
def plugin_error(input_txns, errors, exception_text):
    original_txn = input_txns[-1]
    assert len(errors) == 1
    expected_error = oneliner.PluginOnelinerParseError(original_txn.meta, exception_text.strip("\n"), original_txn)
    assert type(errors[0]) is type(expected_error)
    assert errors[0].message == expected_error.message
    assert test_utils.strip_flaky_meta(errors[0].entry) == test_utils.strip_flaky_meta(expected_error.entry)


@then(parsers.parse("should produce beancount error:" "{exception_text}"))
def beancount_error(input_txns, errors, exception_text, output_txns):
    original_txn = input_txns[-1]
    modified_txn = output_txns[-1]
    assert len(errors) == 1
    expected_error = oneliner.PluginOnelinerParseError(original_txn.meta, exception_text.strip("\n"), original_txn)
    assert errors[0].message == expected_error.message and errors[0].entry == modified_txn
