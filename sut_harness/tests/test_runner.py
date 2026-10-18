from sut_harness.runner import HelloWorldTest, run_tests
from sut_harness.transports import LocalTransport


def test_hello_world_passes_on_local_transport():
    with LocalTransport() as transport:
        outcomes = run_tests(transport, [HelloWorldTest()])

    assert len(outcomes) == 1
    assert outcomes[0].passed


def test_hello_world_fails_on_unexpected_output():
    test = HelloWorldTest(command='echo "Goodbye"', expected="Hello, World!")
    with LocalTransport() as transport:
        outcomes = run_tests(transport, [test])

    assert len(outcomes) == 1
    assert not outcomes[0].passed
    assert "Hello, World!" in outcomes[0].detail


def test_custom_command_and_expected_string():
    test = HelloWorldTest(command='echo "firmware v1.2.3 ready"', expected="v1.2.3")
    with LocalTransport() as transport:
        outcomes = run_tests(transport, [test])

    assert outcomes[0].passed
