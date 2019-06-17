# Generate a structured grid mesh (explicit geometry, implied topology)
# Output will be a vtkStructuredGrid, with Cartesian coordinates, but
# with a spherical geometry.

# This follows the mathematical convetion of
# (rho, theta, phi)
# rho -   radius             [0, inf)
# theta - azimuthal angle    [0, 360]
# phi   - zenithal angle     [0, 180]

# For physics convention - swap theta and phi
# For horizonatal celestial convention - zenith is the complement of elevation

# Hard coding everything to start, because frankly I'm not seeing a really
# good way to do everything I want off the bat... in particular regarding
# letting users input using one of the other conventions...
from vtk import *
from math import cos, sin, pi, radians

def spherical2cartesian(r, theta, phi):
    # assumes theta=azimuth, phi=zenith
    x = r * cos(radians(theta)) * sin(radians(phi))
    y = r * sin(radians(theta)) * sin(radians(phi))
    z = r * cos(radians(phi))
    return x, y, z

class SphericalMesh:
    def __init__(self, convention='math'):
        self._convention = convention
        self._min_radius = 0.0
        tmpscale = 3
        self._max_radius = 10000.0 / tmpscale 
        self._radial_res = 556 / tmpscale
        self._delta_radius = float((self._max_radius - self._min_radius)/(self._radial_res - 1))
        self._min_azimuth = 90.0
        self._max_azimuth = 210.0
        self._azimuthal_res = 224
        self._delta_azimuth = float((self._max_azimuth - self._min_azimuth)/(self._azimuthal_res - 1))
        self._min_zenith = 80.0
        self._max_zenith = 90.0
        self._zenithal_res = 21
        self._delta_zenith = float((self._max_zenith - self._min_zenith)/(self._zenithal_res - 1))
        self._sgrid = vtkStructuredGrid()

    def createStructuredGrid(self):
        self._sgrid.SetDimensions([self._radial_res, self._azimuthal_res, self._zenithal_res])
        pts = vtkPoints()

        for k in range(self._zenithal_res):
            for j in range(self._azimuthal_res):
                for i in range(self._radial_res):
                    r = self._min_radius + i * self._delta_radius
                    theta = self._min_azimuth + j * self._delta_azimuth
                    phi = self._min_zenith + k * self._delta_zenith
                    x, y, z = spherical2cartesian(r, theta, phi)
                    pts.InsertNextPoint([x, y, z])
        self._sgrid.SetPoints(pts)

    def writeLegacyStructuredGrid(self, filename):
        writer = vtkStructuredGridWriter()
        writer.SetFileName(filename)
        writer.SetInputData(self._sgrid)
        writer.Write()

    def writeXMLStructuredGrid(self, filename):
        writer = vtkXMLStructuredGridWriter()
        writer.SetFileName(filename)
        writer.SetInputData(self._sgrid)
        writer.Write()


if __name__=='__main__':
    mesh = SphericalMesh()
    mesh.createStructuredGrid()
    mesh.writeXMLStructuredGrid('resample_3KM_radius.vts')
