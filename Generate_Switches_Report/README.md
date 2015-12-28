Gen_SwitchesReport
==================

A little tool used to generate the switches check report implemented by python.
The dependencies form third-party are docx and openyxl.The module docx used to modify the check_report_template.docx that is the checkreport template,and the module openyxl used to read the switches_mgr.xlsx which record the switches infomation.
Also it can save the whole result of command 'show run' as a .txt file for each switch individually.

You can use "python generate_report.py check_report_template.docx output_report.docx {threadsNum}" to generate the report,
and threadsNum is the number of the threads that you want to use,the suggestion value is lower than 15.

You can use "python generate_commands_results.py {ip list}" to generate the .txt files in the directory show_run_results,
and ip list is optional,you can give the values like 'xx.xx.xxx.xxx' or 'xx.xx.xxx.xxx xx.xx.xxx.xxx'.

Notice:
1.If the number of threads is a bit more, sometimes the telnet connection maybe timeout.
2.Also you can use 'python setup.py py2exe' to get the executable file in Windows.See more details in 'setup.py' please.
3.The log file is 'generate.log'.
