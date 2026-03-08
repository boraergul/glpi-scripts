# Plan: Fix PET Failure & Restore Environment

## Goal
Resolve the "Python Environment Tools (PET) failed" error and restore a functional virtual environment for the script project.

## Phases

### 1. Research (Completed)
- Identified root cause: `.venv` in parent directory is broken (points to non-existent `C:\Users\Super` paths).
- Verified system Python: 3.13.2 is available for current user `maniac`.
- Identified dependencies: `requests`, `urllib3`.

### 2. Implementation
- [ ] Delete broken `.venv` at `d:\Google Drive\Projeler\Script\.venv`.
- [ ] Create new `.venv` using `python -m venv`.
- [ ] Install dependencies (`requests`, `urllib3`).
- [ ] Create `templates_import/requirements.txt` for future use.

### 3. Verification
- [ ] Run `python --version` from new `.venv`.
- [ ] Verify PET error is gone in VS Code.

