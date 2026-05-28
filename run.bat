@echo off
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
"C:\Users\25288\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run app.py
