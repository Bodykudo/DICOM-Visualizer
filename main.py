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
from PyQt6.QtGui import QColor
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from Visualizer import Visualizer
import os


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DICOM Visualizer")
        self.setFixedWidth(800)
        self.setFixedHeight(500)

        self.layout = QHBoxLayout(self)

        self.controls_layout = QVBoxLayout()

        # Create the controls for the folder selection
        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.clicked.connect(self.select_folder)

        self.selected_folder_label = QLabel()
        self.selected_folder_label.setText("No folder selected")

        self.selected_folder = None

        # Create the controls for the rendering mode
        self.raycast_button = QRadioButton("Raycast Rendering")
        self.surface_button = QRadioButton("Surface Rendering")

        self.raycast_button.setChecked(True)

        self.raycast_button.toggled.connect(self.toggle_inputs)
        self.surface_button.toggled.connect(self.toggle_inputs)

        # Create the controls for the raycast rendering
        self.ambient_input = QDoubleSpinBox()
        self.ambient_input.setValue(0.1)
        self.ambient_input.valueChanged.connect(lambda: self.visualize(in_place=True))
        self.diffuse_input = QDoubleSpinBox()
        self.diffuse_input.setValue(0.9)
        self.diffuse_input.valueChanged.connect(lambda: self.visualize(in_place=True))
        self.specular_input = QDoubleSpinBox()
        self.specular_input.setValue(0.2)
        self.specular_input.valueChanged.connect(lambda: self.visualize(in_place=True))
        self.specular_power_input = QDoubleSpinBox()
        self.specular_power_input.setValue(10.0)
        self.specular_power_input.valueChanged.connect(
            lambda: self.visualize(in_place=True)
        )

        # Create the controls for the surface rendering
        self.isovalue_slider = QSlider(Qt.Orientation.Horizontal)
        self.isovalue_slider.setRange(0, 1000)
        self.isovalue_slider.setValue(100)
        self.isovalue_slider.valueChanged.connect(self.update_isovalue_label)

        self.isovalue_label = QLabel()
        self.isovalue_label.setText(f"Isovalue: {self.isovalue_slider.value()}")

        # Create the controls for the color
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

        # Create the visualize button
        self.visualize_button = QPushButton("Visualize")
        self.visualize_button.setEnabled(False)
        self.visualize_button.clicked.connect(self.visualize)

        # Add the controls to the layout
        self.controls_layout.addWidget(self.select_folder_button)
        self.controls_layout.addWidget(self.selected_folder_label)
        self.controls_layout.addWidget(self.raycast_button)
        self.controls_layout.addWidget(self.surface_button)
        self.controls_layout.addWidget(QLabel("Ambient:"))
        self.controls_layout.addWidget(self.ambient_input)
        self.controls_layout.addWidget(QLabel("Diffuse:"))
        self.controls_layout.addWidget(self.diffuse_input)
        self.controls_layout.addWidget(QLabel("Specular:"))
        self.controls_layout.addWidget(self.specular_input)
        self.controls_layout.addWidget(QLabel("Specular Power:"))
        self.controls_layout.addWidget(self.specular_power_input)
        self.controls_layout.addWidget(QLabel("Isovalue:"))
        self.controls_layout.addWidget(self.isovalue_slider)
        self.controls_layout.addWidget(self.isovalue_label)
        self.controls_layout.addWidget(self.color_layout)
        self.controls_layout.addWidget(self.visualize_button)

        # Create the VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor()
        self.layout.addLayout(self.controls_layout)
        self.layout.addWidget(self.vtk_widget)

        # Set up the window
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
            folder_name = os.path.basename(self.selected_folder)
            self.selected_folder_label.setText(folder_name)
            self.visualize_button.setEnabled(True)
            self.visualize()

    def toggle_inputs(self):
        # Enable/disable inputs based on the selected rendering mode
        raycast_selected = self.raycast_button.isChecked()
        self.ambient_input.setEnabled(raycast_selected)
        self.diffuse_input.setEnabled(raycast_selected)
        self.specular_input.setEnabled(raycast_selected)
        self.specular_power_input.setEnabled(raycast_selected)
        self.isovalue_slider.setEnabled(not raycast_selected)
        if self.selected_folder:
            self.visualize()

    def update_isovalue_label(self):
        # Update the isovalue label when the slider value changes
        self.isovalue_label.setText(f"Isovalue: {self.isovalue_slider.value()}")
        if self.selected_folder:
            self.visualize(in_place=True)

    def pick_color(self):
        initial_color = QColor(*[int(c * 255) for c in self.color])
        color = QColorDialog.getColor(initial_color)
        if color.isValid():
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
            self.color = color.getRgbF()[:3]
            if self.selected_folder:
                self.visualize(in_place=True)

    def visualize(self, in_place=False):
        if self.selected_folder:
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

            # Get the current renderer
            render_window = self.vtk_widget.GetRenderWindow()
            current_renderer = render_window.GetRenderers().GetFirstRenderer()

            # Store the current camera settings
            if current_renderer:
                camera = current_renderer.GetActiveCamera()
                position = camera.GetPosition()
                focal_point = camera.GetFocalPoint()
                view_up = camera.GetViewUp()

            # Clear old data
            render_window.GetRenderers().RemoveAllItems()

            # Render the new data
            renderer = visualizer.render()

            # Apply the stored camera settings to the new renderer if update in place is enabled
            if current_renderer and in_place:
                new_camera = renderer.GetActiveCamera()
                new_camera.SetPosition(position)
                new_camera.SetFocalPoint(focal_point)
                new_camera.SetViewUp(view_up)

            # Set the background color and add the new renderer
            if not self.isDarkMode():
                renderer.SetBackground(0.9, 0.9, 0.9)
            render_window.AddRenderer(renderer)
            render_window.Render()

    def isDarkMode(self):
        """
        Checks if the application is in dark mode
        """
        widget = QWidget()
        color = widget.palette().color(QWidget().backgroundRole())
        brightness = color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114
        return brightness < 128


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
