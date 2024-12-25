"""
Light-weight segmentation application
"""

import sys

from PyQt5.QtWidgets import QApplication

from QuickSeg.model.model import Model
from QuickSeg.view.main_view import MainView
from QuickSeg.controller.main_controller import MainController

# TODO: Fix segmentation fault when closing GUI from an interpreter


def _process_arguments(args):

    if args is None:
        # Called from an interactive session with no arguments
        dicom_content = None

    elif isinstance(args, str):
        # Called from an interactive session with an argument
        dicom_content = args

    elif isinstance(args, list):

        if len(args) == 0:

            # Called from the command line with no arguments
            dicom_content = None
        else:
            # Called from the command line with an argument
            dicom_content = args[0]

    else:
        raise ValueError("Invalid arguments")

    return dicom_content


def main(args=None):
    """Open quick_seg application"""

    app = QApplication([])

    model = Model()

    view = MainView()
    view.show()

    controller = MainController(model=model, view=view)

    content_file_path = _process_arguments(args)

    if content_file_path is not None:

        model.load_dicom_dir_content(content_file_path)

        # TODO: Make this unnecessary
        controller._series_selection_controller._refresh_series_list()

    # TODO: Make this unnecessary
    controller._display_controller.refresh_image()

    app.exec()


if __name__ == "__main__":

    # TODO: Make this work more smootly when called from an
    #       interactive session instead of the command line
    main(sys.argv[1:])
