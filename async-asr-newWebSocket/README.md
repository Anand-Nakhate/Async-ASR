# Async GUI for ASR

## Part 1 - Setting up VM/OS environment

### Setup Virtual Machine
1. Download Oracle VM VirtualBox at https://www.virtualbox.org/
2. Download the Operating system image file you wish to install
    - Windows Image/ISO can be download at <a href="https://developer.microsoft.com/en-us/microsoft-edge/tools/vms/">Microsoft website</a>
    - Ubuntu 16.04 Linux VM <a href="https://releases.ubuntu.com/16.04/">Images/ISO file</a>
3. Creating a New Virtual Machine in VirtualBox
    1. Run VirtualBox
    2. Select `New`
    3. Provide the information of the OS you will be installing. 
      ```bash
        Name: Ubunto 20.04
        Type: Linux
        Version: Ubuntu (64-bit)
        Allocated Ram: 2gb *you can assign more when necessary
        Hard disk types : VDI
        Dynamically allocate hard disk
        Hard disk space : 20gb *you can assign more when necessary
      ```
4. Settings to complete process
    1. Select Settings > storage
    2. Under storage devices select Controller: IDE
    3. Select adds optical drive button ![image](https://user-images.githubusercontent.com/42940055/110685908-bd7fe180-8219-11eb-835f-8fe1b3610383.png)
    4. Choose the ISO file which you downloaded previously at step 2   
    5. (<b>Optional step</b>) Select Settings > General > Advanced   
This will allow transfering of files and codes through the host and guest os using Shared Clipboard and Drag'n'Drop
    ```
    Set Shared Clipboard : Host to Guest
    Set Drag'n'Drop : Host to Guest
    ```
5. Select Start and boot up the virtual machine. Follow the guided wizard to install the respectively OS

6. If you created an `unbuntu VM` and set both "Set Shared Clipboard : Host to Guest" and "Set Drag'n'Drop : Host to Guest" option. You will need to install VirtualBox Guest Additions as drag'n'drop support feature requires the installation of Guest Additions package to work properly.
    1.  Install the Guest Additions from the VirtualBox menu (Devices > Install Guest Additions)
    2.  Restart the VM



### Installing Python 3.8.5 on Ubuntu 20.04
1. Prerequisite

As you are going to install Python 3.8 from the source. You need to install some development libraries to compile Python source code. Use the following command to install prerequisites for Python:
```
sudo apt-get install build-essential checkinstall
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev tar wget vim
```
2. Download Python 3.8.5

Download Python source code using the following command from python official site. You can also download the latest version in place of specified below.
```
cd /opt
sudo wget https://www.python.org/ftp/python/3.8.5/Python-3.8.5.tgz
```
Then extract the downloaded source archive file
```sudo tar xzf Python-3.8.5.tgz```

3. Compile Python Source
Use the below set of commands to compile Python source code on your system using the altinstall command.
```
cd Python-3.8.5
sudo ./configure --enable-optimizations
sudo make -j 4
sudo make altinstall
```
4. Check Python Version
Check the installed version of python using the following command. As you have not overwritten the default Python version on the system, So you have to use Python 3.8 as follows:
```
python3.8 -V
```
After successful installation remove the downloaded archive to save disk space
```
cd /opt
sudo rm -f Python-3.8.5.tgz
```

## Part 2  - Setting up the project

### Installation Instructions 
### Linux/Ubuntu
1. Clone the project using `git clone https://github.com/kzintun/async-asr.git` *NEED CHANGE
2. Change current directory to project using `cd async-asr`
3. Install virtual environment tool virtualenv using `python3.8 -m pip install virtualenv`
4. Create a python 3 virtual environment using `virtualenv -p python3.8 venv`
5. Activate the virtual environment using `source venv/bin/activate`
6. Install the requirements using `pip install -r requirements.txt`
* Install portaudio if pyaudio installation failed using `sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0`
7. This project uses python-vlc library which is ctypes-based bindings (see http://wiki.videolan.org/PythonBinding) for the native libvlc API (see http://wiki.videolan.org/LibVLC) of the VLC video player. Install vlc using `sudo apt install vlc`
8. This project uses Spacy's displayCy for Named Entity Recognition. Download the model using `python -m spacy download en_core_web_sm`
9. This project uses sox for audio splitting. Install the same using `sudo apt install sox`
10. Run the application using `python qtmainwindow.py`

### Window
1. Clone the project using `git clone https://github.com/kzintun/async-asr.git` *NEED CHANGE
2. Change current directory to project using `cd async-asr`
3. Install virtual environment tool virtualenv using `python3.8 -m pip install virtualenv`
4. Create a python 3 virtual environment using `virtualenv -p python3.8 venv`
5. Activate the virtual environment using `venv\Scripts\activate`
6. Install the requirements using `pip install -r requirements.txt`
* Install portaudio if pyaudio installation failed, find the appropriate .whl file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio), for example `PyAudio‑0.2.11‑cp38‑cp38m‑win_amd64.whl`, and download it.
* go to the folder where it is downloaded for example `cd C:\Users\foobar\Downloads`
* `pip install PyAudio-0.2.11-cp37-cp37m-win_amd64.whl`
7. This project uses python-vlc library which is ctypes-based bindings (see http://wiki.videolan.org/PythonBinding) for the native libvlc API (see http://wiki.videolan.org/LibVLC) of the VLC video player. Install vlc at their [offical website](https://www.videolan.org/vlc/download-windows.html)
8. Run the application using `python qtmainwindow.py`


### Configuration file
There are 3 configuration file used in this project namely `services.ini`, `colorcode.ini` and `hotkey.ini`
* Services.ini - This configuration will 3 section namely `[ASR]`, `[SUD]` and `[API]`
    1. 

## Part 3 - Software Packaging and Distribution
In this section, it will explain how to compile the PyQt application into stand-alone executables and package the executables into an installer for distribution.

### Creating an executables for the PyQt application
### Linux/Ubuntu
1. Install PyInstaller from PyPI using `pip install pyinstaller`
2. Change current directory to project using `cd async-asr`
3. Activate the virtual environment using `source venv/bin/activate`
4. Create the executable using `pyinstaller asr_linux.spec`
This will generate the bundle in a subdirectory called `dist`
5. Run the executable `dist/asr/asr`

### Window
1. Install PyInstaller from PyPI using `pip install pyinstaller`
2. Change current directory to project using `cd async-asr`
3. Activate the virtual environment using `venv\Scripts\activate` 
4. Create the executable using `pyinstaller asr.spec`
This will generate the bundle in a subdirectory called `dist`
5. Run the executable `dist/asr/asr.exe`

### Package the executables into an installer for distribution
### Linux/Ubuntu - building a Debian package
1. Folder structure
```
Asr/
├──DEBIAN/
|  └──control
├──usr/
|  └──share/
|     └──application/
|        └──asr.desktop
├──opt/
|  └──asr/
|     └──(dist files)
```
<b>Control file</b> - This file in `Asr/DEBIAN/` contains various values which dpkg, dselect, apt-get, apt-cache, aptitude, and other package management tools will use to manage the package. It is defined by the [Debian Policy Manual, 5 "Control files and their fields"](https://www.debian.org/doc/debian-policy/ch-controlfields.html). 

Inside control file:
```
Package: asr
Version: 1.0
Architecture: amd64
Maintainer: Desmond
Description: asr gui
```
<b>asr.desktop</b> - The .desktop files, are generally a combination of meta information resources and a shortcut of an application. These files usually reside in /usr/share/applications/ or /usr/local/share/applications/ for applications installed system-wide, or ~/.local/share/applications/ for user-specific applications. User entries take precedence over system entries. [More information](https://wiki.archlinux.org/index.php/desktop_entries)
Inside asr.desktop file:
```
[Desktop Entry]
Name=Asr
Exec=/opt/asr/asr
Icon=/opt/asr/icons/ASR.png
Type=Application
```
Lastly, Asr/opt/asr/ will contain the `dist` bundle created previously using pyinstaller. Copy manually from `async-asr/dist/asr/` or run `cp -a dist/asr/. packaging/ubuntu/Asr/opt/asr/`

2. Package as Debian installer
Run the following command to make your Debian installer
```
dpkg-deb --build packaging/ubuntu/Asr
```
The Debian installer will be created in the same directory as your project folder.

Now you can install it by:
```sudo dpkg -i <package>```
And uninstall it by:
```sudo dpkg -r <package>```
If all went well, you can run it from Dash.

### Window
1. Download [inno setup compiler](https://jrsoftware.org/isdl.php#stable)
2. Install and run inno setup compiler
3. Go to `file>open` choose `installerscript.iss` located at `async-asr\packaging\win\`
4. Select `run` or `F9`
5. An installer file named `mysetup.exe` will be created at the `async-asr\packaging\win\Output\`
6. run `mysetup.exe` to install

## Useful Links
- [YouTube](https://www.youtube.com/watch?v=sB_5fqiysi4) - How to Use VirtualBox (Beginners Guide)
- [tecadmin](https://tecadmin.net/install-python-3-8-ubuntu/) - How to Install Python 3.8 on Ubuntu, Debian and LinuxMint
- [Pyinstaller spec file](https://pyinstaller.readthedocs.io/en/stable/spec-files.html) - Using Spec Files
- Inno-Setup (https://documentation.help/Inno-Setup/documentation.pdf) - What is Inno Setup?









