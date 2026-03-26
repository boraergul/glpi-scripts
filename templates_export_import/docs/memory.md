# Memory - Template Export/Import

## Known Issues
- `sys.exit(1)` in `Gui_templates_export_v2.py` causes the GUI to close abruptly without showing errors to the user.
- Path handling for `servers.json` needs to be robust across different drive letters (G: vs D:).

## Quirks
- Tkinter mainloop can hang if long-running processes are not handled in separate threads or with `after()`.
