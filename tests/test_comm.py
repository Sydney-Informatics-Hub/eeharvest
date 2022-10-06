from eeharvest import comm


def test_msg_info(capsys):
    comm.msg_info("The 7-th Fibonacci number is 13")
    captured = capsys.readouterr()
    assert "Fibonacci" in captured.out
