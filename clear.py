import os
from typing import Union


def clear_pycache() -> str:
    dir: str = os.path.join(os.getcwd(), 'hades')

    try:
        pycache_paths: list[str] = [os.path.join(
            root, "__pycache__") for root, dirs, files in os.walk(dir) if "__pycache__" in dirs]

        for pycache_path in pycache_paths:
            print(f"Removing {pycache_path}")
            [os.unlink(item) if os.path.isfile(item) or os.path.islink(item) else os.rmdir(
                item) for item in [os.path.join(pycache_path, i) for i in os.listdir(pycache_path)]]
            os.rmdir(pycache_path)

        return "Cleanup completed."
    except Exception as e:
        return f"Error: {str(e)}"


result: Union[str, None] = clear_pycache()
print(result)
