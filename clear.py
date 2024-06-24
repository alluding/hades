import os
from typing import Union


def clear_pycache() -> str:
    try:
        pycache_paths = [
            os.path.join(root, d)
            for root, dirs, _ in os.walk(os.getcwd())
            for d in dirs if d == "__pycache__"
        ]

        for pycache_path in pycache_paths:
            print(f"Removing {pycache_path}")
            items = [
                os.path.join(pycache_path, item)
                for item in os.listdir(pycache_path)
            ]

            for item in items:
                if os.path.isfile(item) or os.path.islink(item):
                    os.unlink(item)

            os.rmdir(pycache_path)

        return "Cleanup completed."
    except Exception as e:
        return f"Error: {e}"


result: Union[str, None] = clear_pycache()
print(result)
