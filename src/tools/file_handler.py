import pandas as pd
import os


def load_csv(file_path: str) -> dict:
    """Load and validate a CSV file. Return basic info."""
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}"}

    try:
        df = pd.read_csv(file_path)

        if df.empty:
            return {"success": False, "error": "CSV file is empty"}

        info = {
            "success": True,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict(),
            "sample_rows": df.head(3).to_string(),
        }
        return info

    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Test with a sample CSV
    import tempfile
    sample = "name,age,salary\nAlice,30,70000\nBob,25,50000\nCharlie,35,90000\n"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(sample)
        tmp = f.name

    result = load_csv(tmp)
    print(f"Success: {result['success']}")
    print(f"Rows: {result['rows']}, Columns: {result['columns']}")
    print(f"Columns: {result['column_names']}")
    print(f"Types: {result['dtypes']}")
    print(f"Missing: {result['missing_values']}")
    os.unlink(tmp)