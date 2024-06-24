from typing import Union, List
import os

def clear_pycache() -> None:
    """
    Clean all pycache files.
    """
    
    try:
        pycache_paths: List[str] = [
            os.path.join(root, d)
            for root, dirs, _ in os.walk(os.getcwd())
            for d in dirs if d == "__pycache__"
        ]

        for pycache in pycache_paths:
            print(f"Removing {pycache}")
            
            items: List[str] = [
                os.path.join(pycache, item)
                for item in os.listdir(pycache)
            ]

            for item in items:
                if os.path.isfile(item) or os.path.islink(item):
                    os.unlink(item)

            os.rmdir(pycache)

        print("Cleanup completed.")
    except Exception as e:
        print(f"Error: {e}")

clear_pycache()
