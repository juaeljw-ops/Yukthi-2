"""
Root entrypoint for Streamlit Community Cloud deployment.
Delegates to dashboard/app.py.
"""
import os
import sys
import runpy

root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

app_path = os.path.join(root_dir, "dashboard", "app.py")
runpy.run_path(app_path, run_name="__main__")
