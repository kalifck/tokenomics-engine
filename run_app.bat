@echo off
title Crypto Tokenomics Analyzer
echo ========================================================
echo     Starting Crypto Tokenomics Analyzer & Engine...
echo ========================================================
echo.
echo Running local web application on http://127.0.0.1:8501
echo Press Ctrl+C in this terminal window to stop the server.
echo.
python -m streamlit run app.py --server.address=127.0.0.1
pause
