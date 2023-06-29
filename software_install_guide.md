### Setting up your Environment (Windows)
## Required software
1. Python Version >=3.7 <3.11
2. Git
3. Docker Desktop
4. An IDE
5. Airflow version 2.5.2

## Optional (but recommended) software
1. Windows Subsystem for Linux


## Installing WSL
*Note: This assumes you are using a Captech issued Windows Machine*
1. Install WSL from the Microsoft Store
2. Install a distrobution from the MS Store (Ubuntu recommended)
3. Open Powershell with administrator elevation
    i. On CT machines, open the start menu and search powershell \n
    ii. Right click, and select open file location \n
    iii. Right click on powershell.exe and select "More Options"
    iv. Select "Beyond Trust" and provide a reason (ex: Install WSL)
    v. You will now need to open a SECOND command prompt window using the following command to get "true" admin permissions
    `Start-Process cmd -Verb runAs`
    vi. With this new CMD window, run the following command
    `wsl --update --web-download`
3. Install terminal for windows
    i. Use the MS Store to download
4. Open terminal, and in the top bar, click the down arrow to open new window options, and select WSL
5. Once you can get into your WSL terminal, update Ubuntu
    i. `sudo apt-get update`

## Installing Git
1. Download and install git from this location
2. Open your termnial with WSL, and run `git --version` to confirm git is available

## Installing Docker Desktop
1. Download and install Docker Desktop
2. Open your terminal with WSL, and run `docker --version` to confirm docker is available

## Installing an IDE
1. Pick your favorite IDE and download and install it
2. This tutorial will assume you are using VSCode

## Installing Python and Setting up a Virtual Environment
*Note: These steps assume you are using a UNIX terminal (Mac, Linux, or WSL)*
1. Install a version of Python >=3.7 and <3.11 (recommend 3.10) from the Microsoft Store
2. Confirm python was installed and available to WSL
    i. `python3 --version`
3. Check if pip is installed by trying to install a normal pyhton package
    i. `pip3 install pandas`
    ii. If this failed, install pip
        `sudo apt install pyhton3-pip`
4. Create a virtual environment
    i. `pip3 install virtualenv`
    ii. python3 -m virtualenv airflow-sandbox
5. Activate your Venv
    i. `source airflow-sandbox/bin/activate`
    ii. Your terminal should now display (airlfow-sandbox) next to the directory

## Installing Airflow
1. Open terminal with WSL
2. Activate the virtual environment from above (only if not already activated)
3. Pip install the recommended version of apache-airflow
`pip3 install apache-airflow==2.5.2`