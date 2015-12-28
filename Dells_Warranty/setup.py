from distutils.core import setup
import py2exe

#Notice:
#you should modify the dlls path depends on your own enviroment on which pyqt4 and qt5 installed.
#the Qt5 essential libEGL.dll must be copied to current directory which py2exe don't do that
#the qwindows.dll must be copied to './platforms' otherwise the program couldn't find it
data_files = [('', ['dells.txt','Readme.txt']),
              ('', [r'C:\Qt\Qt5.1.0\5.1.0\msvc2010\bin\libEGL.dll']),
			  ('platforms', [r'C:\Qt\Qt5.1.0\5.1.0\msvc2010\plugins\platforms\qwindows.dll'])]

setup(name="Dell_Warranty_Tool",
      version="1.0",
      author="wen.zhang",
      author_email="wen.zhang@wedoapp.com",
      windows=[{"script":"execute.py","company_name":"wedoapp.com"}],
      options={"py2exe": {"skip_archive": False, "includes": ["sip"]}},
      zipfile = "lib/library.zip",
	  data_files = data_files
	  )
