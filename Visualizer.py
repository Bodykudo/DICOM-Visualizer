import vtk


class Visualizer:
    def __init__(
        self,
        folder,
        mode,
        ambient=0.1,
        diffuse=0.9,
        specular=0.2,
        specular_power=10.0,
        isovalue=500,
        color=(0.0, 0.0, 1.0),
    ):
        self.folder = folder
        self.mode = mode
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.specular_power = specular_power
        self.isovalue = isovalue
        self.reader = vtk.vtkDICOMImageReader()
        self.color = color

    def read_data(self):
        # Read DICOM data
        self.reader.SetDirectoryName(self.folder)
        self.reader.Update()

    def raycast_rendering(self):
        # Create volume mapper
        volume_mapper = vtk.vtkSmartVolumeMapper()
        volume_mapper.SetBlendModeToComposite()
        volume_mapper.SetRequestedRenderModeToGPU()
        volume_mapper.SetInputData(self.reader.GetOutput())

        # Create volume property
        volume_property = vtk.vtkVolumeProperty()
        volume_property.ShadeOn()
        volume_property.SetInterpolationTypeToLinear()
        volume_property.SetAmbient(self.ambient)
        volume_property.SetDiffuse(self.diffuse)
        volume_property.SetSpecular(self.specular)
        volume_property.SetSpecularPower(self.specular_power)

        # Set gradient opacity
        gradient_opacity = vtk.vtkPiecewiseFunction()
        gradient_opacity.AddPoint(0.0, 0.0)
        gradient_opacity.AddPoint(2000.0, 1.0)
        volume_property.SetGradientOpacity(gradient_opacity)

        # Set scalar opacity
        scalar_opacity = vtk.vtkPiecewiseFunction()
        scalar_opacity.AddPoint(-800.0, 0.0)
        scalar_opacity.AddPoint(-750.0, 1.0)
        scalar_opacity.AddPoint(-350.0, 1.0)
        scalar_opacity.AddPoint(-300.0, 0.0)
        scalar_opacity.AddPoint(-200.0, 0.0)
        scalar_opacity.AddPoint(-100.0, 1.0)
        scalar_opacity.AddPoint(1000.0, 0.0)
        scalar_opacity.AddPoint(2750.0, 0.0)
        scalar_opacity.AddPoint(2976.0, 1.0)
        scalar_opacity.AddPoint(3000.0, 0.0)
        volume_property.SetScalarOpacity(scalar_opacity)

        # Set color transfer function
        color = vtk.vtkColorTransferFunction()
        color.AddRGBPoint(-750.0, *self.color)
        color.AddRGBPoint(-350.0, *self.color)
        color.AddRGBPoint(-200.0, *self.color)
        color.AddRGBPoint(2750.0, *self.color)
        color.AddRGBPoint(3000.0, *self.color)
        volume_property.SetColor(color)

        # Create volume
        volume = vtk.vtkVolume()
        volume.SetMapper(volume_mapper)
        volume.SetProperty(volume_property)

        # Return volume
        return volume

    def surface_rendering(self):
        # Create surface extraction filter (marching cubes)
        surface_extractor = vtk.vtkMarchingCubes()
        surface_extractor.SetInputData(self.reader.GetOutput())
        surface_extractor.SetValue(0, self.isovalue)

        # Create mapper and actor for the surface
        surface_mapper = vtk.vtkPolyDataMapper()
        surface_mapper.SetInputConnection(surface_extractor.GetOutputPort())
        surface_mapper.ScalarVisibilityOff()

        surface_actor = vtk.vtkActor()
        surface_actor.SetMapper(surface_mapper)
        surface_actor.GetProperty().SetColor(*self.color)

        # Return surface actor
        return surface_actor

    def render(self):
        self.read_data()

        # Create renderer and render window
        renderer = vtk.vtkRenderer()
        renderer.SetBackground(0.1, 0.2, 0.3)

        if self.mode == "raycast":
            # Add volume to renderer
            volume = self.raycast_rendering()
            renderer.AddVolume(volume)
        elif self.mode == "surface":
            # Add surface actor to renderer
            surface_actor = self.surface_rendering()
            renderer.AddActor(surface_actor)

        renderer.ResetCamera()
        return renderer
