from distutils.core import setup
import py2exe
#TODO:We need to mkdir 'show_run_results' in the .exe directory and copy all the lxml module files into the library.zip/lxml manually when
#'python setup.py py2exe' has been executed in windows command.
data_files = [('', ['switches_mgr.xlsx','check_report_template.docx','switches_commands.json'])]

setup(name="Swithes_Telnet_Tool",
      version="1.0",
      author="wen.zhang",
      author_email="wen.zhang@wedoapp.com",
      console=[{"script":"generate_report.py"},{"script":"generate_commands_results.py"}],
      options={"py2exe": {"skip_archive": False}},
      zipfile = "lib/library.zip",
	  data_files = data_files
	  )
