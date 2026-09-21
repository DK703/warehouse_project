import os
from glob import glob


package_name = 'cartographer_slam'


(os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
(os.path.join('share', package_name, 'config'), glob('config/*'))
