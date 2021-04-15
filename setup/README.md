# How to setup a Maya Python environment

## Introduction
This guide will walk you through setting up a PyCharm environment that can interact with Autodesk Maya.
You will be able to run code in Maya from PyCharm, debug code running in Maya, and execute tests in Maya.
PyCharm will be set up with auto-completion for the Maya Python APIs.

## Assumptions & Definitions
It is assumed that Autodesk Maya already is installed.
We denote its version as `<MAYA_VERSION>` and its installation path as `<MAYA_INSTALL_PATH>`.
Under Windows this will typically be `C:/Program Files/Autodesk/Maya2020` for the 2020 version of Maya.
Maya has a scripts folder for Python code that can be imported and used in the Maya script editor without further ado.
We denote the path to this scripts folder as `<MAYA_SCRIPTS_PATH>`. Under Windows `<MAYA_SCRIPTS_PATH>` will typically be `C:/Users/<USERNAME>/Documents/maya/<MAYA_VERSION>/scripts` where `<USERNAME>` is the Windows username.

## Setup

1) Download and install [PyCharm](https://www.jetbrains.com/pycharm/download/). The free Community edition suffices.
   - Consider to tick the `Create Associations` box associating `.py` files with PyCharm.
2) Open PyCharm.
3) **Create a `New Project`.**
    - Select a sufficent location for the project. We denote the project path as `<PROJECT_PATH>`.
    - Expand the `Python Interpreter: ...` field group, if not expanded.
    - Select `Previously configured interpreter` and click the `[...]` button.
        - In the window that pops up go to `System Interpreter` and click the `[...]` button.
        - Select `<MAYA_INSTALL_PATH>/bin/mayapy.exe` as the interpreter.
        - Click `OK`.
    - Untick the `Create a main.py welcome script` option.
    - Click `Create`.
    - In the newly created project, select the directory with the name you gave the project. Right-click and select `New` > `Directory` to create a directory called `scripts`. This directory will contain your Python scripts for use in Maya.
    - Right-click the newly created `scripts` directory and select `Mark Directory As` > `Sources Root`.
    - Select the project directory. Right-click and select `New` > `Python Package` to create a directory called `test`. Note that the directory is created with a `__init__.py` file. The intend of the `test` directory is to host automatic tests for your code in `<PROJECT_PATH>/scripts`.
4) **Install the MayaCharm plugin to use PyCharm as an upgrade to Maya's script editor.** This will allow execution of Python code in Maya from PyCharm and getting Maya log output sent to PyCharm.
    - In the menu of your open project go to `File` > `Settings` > `Plugins`.
    - In the plugins search field write `MayaCharm`. A single result should appear.
    - Click `Install` and `Accept` any third-party plugins privacy note that may pop up.
    - Click `Apply` in the lower-right corner once the plugin has been installed.
      The settings window should update and `MayaCharm` should appear in the submenu to the left.
    - Click on `MayaCharm` in the left submenu.
    - Verify that `<MAYA_INSTALL_PATH>/bin/mayapy.exe` is listed as the `Active Maya Sdk` and that the port number `4434` appears in the list below.
    - Click `OK` to close the settings window.
    - Copy `userSetup.py`, provided with this guide, to the destination: `<MAYA_SCRIPTS_PATH>/userSetup.py`. The `userSetup.py` script will make Maya open a command port on port `4434` upon startup, allowing PyCharm to execute code in Maya via the MayaCharm plugin. If the destination file already exists, copy the contents of `userSetup.py` to the end of the destination file.
    - Restart Maya if currently running.
    - Restart PyCharm. Your project should reopen.
    - Verify that MayaCharm can connect to Maya by activating `Run` > `Connect to Maya's Log`  in the PyCharm menu. No error notification should pop up. If you ever have PyCharm issues with receiving output from a script run in Maya, activate this menu item again. _You need to do it every time Maya (re)starts._
5) **Setup PyCharm code completion of Maya Python APIs:**
    - You will need the Maya development kit for this. If you already have downloaded it, the following directory should exist: `<MAYA_INSTALL_PATH>/devkit/other/pymel/extras/completion/pyi`. Otherwise download and install it:
        1) Go to the [Maya Development Center](https://www.autodesk.com/developer-network/platform-technologies/maya) (login required).
        2) Scroll down until "Maya `<MAYA_VERSION>` devkit Downloads" and download the latest update of the devkit for your operating system.
        3) Unzip the downloaded zip archive to `<UNZIPPED>` (your choice) and copy the contents of `<UNZIPPED>/devkitBase/devkit` to `<MAYA_INSTALL_PATH>/devkit`.
        4) The parts of the development kit we are interested in have now been installed.
    - Inside your PyCharm project, in the menu go to `File` > `Settings` > `Project: <NAME>` > `Project Structure`.
    - Click `Add Content Root` to the right and navigate to `<MAYA_INSTALL_PATH>/devkit/other/pymel/extras/completion/pyi`. Click `OK` to add the `pyi` directory.
    - The `pyi` directory is now selected as content root. Click `Excluded`.
    - Click `OK` to apply and close the settings window.
6) **Setup easy lookup of `maya.cmds` documentation in PyCharm.**
    - Inside your PyCharm project, in the menu go to `File` > `Settings` > `Tools` > `External Documentation`.
    - Click the `+` to add new external documentation. Fill out:
      *Module Name*: `maya.cmds` 
      *URL/Path Pattern*: `https://help.autodesk.com/cloudhelp/<MAYA_VERSION>/ENU/Maya-Tech-Docs/CommandsPython/{element.name}.html`. (remember to replace `<MAYA_VERSION>`)
    - Click `OK`.
    - Click `OK` to apply and close the settings window.
    - You can now quickly browse documentation for a `maya.cmds` function by setting the cursor within the function name (e.g. `ls` in `cmds.ls()`) and pressing `shift` + `F1`.
7) **Make your awesome Python code available in Maya.**
   We want the Maya script editor to have access to the scripts located in `<PROJECT_PATH>/scripts`, either when code is executed directly in Maya or via MayaCharm. You could place your project in the script folder (`<MAYA_SCRIPTS_PATH>`) to make it available, but then you would have to access a module `X` as `import YourAwesomeProject.scripts.X` rather than just `import X`.
   Here are two ways to resolve the problem:
    1) Add the following snippet to `<MAYA_SCRIPTS_PATH>/userSetup.py`
        
        ```
        import sys
        sys.path.append("<PROJECT_PATH>/scripts")  # or whatever folder that contains the Python code
        ```
        and then restart Maya.
    2) Or: Add `<PROJECT_PATH>/scripts` to the `PYTHONPATH` environment variable and restart Maya. You can use this technique to install any Python library for use in or outside Maya. To install `<PROJECT_PATH>/scripts` on Windows:
        - Go to `My Computer` > `Properties` > `Advanced System Settings` > `Environment Variables`.
        - If `PYTHONPATH` isn't listed as variable in the top half of the dialog, then click the top `New...` button, fill out
        *Variable name*: `PYTHONPATH`
        *Variable value*: `<PROJECT_PATH>/scripts`
        and click `OK`.
        - Otherwise select the listed `PYTHONPATH` variable and click `Edit...`. Append `;<PROJECT_PATH>/scripts` (note the semicolon) to the variable value and click `OK`.
8) **Execute and debug code in Maya.**
    With all prior setup steps done we can now test remote code execution and debugging in Maya.
    - Create a file called `testing.py` in `<PROJECT_PATH>/scripts` with the following contents:
      ```
      def hello(name):
          print "Hello", name
      ```
    - Create a file called `test.py` _outside_ the `/scripts` directory, with the following contents:
      ```
      import testing
      testing.hello("world")
      ```
    - Make sure PyCharm is receives output from Maya; in the menu do `Run` > `Connect to Maya's Log`.
    - Open the `MayaLog` console window at the bottom of PyCharm.
    - Inside `test.py` press `alt` + `A` or in the menu go to `Run` > `Execute document in Maya`.
      If all went well this should output `Hello world` in the MayaLog console window.
    - Next set break points at the lines saying `testing.hello("world")` in `test.py` and `print "Hello", name` in `testing.py` (click the empty area to the right of the line number).
    - In the menu go to `Run` > `Attach to Process...` and select the Maya option from the list that appears.
      A debug window saying `Successfully attached to Maya` should appear.
    - Go to `test.py` and print press `alt` + `A`. `test.py` should begin to execute in Maya and pause at the break point.
    - Click the green arrow in the debug window to resume execution. Execution should pause at the break point in `testing.py`.
    - Resume execution again. `Hello world` should be writen to both the debug console and the MayaLog console, and the execution should finish.
    - Congratulations, you can now develop and test Maya code in PyCharm without going to Maya.
9) **Implement and run automatic tests.**
    This assumes that the `pyphil` library has been installed and is available to the project.
   - In `<PROJECT_PATH>/test` add a new file called `test_demo.py` with contents:
        ```
        from pyphil.test import TestCase
        import maya.cmds as cmds
        
        class DemoTests(TestCase):
            def test_create_sphere(self):
                sphere = cmds.polySphere(name="mySphere")[0]
                self.assertEqual("mySphere", sphere)
                
            def test_create_sphere2(self):
                sphere = cmds.polySphere(name="mySphere")[0]
                self.assertEqual("mySphere", sphere)
        
        ```
   - Right-click the file and choose `Run 'Unittests in test_demo.py'`.
     The two example test cases will run isolated from each other and should both succeed.
     The `DemoTest` class extends the `pyphil.test.TestCase` which sets up a fresh Maya scene for each test case that runs.
     Maya is run in the background, independent from any Maya instance that already may (or may not) be running.
   