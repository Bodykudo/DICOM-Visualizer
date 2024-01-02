from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QRadioButton,
    QSlider,
    QLabel,
    QFileDialog,
    QDoubleSpinBox,
    QColorDialog,
)
from PyQt6.QtCore import Qt, QCoreApplication

from Visualizer import Visualizer


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DICOM Visualizer")
        self.setFixedWidth(300)

        self.layout = QVBoxLayout(self)

        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.clicked.connect(self.select_folder)

        self.selected_folder_label = QLabel()
        self.selected_folder_label.setText("No folder selected")

        self.folder = ""

        self.raycast_button = QRadioButton("Raycast Rendering")
        self.surface_button = QRadioButton("Surface Rendering")

        self.raycast_button.setChecked(True)

        self.raycast_button.toggled.connect(self.toggle_inputs)
        self.surface_button.toggled.connect(self.toggle_inputs)

        self.ambient_input = QDoubleSpinBox()
        self.ambient_input.setValue(0.1)
        self.diffuse_input = QDoubleSpinBox()
        self.diffuse_input.setValue(0.9)
        self.specular_input = QDoubleSpinBox()
        self.specular_input.setValue(0.2)
        self.specular_power_input = QDoubleSpinBox()
        self.specular_power_input.setValue(10.0)

        self.isovalue_slider = QSlider(Qt.Orientation.Horizontal)
        self.isovalue_slider.setRange(100, 1000)
        self.isovalue_slider.valueChanged.connect(self.update_isovalue_label)

        self.isovalue_label = QLabel()
        self.isovalue_label.setText(f"Isovalue: {self.isovalue_slider.value()}")

        self.color_layout = QWidget()
        self.color_layout.setLayout(QHBoxLayout())

        self.color_label = QLabel("Pick a color:")
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 20)
        self.color_button.clicked.connect(self.pick_color)
        self.color_button.setStyleSheet("background-color: blue")
        self.color = (0.0, 0.0, 1.0)

        self.color_layout.layout().addWidget(self.color_label)
        self.color_layout.layout().addWidget(self.color_button)

        self.visualize_button = QPushButton("Visualize")
        self.visualize_button.setEnabled(False)
        self.visualize_button.clicked.connect(self.visualize)

        self.layout.addWidget(self.select_folder_button)
        self.layout.addWidget(self.selected_folder_label)
        self.layout.addWidget(self.raycast_button)
        self.layout.addWidget(self.surface_button)
        self.layout.addWidget(QLabel("Ambient:"))
        self.layout.addWidget(self.ambient_input)
        self.layout.addWidget(QLabel("Diffuse:"))
        self.layout.addWidget(self.diffuse_input)
        self.layout.addWidget(QLabel("Specular:"))
        self.layout.addWidget(self.specular_input)
        self.layout.addWidget(QLabel("Specular Power:"))
        self.layout.addWidget(self.specular_power_input)
        self.layout.addWidget(QLabel("Isovalue:"))
        self.layout.addWidget(self.isovalue_slider)
        self.layout.addWidget(self.isovalue_label)
        self.layout.addWidget(self.color_layout)
        self.layout.addWidget(self.visualize_button)

        self.toggle_inputs()
        self.center_on_screen()

    def center_on_screen(self):
        # Center the window on the screen
        screen = QCoreApplication.instance().screens()[0]
        screen_geometry = screen.geometry()
        self.move(
            int((screen_geometry.width() / 2) - (self.frameSize().width() / 2)),
            int((screen_geometry.height() / 2) - (self.frameSize().height() / 2)),
        )

    def select_folder(self):
        # Open a dialog to select a folder
        self.selected_folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if self.selected_folder:
            self.selected_folder_label.setText(self.selected_folder)
            self.visualize_button.setEnabled(True)

    def toggle_inputs(self):
        # Enable/disable inputs based on the selected rendering mode
        raycast_selected = self.raycast_button.isChecked()
        self.ambient_input.setEnabled(raycast_selected)
        self.diffuse_input.setEnabled(raycast_selected)
        self.specular_input.setEnabled(raycast_selected)
        self.specular_power_input.setEnabled(raycast_selected)
        self.isovalue_slider.setEnabled(not raycast_selected)

    def update_isovalue_label(self):
        # Update the isovalue label when the slider value changes
        self.isovalue_label.setText(f"Isovalue: {self.isovalue_slider.value()}")

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
            self.color = color.getRgbF()[:3]
            print(self.color)

    def visualize(self):
        # Get the current values of the inputs
        current_mode = "raycast" if self.raycast_button.isChecked() else "surface"
        current_ambient = self.ambient_input.value()
        current_diffuse = self.diffuse_input.value()
        current_specular = self.specular_input.value()
        current_specular_power = self.specular_power_input.value()
        current_isovalue = self.isovalue_slider.value()

        # Create a visualizer object
        visualizer = Visualizer(
            folder=self.selected_folder,
            mode=current_mode,
            ambient=current_ambient,
            diffuse=current_diffuse,
            specular=current_specular,
            specular_power=current_specular_power,
            isovalue=current_isovalue,
            color=self.color,
        )

        # Render the data
        visualizer.render()


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
