import os
import glob
from importlib import reload

from atmospheric_lidar import raymetrics
reload(raymetrics)

from matplotlib import pyplot as plt


# dirs = glob.glob('/media/sf_Work/Work/Data/Raymetrics/Noa Lidar Data/06.Lidar_Data/Scanning_Measurements/*')
# output_dir = '/home/ioannis//Work/Work/Data/Raymetrics/Noa Lidar Data/scan_plots/'

dirs = glob.glob('/media/sf_Work/Work/Data/Raymetrics/Safetrans/NOA/Scanning_Measurements/*')
output_dir = '/home/ioannis//Work/Work/Data/Raymetrics/Safetrans/NOA/scan_plots/'


print("%s dirs found." % len(dirs))

for dir in dirs:
    scan_dirs = [d for d in glob.glob('{0}/*'.format(dir)) if ('AS' in d)]

    for scan_path in scan_dirs:
        files = glob.glob('{0}/RM*'.format(scan_path, ))

        scan_dir = os.path.basename(scan_path)

        if files:
            m = raymetrics.ScanningLidarMeasurement(files, use_id_as_name=True)
            print(files[0])
            print(m.channels.keys())

            # c = m.channels['BC0']
            # c.calculate_rc(first_signal_bin=0)
            # c.plot_scan(z_max=5500, vmin=0, vmax=3e9, box=True, show_plot=False)
            # plt.savefig(os.path.join(output_dir, 'photon', scan_dir + '_ph.png'), dpi=200)
            # plt.close()

            c = m.channels['BT0']
            c.calculate_rc(first_signal_bin=9)
            # c.plot_scan(z_max=5500, vmin=0, vmax=3e6, box=True, show_plot=False, ax1_span=1, ax2_position=(0, 1), ax2_span=3)  # RHI
            c.plot_scan(z_max=10000, vmin=0, vmax=3e6, box=True, show_plot=False, ax1_span=2, ax2_position=(0, 2), ax2_span=2)  # PPI

            plt.savefig(os.path.join(output_dir, 'analog/', scan_dir + '_an.png'), dpi=200)
            plt.close()

        else:
            print("No files found in {0}.".format(scan_path))
