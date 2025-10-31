# Climate Vulnerability Index (CVI) Analysis

This directory contains the complete Climate Vulnerability Index calculations for Delhi NCR districts based on the operational CVI formulas.

## 📁 Directory Structure

```
CVI_Analysis/
├── calculate_cvi.py              # Main calculation script
├── CVI_REPORT.md                 # Detailed analysis report
├── cvi_results/
│   └── cvi_results.json          # Numerical results in JSON format
└── cvi_visualizations/
    ├── cvi_components_comparison.png
    ├── cvi_radar_Central_Delhi.png
    ├── cvi_radar_Alwar.png
    └── cvi_summary_table.png
```

## 🎯 Quick Start

### Run CVI Analysis
```bash
cd /home/devkanani/VSCODE/EVST/EVST_Project/CVI_Analysis
python3 calculate_cvi.py
```

## 📊 Results Summary

### Central Delhi
- **CVI Score**: 0.3889
- **Vulnerability Level**: MODERATE
- **Key Issue**: Very high population density (27,730/km²)
- **Strength**: High adaptive capacity (100% urbanization)

### Alwar
- **CVI Score**: 0.3673
- **Vulnerability Level**: MODERATE
- **Key Issue**: Low adaptive capacity (low urbanization)
- **Strength**: Low population density (438/km²)

## 🔬 Methodology

The analysis follows the CVI operational formulas:

1. **Potential Impact (PI)** = α×E + β×S
2. **OUV Vulnerability** = PI × (1 - AC)
3. **ESC Impact** = δ × OUV + (1 - δ) × ESC_Dependency
4. **Community Vulnerability (CV)** = ESC × (1 - ESC_AC)

### Components Calculated:
- **Exposure (E)**: Temperature extremes, rainfall variability
- **Sensitivity (S)**: Population density, water stress
- **Adaptive Capacity (AC)**: Income, urbanization

## 📈 Data Sources

| Component | Data Source | Coverage |
|-----------|-------------|----------|
| Temperature | IMD/NASA | 2013-2024 |
| Rainfall | IMD | 2013-2024 |
| Population | Census 2011 | District-level |
| Income | District Reports | Various years |
| Groundwater | CGWB | 2013-2021 |

## 📄 Reports

See `CVI_REPORT.md` for detailed analysis, methodology, findings, and recommendations.

## 🔧 Dependencies

```python
pandas
numpy
matplotlib
seaborn
scipy
```

## 🎨 Visualizations

All visualizations are automatically generated and saved in `cvi_visualizations/`:
- Component comparison charts
- Radar charts for vulnerability profiles
- Summary tables with color-coded vulnerability levels

## 📝 Notes

- Both districts show MODERATE vulnerability but with different underlying factors
- Central Delhi: High sensitivity, high adaptive capacity
- Alwar: High exposure, low sensitivity, low adaptive capacity

## 🔮 Future Enhancements

- [ ] Add AQI data integration
- [ ] Include all Delhi NCR districts
- [ ] Time-series CVI analysis (2013-2024)
- [ ] Interactive dashboard
- [ ] Scenario analysis for climate projections

---

**Last Updated**: October 14, 2025
