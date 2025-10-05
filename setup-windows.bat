@echo off
chcp 65001 > nul
echo.
echo 🚀 LocalSync - Starting Graphical Interface...
echo.
python -c "import localsync.cli; localsync.cli.main()" --gui
echo.
echo LocalSync has closed.
echo.
pause