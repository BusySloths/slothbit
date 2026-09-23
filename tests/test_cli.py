from slothbit.cli import main


def test_no_arguments_prints_help(capsys):
    assert main([]) == 0

    output = capsys.readouterr().out
    assert "usage: slothbit" in output
    assert "doctor" in output
    assert "infer" in output
    assert "serve" in output
