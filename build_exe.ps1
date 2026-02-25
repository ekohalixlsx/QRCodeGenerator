python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller --noconsole --onefile --name QR_Etiket_PDF --icon QrCode.ico --add-data "QrCode.ico;." app_gui.py
