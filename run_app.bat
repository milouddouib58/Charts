@echo off
chcp 65001
cls
echo ==========================================
echo    تثبيت المكتبات المطلوبة (Installing Libraries)...
echo ==========================================
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] حدث خطأ أثناء التثبيت. تأكد من اتصالك بالإنترنت.
    pause
    exit /b
)

echo.
echo ==========================================
echo    تشغيل التطبيق (Starting App)...
echo ==========================================
streamlit run app.py
pause
