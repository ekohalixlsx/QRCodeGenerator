python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller --noconsole --onefile --name QR_Etiket_PDF --icon QR_icon_01.ico --add-data "QR_icon_01.ico;." app_gui.py
