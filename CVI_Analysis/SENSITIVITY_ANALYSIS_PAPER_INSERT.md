## Sensitivity Analysis Results (Weight Perturbation ±10-20%)

### Purpose
To test whether district vulnerability outcomes were driven by arbitrary parameter choices, we performed a structured sensitivity analysis by perturbing key weights in the Sensitivity (S), Adaptive Capacity (AC), and Potential Impact (PI) formulations.

### Scenarios Tested
The baseline and five alternative scenarios are listed in the CSV table:
- [sensitivity_analysis_results/table_scenario_weight_settings.csv](sensitivity_analysis_results/table_scenario_weight_settings.csv)

In brief:
1. Baseline: S = 0.6 PD + 0.4 GWD; AC = 0.7 I + 0.3 U; PI = 0.5 E + 0.5 S.
2. Scenario 1: groundwater-emphasis in S (0.5/0.5).
3. Scenario 2: population-emphasis in S (0.7/0.3).
4. Scenario 3: exposure-emphasis in PI (0.6E + 0.4S).
5. Scenario 4: sensitivity-emphasis in PI (0.4E + 0.6S).
6. Scenario 5: reduced income influence in AC (0.6/0.4).

### Evaluation Metrics
For each scenario, CVI was recomputed for all districts and compared with baseline using:
- Spearman rank correlation (ranking stability)
- District class stability (LOW/MODERATE/HIGH consistency)
- Hotspot overlap (Top-10 district overlap)
- High-vulnerability class overlap
- Mean CVI shift (%)

The consolidated results are provided in:
- [sensitivity_analysis_results/table_stability_diagnostics.csv](sensitivity_analysis_results/table_stability_diagnostics.csv)

### Core Results
1. Ranking robustness remained high across scenarios.
   - Spearman rho values were: 0.977 (Scenario 1), 0.993 (Scenario 2), 0.945 (Scenario 3), 0.975 (Scenario 4), and 0.869 (Scenario 5).
   - Mean correlation across alternatives was 0.952, indicating strong rank-order stability.

2. Classification stability was high.
   - Stability ranged from 85.7% to 100.0% across scenarios.
   - Reclassifications were limited (0, 0, 5, 1, 1 districts in Scenarios 1-5, respectively).

3. High-vulnerability districts were mostly preserved.
   - High-class overlap with baseline was 100% for Scenarios 1-3 and 75% for Scenarios 4-5.
   - This indicates the highest-risk core remains largely stable under moderate perturbations.

4. Hotspot composition showed moderate but interpretable shifts.
   - Top-10 overlap with baseline: 80%, 100%, 70%, 90%, 70% (Scenarios 1-5).
   - Changes occurred mainly around mid-ranked transition districts, not complete spatial reversal.

5. Score-level shifts were bounded and directional.
   - Mean CVI change (%) relative to baseline: -1.00, +1.00, +6.40, -6.40, -7.64.
   - The largest shifts occurred when PI and AC were directly reweighted, as expected.

### Interpretation for the Paper
Overall, the CVI framework demonstrates robust behavior under plausible weight perturbations. The rank structure and broad spatial pattern are preserved, while expected movement occurs primarily among moderate-vulnerability districts near class thresholds. This supports the claim that identified vulnerability patterns are not artifacts of one specific weighting choice.

A balanced interpretation is recommended:
- The model is robust for ranking and priority screening.
- Sensitivity is non-zero and policy-relevant in boundary districts, especially under PI and AC reweighting.

---

## Figure and Table Package to Include

### Figure (Main)
Use this figure in the main paper:
- [sensitivity_analysis_results/sensitivity_analysis_comparison.png](sensitivity_analysis_results/sensitivity_analysis_comparison.png)

**Suggested caption (Figure X):**
"Sensitivity analysis of CVI under alternative weight configurations (±10-20%). Panels show: (a) distribution of CVI scores by scenario, (b) baseline-versus-scenario CVI relationship (with no-change diagonal), (c) district rank changes relative to baseline, and (d) percentage CVI change by scenario. High clustering near the no-change line and low median rank shifts indicate robust ranking performance, with larger but interpretable shifts under PI and AC reweighting scenarios."

### Table 1 (Scenario Definitions)
CSV file:
- [sensitivity_analysis_results/table_scenario_weight_settings.csv](sensitivity_analysis_results/table_scenario_weight_settings.csv)

**Suggested caption (Table X):**
"Baseline and alternative weighting schemes used in sensitivity analysis for Sensitivity (PD, GWD), Adaptive Capacity (I, U), and Potential Impact (E, S) components."

### Table 2 (Robustness Outcomes)
CSV file:
- [sensitivity_analysis_results/table_stability_diagnostics.csv](sensitivity_analysis_results/table_stability_diagnostics.csv)

**Suggested caption (Table Y):**
"Scenario-wise robustness diagnostics relative to baseline, including Top-10 hotspot overlap, high-vulnerability overlap, district reclassification count, Spearman rank correlation, class stability, and mean CVI change (%)."

---

## Short Paragraph You Can Directly Paste (Results Section)
"Weight-perturbation sensitivity analysis (±10-20%) showed that CVI rankings were generally stable across alternative assumptions. Spearman rank correlation with baseline remained high (0.869-0.993; mean 0.952), while class stability ranged from 85.7% to 100.0%. Top-10 hotspot overlap was 70-100% and high-vulnerability overlap was 75-100%, indicating that the high-risk core persists across scenarios. Observed changes were concentrated in moderate-vulnerability boundary districts, especially under PI and AC reweighting, rather than reflecting wholesale spatial reordering. These results support the robustness of the assigned weights for district-level screening and prioritization."

## Short Paragraph You Can Directly Paste (Discussion Section)
"The sensitivity analysis confirms that the proposed CVI framework is robust to moderate weight perturbations, while still retaining meaningful responsiveness to alternative policy emphases. In practical terms, the model preserves priority identification under plausible assumptions and highlights transition districts where interventions may be most sensitive to planning choices. This balance of stability and responsiveness strengthens confidence that the mapped vulnerability patterns reflect underlying socio-environmental structure rather than a single arbitrary parameterization."
