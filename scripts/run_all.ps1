# 1) Ollama doit déjà être installé
Start-Process powershell -ArgumentList "-NoExit", "ollama serve"

Start-Process powershell -ArgumentList "-NoExit", "uvicorn fog_server:app --host 0.0.0.0 --port 8001 --reload"
Start-Process powershell -ArgumentList "-NoExit", "uvicorn gateway_api:app --host 0.0.0.0 --port 8000 --reload"

Start-Process powershell -ArgumentList "-NoExit", "cd pwa_app; python -m http.server 5173"
# Option Streamlit :
# Start-Process powershell -ArgumentList "-NoExit", "streamlit run streamlit_app.py"
