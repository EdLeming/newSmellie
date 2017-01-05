from setuptools import setup
from glob import glob

setup(name = "smellie",
      version = "1.0.2",
      description = "SNODROP smellie h/w control server",
      author= "Luca Cavalli, Jack Dunger, Chris Jones, Jeff Lidgard and Krishanu Majumdar",
      maintainer = "Jack Dunger, Jeff Lidgard",
      author_email = "jack.dunger@physics.ox.ac.uk",
      packages = ["smellie", "sepia", "server", "daqmx"],
      py_modules = ["smellie_config"],
      install_requires = ["pyserial==2.7", "hiredis", "LabJackPython", "numpy"], 
      scripts=glob("bin/*")
      )
