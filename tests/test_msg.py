from eeharvest import msg


def test_msg_info(capsys):
    msg.info("The 7-th Fibonacci number is 13")
    captured = capsys.readouterr()
    assert "The" in captured.out


def test_msg_dl(capsys):
    msg.dl("The 7-th Fibonacci number is 13")
    captured = capsys.readouterr()
    assert "Fibonacci" in captured.out


def test_msg_warn(capsys):
    msg.warn("The 7-th Fibonacci number is 13")
    captured = capsys.readouterr()
    assert "number" in captured.out


def test_msg_err(capsys):
    msg.err("The 7-th Fibonacci number is 13")
    captured = capsys.readouterr()
    assert "is" in captured.out


def test_msg_success(capsys):
    msg.success("The 7-th Fibonacci number is 13")
    captured = capsys.readouterr()
    assert "13" in captured.out


def test_spin():
    with msg.spin("Checking if spin is working") as s:
        out = "OK, spin works"
        s()
    assert out == "OK, spin works"
