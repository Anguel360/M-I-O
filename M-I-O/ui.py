import ctypes
import os
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QMessageBox, QComboBox, QLineEdit, QRadioButton, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
from utils import list_disks, format_disk_windows, make_disk_bootable, create_bootable_disk

class DiskOperationThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, iso_file, disk_letter, disk_name, partition_scheme):
        super().__init__()
        self.iso_file = iso_file
        self.disk_letter = disk_letter
        self.disk_name = disk_name
        self.partition_scheme = partition_scheme

    def run(self):
        try:
            # Formatea el disco y asigna el nombre
            format_disk_windows(self.disk_letter, self.disk_name, self.partition_scheme)
            # Hace el disco booteable
            make_disk_bootable(self.disk_letter)
            # Crea el medio de booteo
            create_bootable_disk(self.iso_file, self.disk_letter)
            self.finished.emit(True)
        except Exception as e:
            self.progress.emit(f"Error: {e}")
            self.finished.emit(False)

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def run_as_admin():
    if is_admin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

class BootTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.boot_label = QLabel("Crear Medio de Booteo")
        self.boot_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.iso_button = QPushButton("Seleccionar Imagen ISO")
        self.iso_button.setStyleSheet("background-color: #61afef; color: #ffffff; font-size: 16px; padding: 10px;")
        self.iso_button.clicked.connect(self.select_iso)

        self.disk_label = QLabel("Seleccionar Disco Destino")
        self.disk_label.setStyleSheet("font-size: 16px;")
        self.disk_combo = QComboBox()
        self.disk_combo.setStyleSheet("background-color: #3e4451; color: #ffffff; font-size: 16px; padding: 10px;")
        
        self.name_label = QLabel("Nombre del Disco")
        self.name_label.setStyleSheet("font-size: 16px;")
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet("background-color: #3e4451; color: #ffffff; font-size: 16px; padding: 10px;")
        
        self.partition_scheme_label = QLabel("Esquema de Partición")
        self.partition_scheme_label.setStyleSheet("font-size: 16px;")
        self.mbr_radio = QRadioButton("MBR")
        self.gpt_radio = QRadioButton("GPT")
        self.mbr_radio.setChecked(True)  # Por defecto seleccionamos MBR
        
        scheme_layout = QHBoxLayout()
        scheme_layout.addWidget(self.mbr_radio)
        scheme_layout.addWidget(self.gpt_radio)

        self.boot_button = QPushButton("Crear Medio de Booteo")
        self.boot_button.setStyleSheet("background-color: #98c379; color: #ffffff; font-size: 16px; padding: 10px;")
        self.boot_button.clicked.connect(self.create_bootable_disk)
        self.boot_button.setEnabled(False)

        layout.addWidget(self.boot_label)
        layout.addWidget(self.iso_button)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.disk_combo)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.partition_scheme_label)
        layout.addLayout(scheme_layout)
        layout.addWidget(self.boot_button)

        self.setLayout(layout)
        self.iso_file = None
        self.thread = None

    def select_iso(self):
        self.iso_file, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen ISO", "", "ISO Files (*.iso)")
        if self.iso_file:
            self.update_disk_list()
            self.boot_button.setEnabled(True)
        else:
            self.boot_button.setEnabled(False)

    def update_disk_list(self):
        self.disk_combo.clear()
        disks = list_disks()
        self.disk_combo.addItems(disks)

    def create_bootable_disk(self):
        if not self.iso_file:
            QMessageBox.warning(self, "Error", "Seleccionar archivo ISO.")
            return

        target_disk = self.disk_combo.currentText()
        if target_disk:
            disk_letter = target_disk.split()[0]
            disk_name = self.name_input.text()
            partition_scheme = 'GPT' if self.gpt_radio.isChecked() else 'MBR'

            self.boot_button.setEnabled(False)
            self.thread = DiskOperationThread(self.iso_file, disk_letter, disk_name, partition_scheme)
            self.thread.progress.connect(self.show_message)
            self.thread.finished.connect(self.on_finished)
            self.thread.start()
        else:
            QMessageBox.warning(self, "Error", "Seleccionar disco destino.")

    def show_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def on_finished(self, success):
        if success:
            QMessageBox.information(self, "Éxito", "Medio de booteo creado con éxito.")
        else:
            QMessageBox.critical(self, "Error", "Ocurrió un error durante el proceso.")
        self.boot_button.setEnabled(True)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Disk Utility")
        self.setStyleSheet("background-color: #282c34; color: #ffffff;")
        self.setFixedSize(800, 600)

        self.layout = QVBoxLayout()
        self.boot_tab = BootTab()

        self.layout.addWidget(self.boot_tab)
        self.setLayout(self.layout)

def main():
    try:
        app = QApplication([])
        window = MainWindow()
        window.show()
        app.exec_()
    except Exception as e:
        with open('error_log.txt', 'a') as f:
            f.write(f"{traceback.format_exc()}\n")
        QMessageBox.critical(None, "Error", f"Se ha producido un error. Consulta error_log.txt para más detalles.")

if __name__ == "__main__":
    if not run_as_admin():
        sys.exit()
    main()
