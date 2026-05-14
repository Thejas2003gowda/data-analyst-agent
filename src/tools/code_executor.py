import subprocess
import tempfile
import os


def execute_python_code(code: str, timeout: int = 30, work_dir: str = None) -> dict:
    """Execute Python code in a subprocess and return stdout/stderr."""
    if work_dir is None:
        work_dir = os.getcwd()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=work_dir) as f:
        f.write(code)
        f.flush()
        tmp_path = f.name

    try:
        result = subprocess.run(
            ['python3', tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=work_dir
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
    result = execute_python_code("print('hello from executor')")
    print(f"Success: {result['success']}")
    print(f"Output: {result['stdout']}")