#==========================FOR WINDOWS==========================
# from cx_Freeze import setup, Executable
# import os.path
# PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
# os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
# os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')
#
# options = {
#     'build_exe': {
#         'include_files':["autorun.inf",os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
#                          os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),os.path.join(PYTHON_INSTALL_DIR,'lib','site-packages','numpy')],},
# }
#
# setup(name = "DATASOFT CONTAINER NUMBER READER" ,
#       version = "0.1" ,
#       description = "This system can read container number from container body using camara" ,
#       author="Asif",
#       author_email="softengr.asif@gmail.com",
#       options=options,
#       executables = [Executable("Main.py","Console")])







#==========================FOR UBUNTU==========================
from cx_Freeze import setup, Executable

options = {
    'build_exe': {
        'packages': ['numpy', 'imutils'],  # add packages your app depends on
        'includes': ['http', 'http.client', 'urllib.request'],  # explicitly include these stdlib modules
        'excludes': ['tkinter', 'unittest', 'email', 'html'],  # optional exclusions
        'include_files': []
    },
}

setup(
    name="DATASOFT CONTAINER NUMBER READER",
    version="0.1",
    description="This system can read container number from container body using camera",
    author="Asif",
    author_email="softengr.asif@gmail.com",
    options=options,
    executables=[Executable("Main.py")]  # or your actual script name
)
