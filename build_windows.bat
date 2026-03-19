@echo off
echo Installing build dependencies...
pip install pyinstaller

echo.
echo Building EgyptianHoroscope.exe...
pyinstaller --onefile --windowed ^
    --name "EgyptianHoroscope" ^
    --hidden-import "app.systems.egyptian" ^
    --hidden-import "app.ai.generator" ^
    --hidden-import "app.systems.western" ^
    --hidden-import "app.systems.vedic" ^
    --hidden-import "app.systems.chinese" ^
    --hidden-import "dotenv" ^
    --hidden-import "anthropic" ^
    gui.py

echo.
echo Done! Find EgyptianHoroscope.exe in the dist\ folder.
echo.
echo Place your .env file (with ANTHROPIC_API_KEY) next to the .exe,
echo or the app will prompt you for the key on first launch.
pause
