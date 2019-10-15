# Converts a .hpl LiDAR scan output to VTK data
# - gates creates vtkPolyData vertex cells
# - rays creates vtkPolyData polyline cells
# - sweep creates vtkStructuredGrids
#
# - no time information is written out, this has to be figured out yet
# - User defined scans sweeps have suprious connecting cells between
#   the ends of adjacent (in time) sweeps. 
import sys
from math import radians, sin, cos, pi
import glob
import vtk
# Slight issue with VTK 8.2 random hiccup. If stuck, do not halt.
import argparse

class HPL:
    '''HPL data, right now, data from a single .hpl file, but could see
    combining multiple files into one object.'''
    def __init__(self, scanType, geomType, pitchAndRoll):
        self.headersize = 17
        self.header = {}
        self.scanType = scanType
        self.geomType = geomType
        self.pitchAndRoll = pitchAndRoll

        if geomType == 'rays' or geomType == 'gates':
            self.scan = vtk.vtkPolyData()
        elif geomType == 'sweep':
            self.scan = vtk.vtkStructuredGrid()

    def read_hpl_file(self, hplfilename):
        with open(hplfilename, 'r') as hplfile:
            self._read_header(hplfile)
            self._read_rays(hplfile)

    def _read_header(self, hplfile):
        '''HPL files appear to have a set, predictable header format of 17 lines.
        This function reads the values directly into a dict for later use.
    
        One thing to note is that the header is mix of descriptive data and
        descriptive text.

        The next thing to note is that delimiting and whitespaceing is not
        quite consistent.
        '''
        # grab header as list of strings

        # blah, vtkpython is python2 and was giving me some grief about
        # mixing iteration and readline file access.
        i = 0
        headertext = []
        while i < self.headersize:
            headertext.append(hplfile.readline().strip())
            i += 1

        #   lines 1 - 11 are descriptive data
        # Filename:              <str self-decription>
        # System ID:             <int hard coded to 100>
        # Number of gates:       <int discrete data locations along the beam>
        # Range gate length (m): <float distance between gates>
        # Gate length (pts):     <int no idea>
        # Pulses/ray:            <int literal number of emmissions?>

        # RHI and VAD files have --
        # No. of rays in file:   <int beams that were cast.>
        
        # User files have --
        # No. of waypoints in file: <int waypoints set by operator (not clear this used explicitly in file)

        # Scan type:             <str>
        # Focus Range:           <int no idea>
        # Start time:            <YYYYMMDD HH:MM:SS.SS>
        # Resolution (m/s):      <float no idea>

        for line in headertext[:11]:
            k, v = [x.strip() for x in line.split(':', 1)]
            self.header[k] = v

        self.header['Number of gates'] = int(self.header['Number of gates'])
        self.header['Range gate length (m)'] = float(self.header['Range gate length (m)'])
        self.header['Gate length (pts)'] = int(self.header['Gate length (pts)'])
        self.header['Pulses/ray'] = int(self.header['Pulses/ray'])

        if self.scanType in ['VAD', 'RHI', 'Stare']:
            self.header['No. of rays in file'] = int(self.header['No. of rays in file'])
        elif self.scanType == 'User':
            self.header['No. of waypoints in file'] = int(self.header['No. of waypoints in file'])

        self.header['Focus range'] = int(self.header['Focus range'])
        self.header['Resolution (m/s)'] = float(self.header['Resolution (m/s)'])

        #   lines 12 - 17 are comments, general info
        # 12. how to calculate altitude of measuement 
        # 13. description of what start of a ray sequence will contain
        # 14. ~~ C-style format specifiers for 1st line of ray sequence
        # 15. description of what rest of a ray sequence will contain
        # 16. ~~ C-style format specifiers for the next Num gates lines
        # 17. header delimiter of 4 asteriks 
        # These can be ignored, the important thing is that the file now
        # points to just past the header.

    def _read_rays(self, hplfile):
        '''
        ASSUMPTION - _read_header() has been called and the file handle is pointing
        to the correct spot in the file.
        Read the sequences of LiDAR beam data. These always start after the header on
        line 18.
        There are 'No. of rays in file' sections. 
        These have 1 initial line with:
        <time> <azimuth> <elevation> <pitch> <roll>
        Followed by 'Number of gates' lines of
        <gate ID> <doppler> <intensity> <beta>
        '''
        # a first pass would be to just grab the <azimuth> <elevation> and calculate
        # an x,y,z triple with
        # r = gate_ID * 'Range gate length (m)'
        # x = r*sin(elevation)*cos(azimuth)
        # y = r*sin(elevation)*sin(azimuth)
        # z = r*cos(elevation)

        gate_length = self.header['Range gate length (m)']
        num_gates = self.header['Number of gates']


        # these are locals because they get added to self.scan
        pts = vtk.vtkPoints()
        vts = vtk.vtkCellArray()
        
        dopplerScalars = vtk.vtkFloatArray()
        dopplerScalars.SetName('doppler')
        dopplerScalars.SetNumberOfComponents(1)

        intensityScalars = vtk.vtkFloatArray()
        intensityScalars.SetName('intensity')
        intensityScalars.SetNumberOfComponents(1)

        betaScalars = vtk.vtkFloatArray()
        betaScalars.SetName('beta')
        betaScalars.SetNumberOfComponents(1)

        gateIDScalars = vtk.vtkIntArray()
        gateIDScalars.SetName('gateID')
        gateIDScalars.SetNumberOfComponents(1)

        beamIDScalars = vtk.vtkIntArray()
        beamIDScalars.SetName('beamID')
        beamIDScalars.SetNumberOfComponents(1)

        azimuthScalars = vtk.vtkFloatArray()
        azimuthScalars.SetName('azimuth')
        azimuthScalars.SetNumberOfComponents(1)

        elevationScalars = vtk.vtkFloatArray()
        elevationScalars.SetName('elevation')
        elevationScalars.SetNumberOfComponents(1)

        if self.pitchAndRoll:
            pitchScalars = vtk.vtkFloatArray()
            pitchScalars.SetName('pitch')
            pitchScalars.SetNumberOfComponents(1)

            rollScalars = vtk.vtkFloatArray()
            rollScalars.SetName('roll')
            rollScalars.SetNumberOfComponents(1)
        
        beamID = 0
        
        # outer while is each beam
        while True:
            beam = hplfile.readline().strip()
            if not beam: break

            # beam header line
            time, azimuth, elevation, pitch, roll = [float(x) for x in beam.split()]
            razimuth, relevation = radians(azimuth), radians(elevation)
            rpitch, rroll = radians(pitch), radians(roll)

            # convert elevation to inclination
            inclination = pi/2 - relevation
            # gates along ray
            for g in range(num_gates):
                gate_ID, doppler, intensity, beta = hplfile.readline().strip().split()
                
                gateIDScalars.InsertNextValue(int(gate_ID))
                dopplerScalars.InsertNextValue(float(doppler))
                intensityScalars.InsertNextValue(float(intensity))
                betaScalars.InsertNextValue(float(beta))
                beamIDScalars.InsertNextValue(beamID) 
                azimuthScalars.InsertNextValue(azimuth)
                elevationScalars.InsertNextValue(elevation)
                if self.pitchAndRoll:
                    pitchScalars.InsertNextValue(pitch)
                    rollScalars.InsertNextValue(roll)
                # this behaves as: 
                # azimuth 0 is N and increases CW
                # elevation 0 is vertically straight up and increases towards ground
                # but what I want is
                # elevation 0 is horizontally and increases to 90 being straight up. 
                # IIUC wikipedia says this is the "horizontal" or "topocentric" coordinate
                # system in the family of celestial coordiantes.

                r = (int(gate_ID) + 1) * gate_length
                y = r * sin(inclination) * cos(razimuth)
                x = r * sin(inclination) * sin(razimuth)
                z = r * cos(inclination)
               
                if self.pitchAndRoll:
                    # blech, hand-transforms
                    pitchedy = y * cos(rpitch) - z * sin(rpitch)
                    pitchedz = y * sin(rpitch) + z * cos(rpitch)
                    y = pitchedy
                    z = pitchedz

                    rolledx = x * cos(rroll) + z * sin(rroll)
                    rolledz = -x * sin(rroll) + z * cos(rroll)
                    x = rolledx
                    z = rolledz
                
                pts.InsertNextPoint([x, y, z])
                

            beamID += 1 
            # could apply pitch and roll here, since they are beam-wise. 
            # pitch is absolute pitch around East-West axis (X)
            # > 0 means N tilted above S, so azimuth (-90,90) tilt up
            #   and azimuth(90, -90) tilt down
            # roll is absolute pitch around N-S axis (Y)
            # >0 means west tilted above E, so azimuth (180,0) tilt up
            #    and azimuth (0,180) tilt down.

            # for the life of me, not sure how to do this through VTK
            # VTK transforms are meant to act as pipeline filters, but
            # this is in the modeling stage...
            # hand distributing the matrix multiplication gives

    
        self.scan.SetPoints(pts)
        self.scan.GetPointData().AddArray(gateIDScalars)
        self.scan.GetPointData().AddArray(dopplerScalars)
        self.scan.GetPointData().AddArray(intensityScalars)
        self.scan.GetPointData().AddArray(betaScalars)
        self.scan.GetPointData().AddArray(beamIDScalars)
        self.scan.GetPointData().AddArray(azimuthScalars)
        self.scan.GetPointData().AddArray(elevationScalars)

        if self.pitchAndRoll:
            self.scan.GetPointData().AddArray(pitchScalars)
            self.scan.GetPointData().AddArray(rollScalars)

        # This creates separate vertex cells
        
        print("MVM: {}".format(pts.GetNumberOfPoints()))
        vts.InsertNextCell(pts.GetNumberOfPoints())
        for i in range(pts.GetNumberOfPoints()):
            vts.InsertCellPoint(i)

       
        # I do not think you really need to specify this unless
        # you are running anything significantly different.

        if self.geomType == 'sweep':
            if self.scanType == 'RHI' or self.scanType == 'VAD':
                self.scan.SetDimensions([self.header['Number of gates'], self.header['No. of rays in file'], 1])
            elif self.scanType == 'User1':
                self.scan.SetDimensions([self.header['Number of gates'], beamID, 1])
            else:
                self.scan.SetDimensions([self.header['Number of gates'], beamID, 1])


        if self.geomType == 'gates':
            self.scan.SetVerts(vts)
        elif self.geomType == 'rays':
            # when I do it this way, I get one cell of multiple lines
            # I'd rather have multiple cells, I think
            # which means... either inserting after
            self.scan.SetLines(vts)
    

    def writePolyData(self, nfile):
        if self.pitchAndRoll:
            filename = '{}.{}.{}'.format(self.scanType,self.geomType,nfile)
        else:
            filename = '{}.{}.no-pitch-and-roll.{}'.format(self.scanType,self.geomType,nfile)


        if self.geomType == 'gates' or self.geomType == 'rays':
            writer = vtk.vtkXMLPolyDataWriter()
            filename += '.vtp'
        elif self.geomType == 'sweep':
            writer = vtk.vtkXMLStructuredGridWriter()
            filename += '.vts'
        writer.SetFileName(filename)
        writer.SetInputData(self.scan)
        writer.Write()
   
if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Options for hpl2vtk', 
            formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument('scanDirectory', help='Directory containing scans of a particular type.')
    argparser.add_argument('scanType', help='LiDAR scan type, one of {RHI|VAD|Stare|User}')
    argparser.add_argument('outputGeometry', help='Output geometry type, one of{gates|rays|sweeps}\n'
            '"gates" are VTK polydata vertex cells\n'
            '"rays" are VTK polydata poly line cells\n'
            '"sweeps" are VTK structured grids')

    argparser.add_argument('--pitch-and-roll', dest='pitchAndRoll',
            action='store_true',
            help='apply pitch and roll of lidar device to output geometry.')
    argparser.add_argument('--no-pitch-and-roll', dest='pitchAndRoll',
            action='store_false',
            help='ignore pitch and roll of the lidar device')

    argparser.set_defaults(pitchAndRoll=True)

    if len(sys.argv) == 1:
        argparser.print_help()
        sys.exit(1)

    args = argparser.parse_args()

    hplfilenames = sorted(glob.glob(args.scanDirectory + '/' + args.scanType + '*.hpl'))

    nfile = 0
    for f in hplfilenames:
        hpl = HPL(args.scanType, args.outputGeometry, args.pitchAndRoll)
        hpl.read_hpl_file(f)
        # writing here is as if each file is an instaneous time step
        # which is possibly okay for RHI and VAD but definitely not
        # for Stare and who knows for User.
        
        # Still being stored under the folder where the thing is stored at
        # Well, to be more specific, the project folder.

        # Parallel processing version should be uploaded soon.
        hpl.writePolyData(nfile)
        nfile += 1
