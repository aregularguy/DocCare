"""PyInstaller entry point — avoids relative import issues."""
import sys
import os

# When running as a frozen .exe, add the exe's directory to path
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
    os.chdir(base_dir)
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_dir)

from src.main import main  # absolute import works fine from root

if __name__ == '__main__':
    main()
