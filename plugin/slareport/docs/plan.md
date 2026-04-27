# Plan: SLA Translation & Deployment Optimization

## Goal
Fix persistent translation issues, enhance PDF report aesthetics, and establish a reliable production deployment workflow.

## Steps (Completed)
- [x] **Custom Translation Engine**: Implement `PluginSlareportReport::trans()` to bypass GLPI cache issues.
- [x] **Locale Conversion**: Migrate `.mo/.po` files to direct PHP return arrays for TR/EN.
- [x] **UI Integration**: Update `index.php`, `report.class.php`, and `export_pdf.php` to use the new engine.
- [x] **Premium PDF Restoration**: Re-implement cover page, charts, and executive summary with multi-language support.
- [x] **PROD Deployment**: Create `deploy_prod.sh` targeting `10.42.2.149` with correct paths and users.
- [x] **Bug Fixes**: 
    - Resolved 500 error in `setup.php`.
    - Fixed TCPDF inclusion for GLPI 10/11.
    - Fixed CSV output buffering issues.

## Verification
- [x] Dashboard fully translated in itsm-dev.
- [x] PDF export generated with cover page and Turkish characters.
- [x] CSV export working without errors.
- [x] deploy_prod.sh tested and verified.

## Next Steps (Future)
- Monitor memory usage for extremely large PDF exports.
- Implement background processing for very large date ranges.
