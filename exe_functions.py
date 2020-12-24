import os
import sys
from os import path

def build_path(folder, fname):
#basedir = getattr(sys.executable, path.abspath(path.dirname(__file__)))
	basedir = sys.executable
	#print("basedir: ", basedir)
	#print("sys.executable: ", sys.executable)
	bundle_dir = path.dirname(basedir)
	# Original
	return path.abspath(path.join(bundle_dir, folder, fname))
   