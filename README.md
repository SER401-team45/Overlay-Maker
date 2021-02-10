# Overlay-Maker

Python based GUI for creating polygonal regions for video overlay.
Saves overlay to JSON format.


Use:
- Image must be loaded before overlay construction.
- Existing overlay files can be loaded and edited.
- Regions with non-empty, unique names may be added to the overlay.
- The last point added to a region always connects to the first point.
- The last point of a region may be deleted
- Entire regions may be deleted
- Existing regions may be selected from the region list.
- Completed overlays may be saved to JSON files.

Hot-Key shortcuts are shown under the "Shortcuts" dropdown

A grid overlay under "Tools" may be displayed to assist alignment.


Running this script requires installation of Tkinter and PIL

pip install Tkinter
pip install PIL



# Model_Overlay

Model_Overlay.py requires libraries Numpy, cv2, and shapely.

	pip install Numpy
	pip install cv2
	pip install shapely

Note:
shapely installed for me, but failed at runtime. The following commands resolved my issue.

	conda config --add channels conda-forge
	conda install shapely