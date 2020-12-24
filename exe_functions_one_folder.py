from os import path
import sys

def build_path(folder, fname):
	bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
	return path.abspath(path.join(bundle_dir, folder, fname))