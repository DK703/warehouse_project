import os
from glob import glob

package_name = 'map_server'

(os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
(os.path.join('share', package_name, 'config'), glob('config/*'))
