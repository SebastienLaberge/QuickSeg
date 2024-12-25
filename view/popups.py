"""
Creation of popup windows
"""

from PyQt5.QtWidgets import QMessageBox


def warning_popup(message: str):

    msg_box = QMessageBox(
        QMessageBox.Warning,
        "Warning",
        message)

    msg_box.exec()
