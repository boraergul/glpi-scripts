# Plan - Fix Gui_templates_export_v2.py Crashes

## Goal
Prevent `Gui_templates_export_v2.py` from closing abruptly when an error occurs in the underlying `export_templates.py` or `import_templates.py` modules.

## User Review Required
> [!IMPORTANT]
> The changes involve modifying `export_templates.py` and `import_templates.py` to raise exceptions instead of calling `sys.exit(1)`. This will change the behavior of these scripts if run as standalone CLI tools (they will show a traceback instead of a silent exit code 1), but it is necessary for GUI stability.

## Proposed Changes

### [Template Export/Import Modules]

#### [MODIFY] [export_templates.py](file:///g:/Drive%27%C4%B1m/Projeler/Script/templates_export_import/export_templates.py)
- Replace `sys.exit(1)` in `load_config()` and `init_session()` with `raise RuntimeError(...)`.

#### [MODIFY] [import_templates.py](file:///g:/Drive%27%C4%B1m/Projeler/Script/templates_export_import/import_templates.py)
- Replace `sys.exit(1)` in `init_session()` and credential prompts with `raise RuntimeError(...)`.
- *Note*: Credentials prompts are mostly used in CLI mode, but `init_session` is used by both.

### [GUI Application]

#### [MODIFY] [Gui_templates_export_v2.py](file:///g:/Drive%27%C4%B1m/Projeler/Script/templates_export_import/Gui_templates_export_v2.py)
- Ensure all calls to `exp.init_session` and `imp.init_session` are wrapped in try-except blocks that log the error to the GUI log panel and show a `messagebox`.

## Verification Plan

### Automated Tests
- None currently exist. I will verify by running the GUI.

### Manual Verification
1.  **Connection Failure Test**:
    - Open `Gui_templates_export_v2.py`.
    - Select a profile with an invalid URL.
    - Click "Export Kaynak".
    - **Expected**: An error message should appear in the log and a popup, but the GUI window should remain open.
2.  **CLI Regression Test**:
    - Run `python export_templates.py` with an invalid config.
    - **Expected**: It should fail with an error message (traceback or printed error) and non-zero exit code.
