"""
View for the navigation panels
"""

from typing import Optional

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton)

from QuickSeg.view.panel import Panel


class NavigationPanel(Panel):

    def __init__(self, label: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        selection_label = QLabel(label + ": ")
        self.current_index_edit = QLineEdit()
        self.max_index_label = QLabel()
        self.previous_button = QPushButton("<")
        self.next_button = QPushButton(">")

        self.current_index_edit.setFixedWidth(40)
        self.max_index_label.setFixedWidth(30)
        self.previous_button.setFixedWidth(20)
        self.next_button.setFixedWidth(20)

        navigation_layout = QHBoxLayout()
        navigation_layout.addWidget(selection_label)
        navigation_layout.addWidget(self.current_index_edit)
        navigation_layout.addWidget(self.max_index_label)
        navigation_layout.addWidget(self.previous_button)
        navigation_layout.addWidget(self.next_button)

        self.setLayout(navigation_layout)

    def get_current_index(self) -> Optional[int]:

        current_index_text = self.current_index_edit.text()

        # Try converting text to int
        try:
            current_index = int(current_index_text)

        except ValueError:
            # Invalid value
            return None

        # Make index 0-based
        return current_index - 1

    def set_current_index(self, index: Optional[int]):

        if index is None:
            # No text
            self.current_index_edit.setText("")
        else:
            # Make index 1-based
            self.current_index_edit.setText(str(index+1))

    def set_max_index(self, max_index: int):

        # Make max index 1-based
        self.max_index_label.setText('/ ' + str(max_index+1))
