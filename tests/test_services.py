from pathlib import Path
from fs_agent.services.filesystem import FileSandbox
from fs_agent.services.calculator import CalculatorService

def test_calculator():
    calc = CalculatorService()
    assert calc.evaluate("2+2") == 4.0

def test_filesystem(tmp_path: Path):
    fs = FileSandbox(tmp_path)
    # create & read
    p = fs.create_file("hello.txt", "hi")
    assert Path(p).exists()
    assert fs.read_file("hello.txt") == "hi"
    # list_dir not empty
    assert "hello.txt" in fs.list_dir(".", tree=False)
    # delete
    fs.delete_file("hello.txt")
    assert "empty" in fs.list_dir(".", tree=False)
