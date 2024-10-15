from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from MainWidget import MainWidget
from ChoosePortWidget import ChoosePortWidget
import sys, serial

app = QApplication(sys.argv)

while True:
    # creating window of choosing port
    window1 = ChoosePortWidget()
    status = window1.exec()


    if status != QDialog.DialogCode.Accepted:
        sys.exit(-1)
    
    # creating main window
    try:
        main_widget = MainWidget(window1.device_name, window1.device_speed)
        main_widget.show()
    except serial.SerialException:
        QMessageBox.critical(main_widget,"Error", "Error with COM port read.")
        continue

    break

return_code = app.exec()
sys.exit(return_code)