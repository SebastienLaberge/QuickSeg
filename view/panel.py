"""
Implementation of a panel (GUI subsection)
"""

from PyQt5.QtWidgets import QFrame


class Panel(QFrame):
    """
    Base class for panels containing a GUI subsection
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFrameShape(QFrame.StyledPanel)
