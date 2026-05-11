import subprocess
import tempfile
import os


def execute_python_code(code: str, timeout: int = 30) -> dict:
    """Execute Python code in a subprocess and return stdout/stderr."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        f.flush()
        tmp_path = f.name

    try:
        result = subprocess.run(
            ['python3', tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(tmp_path)
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Code execution timed out after {timeout} seconds",
            "returncode": -1,
        }
    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    # Test basic execution
    result = execute_python_code("print('hello from executor')")
    print(f"Success: {result['success']}")
    print(f"Output: {result['stdout']}")

    # Test error handling
    result = execute_python_code("raise ValueError('test error')")
    print(f"\nError test - Success: {result['success']}")
    print(f"Stderr: {result['stderr']}")

    # Test pandas
    result = execute_python_code("import pandas as pd; print(pd.__version__)")
    print(f"\nPandas test - Output: {result['stdout']}")