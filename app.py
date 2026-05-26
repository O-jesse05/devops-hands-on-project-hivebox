import sys

# 1. Manually define the Semantic Version as requested
__version__ = "0.0.1"

def print_version_and_exit():
    """Prints the current application version and terminates."""
    print(f"HiveBox App Version: {__version__}")
    sys.exit(0)  # 0 means the program closed successfully with no errors

# This ensures the function runs immediately when the file is executed
if __name__ == "__main__":
    print_version_and_exit()