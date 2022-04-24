Install the version of python that you prefer (>=3.6) from here: https://www.python.org/.

Install the IDE that you prefer. For Python, I recommend PyCharm or VisualStudio Code.

Create a new folder called "GTec Hackaton 2022" (or whatever you prefer)

Go into that folder and open a new terminal, verify that Python is installed by launching 

`python --version`

Now lunch the following command to create a new virtual environment

`python -m venv hackaton` 

you can also specify a path if you wanna create in subfolders, for example

`python -m venv myenv/hackaton`

Then activate the virtual environment use the following command on Windows

`.\hackaton\Scripts\activate.bat`

or on Mac / Linux

`source hackaton/bin/activate`

Now your environment should be ready, let's check everything is ok by launching

`python --version`

Alright, now we are ready to install some libraries. First we want MNE for signal processing. It will take some
time, but you will have all the main libraries for handling and visualizing data, like NumPy, SciPy and Matplotlib.

`pip install mne[hdf5]`

Then we will install Brainflow to manage IO devices

`python -m pip install brainflow`

Finally, we are ready to open PyCharm and create a new project (or import this one if you pulled it from GitHub).
At this point remember to select the environment we just created by using the dropdown menu and selecting the 
environment reference  `hackaton\Scripts\python.exe` or `hackaton/bin/python` on Mac/Linux.