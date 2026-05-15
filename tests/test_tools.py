import os
import tempfile
from src.tools.code_executor import execute_python_code
from src.tools.file_handler import load_csv


def test_execute_valid_code():
    result = execute_python_code("print('hello')")
    assert result["success"] is True
    assert "hello" in result["stdout"]


def test_execute_invalid_code():
    result = execute_python_code("raise ValueError('test')")
    assert result["success"] is False
    assert "ValueError" in result["stderr"]


def test_execute_timeout():
    result = execute_python_code("import time; time.sleep(10)", timeout=2)
    assert result["success"] is False
    assert "timed out" in result["stderr"]


def test_load_valid_csv():
    sample = "a,b\n1,2\n3,4\n"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample)
        tmp = f.name
    result = load_csv(tmp)
    assert result["success"] is True
    assert result["rows"] == 2
    assert result["columns"] == 2
    os.unlink(tmp)


def test_load_missing_file():
    result = load_csv("/nonexistent/path.csv")
    assert result["success"] is False


def test_load_empty_csv():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("")
        tmp = f.name
    result = load_csv(tmp)
    assert result["success"] is False
    os.unlink(tmp)