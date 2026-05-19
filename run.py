import subprocess
import time
import os

# 1. Sabse pehle FastAPI backend ko background mein start karein
print("Starting FastAPI Backend...")
backend_process = subprocess.Popen([
    "uvicorn", "api:app", "--host", "127.0.0.1", "--port", "8000"
])

# 2. 5 seconds wait karein taake backend sahi se load ho jaye
time.sleep(5)

# 3. Ab Streamlit frontend ko start karein
print("Starting Streamlit Frontend...")
os.system("streamlit run app.py --server.port 8501")