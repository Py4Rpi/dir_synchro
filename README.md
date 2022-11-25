# DIR SYNCHRO

Test task program


## Description

Hello!

This is my test task from employer. It is a simple Python program that synchronizes two folders periodically.
The algorithm uses hash of files and folders to compare them between the source and destination directories.

 
## Getting Started

### Dependencies

I used Python 3.8. in this project.

There is only one external librariy to be used - dirhash. Others are native python modules.

### Installing

To install the programm you can just download it as a ZIP file or use "gh repo clone Py4Rpi/dir_synchro" command. 
Then just copy the main.py file to convenient folder. Ensure that Python 3.8 is installed on your Windows.
Then install dirhash library with "pip install dirhash" command in your cmd.

### Executing program

* When dependencies and installing steps are completed you can just open terminal, go to dir with main.py and run it 
with appropreate arguments. It takes four arguments: path to source directory, path where the replica directory will 
be created, path and name of log file (.log), interval between synchronizations in seconds:

```
python main.py C:\Input\sync D:\Output C:\Output\sync_log_file.log 3

```

If all goes well then program will start synchronization process of source and replica folder with mentioned interval.
Keep in mind that program won't run if entered path is not valid.

It will keep track of all operations in the mentioned log file so it can be analized afterwards.

To stop the program execution just press CTRL+C in the terminal window with running program. 

So far its tested only under Windows 10 operating system but it should run fine on Linux systems too.

This code still can be improved by many ways. New versions will be uploaded later.

## Help

If any troubles you can use Issue Tracker to notify me.

