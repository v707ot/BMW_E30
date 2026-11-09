"""Render 3D previews (PNG) of both adapters via VTK offscreen rendering."""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

import adapter  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "renders")

VIEWS = {
    "iso": (35, 25),
    "top": (0, 89),
    "front": (0, 0),
}


def _render(solid, path: str, azim: float, elev: float) -> None:
    import vtk
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    tmp = tempfile.NamedTemporaryFile(suffix=".stl", delete=False)
    tmp.close()
    BRepMesh_IncrementalMesh(solid.wrapped, 0.08)
    StlAPI_Writer().Write(solid.wrapped, tmp.name)

    reader = vtk.vtkSTLReader()
    reader.SetFileName(tmp.name)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(reader.GetOutputPort())
    normals.SetFeatureAngle(40)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.62, 0.66, 0.72)
    actor.GetProperty().SetSpecular(0.4)
    actor.GetProperty().SetSpecularPower(28)

    ren = vtk.vtkRenderer()
    ren.AddActor(actor)
    ren.SetBackground(1, 1, 1)
    ren.SetBackground2(0.90, 0.93, 0.97)
    ren.GradientBackgroundOn()
    cam = ren.GetActiveCamera()
    ren.ResetCamera()
    cam.Azimuth(azim)
    cam.Elevation(elev)
    cam.Zoom(1.15)
    ren.ResetCameraClippingRange()

    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.AddRenderer(ren)
    win.SetSize(1100, 850)
    win.Render()
    w2i = vtk.vtkWindowToImageFilter()
    w2i.SetInput(win)
    w2i.Update()
    w = vtk.vtkPNGWriter()
    w.SetFileName(path)
    w.SetInputConnection(w2i.GetOutputPort())
    w.Write()
    os.unlink(tmp.name)


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for maker in (adapter.make_part1, adapter.make_part2):
        name = maker.__name__.replace("make_", "")
        solid = maker().val()
        for view, (az, el) in VIEWS.items():
            p = os.path.join(OUT, f"{name}_{view}.png")
            _render(solid, p, az, el)
            print("wrote", p)


if __name__ == "__main__":
    main()
