# FXPUtil
A utility for working with VST preset files.

## Quick Overview
- View metadata about the VST preset files such as the plugin it was made for, the company, etc 
- Compare two preset files to see byte-level differences

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/AbsoluteSkid/FXPUtil.git
   ```

2. Install required dependencies:
   ```
   pip install requests
   ```

3. Run the application:
   ```
   python FXPUtil.py
   ```

## Usage

### GUI
#### Launch the application without any commands to use the GUI:
```
python FXPUtil.py
```
![A screenshot of the interface](https://github.com/user-attachments/assets/7469c5b6-f824-456d-9705-de3aa4c8e125)

### CLI
#### Get Preset Information
```
python FXPUtil.py info -f preset.fxp
```

#### Compare Two Presets
```
python FXPUtil.py compare -f1 prest1.fxp -f2 preset2.fxp -n 200
```
The `-n` parameter specifies how many bytes to compare (optional, default is 100)

## Use it in your own scripts
Use the functions:
```python
from FXPUtil import *

# Get information about a preset
plugin_name = GetName("preset.fxp")
company = GetCompany("preset.fxp")
code = GetCode("preset.fxp")

# Change a preset's plugin code
SetCode("preset.fxp", "abcd")

# Compare two presets' bytes
comparison = Compare("preset1.fxp", "preset2.fxp", 100)
```

Use the interface:
```python
from FXPUtil import GUI

GUI()
```

## Requirements
- `requests` library, install using `pip install requests`

## Why does it say unknown on a valid preset?

If you have a preset but its information is unknown, you can add it to your database using the GUI or the AddToDatabase() function. Then optionally create a new issue in GitHub and include the preset file so it can be updated.

## License

This project is available under the MIT License. See the LICENSE file for details.
