# Desktop-Icon-Position-Saver-Restorer-Windows-

A small Python script that saves the positions of your desktop icons to a JSON file and restores them later. It uses ctypes to talk to the desktop's SysListView32 control inside explorer.exe: it reads each icon's name and coordinates via Win32 messages (LVM_GETITEMTEXTW, LVM_GETITEMPOSITION), and repositions them with LVM_SETITEMPOSITION. Icons are matched by display name, so deleted or new icons are handled gracefully.

Usage:
python icone.py s    # save current layout to icone.json
python icone.py r    # restore saved layout

Requirements: Windows, 64-bit Python, and "Auto arrange icons" turned off.
