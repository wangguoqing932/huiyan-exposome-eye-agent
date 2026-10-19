# Table 2. The 21 literature-derived exposome rules: entity flags, direction, evidence level and source

| rule_id | severity | risk_type | evidence_level | direction | a_flags | b_flags | negative_control | note |
|---|---|---|---|---|---|---|---|---|
| r01_uric_acid_x_cataract | low | inflammation_immune | C | risk_up | uric_acid_elevated | cataract_any | True |  |
| r02_hyperglycemia_x_cataract | medium | glycation_metabolic | B | risk_up | hyperglycemia,hba1c_elevated | cataract_any | False |  |
| r03_hba1c_x_retinopathy_any | medium | glycation_metabolic | B | risk_up | hba1c_elevated,hyperglycemia | retinopathy_any | False |  |
| r04_hba1c_x_dr_pdr | low | vascular_perfusion | C | risk_up | hba1c_elevated,hyperglycemia | dr_pdr,dr_npdr | False |  |
| r05_dyslipidemia_x_amd_late | low | oxidative_stress | C | risk_up | dyslipidemia | amd_late | False |  |
| r06_crp_x_amd_late | medium | inflammation_immune | B | risk_up | crp_elevated | amd_late | False |  |
| r07_vitamind_x_dr_npdr | medium | endocrine_hormonal | B | risk_up | vitamin_d_deficiency | dr_npdr | False |  |
| r08_low_antioxidant_x_cataract | medium | oxidative_stress | B | risk_up | low_antioxidant_intake | cataract_any | False |  |
| r09_mediterranean_diet_x_amd_late | medium | oxidative_stress | B | risk_down | mediterranean_diet | amd_late | False |  |
| r10_smoking_x_cataract | medium | oxidative_stress | B | risk_up | current_smoking | cataract_any | False |  |
| r11_smoking_x_amd_late | high | oxidative_stress | A | risk_up | current_smoking | amd_late | False |  |
| r12_alcohol_x_cataract | medium | oxidative_stress | B | risk_up | alcohol_intake | cataract_any | False |  |
| r13_bmi_x_cataract | medium | glycation_metabolic | B | risk_up | bmi_high | cataract_any | False |  |
| r14_lead_x_cataract | medium | heavy_metal_toxicity | B | risk_up | lead_exposure | cataract_any | False |  |
| r16_pm25_x_glaucoma_iop_cdr | medium | vascular_perfusion | B | risk_up | pm25_exposure | glaucoma_iop_elevated,glaucoma_suspect_cdr | False |  |
| r17_pm25_x_amd_early | medium | inflammation_immune | B | risk_up | pm25_exposure | amd_early | False |  |
| r18_uv_x_cataract | medium | photochemical_uv | B | risk_up | uv_exposure | cataract_any | False |  |
| r22_bmi_x_retinopathy | low | inflammation_immune | C | risk_up | bmi_high | retinopathy_any,dr_npdr | False |  |
| r19_proinflam_diet_x_dr_npdr | low | inflammation_immune | C | risk_up | pro_inflammatory_diet | dr_npdr | False |  |
| r20_smoking_x_vi_mod_severe | medium | oxidative_stress | B | risk_up | current_smoking | vision_impairment_moderate,vision_impairment_severe | False |  |
| r21_pm25_x_vi_mod_severe | medium | vascular_perfusion | B | risk_up | pm25_exposure | vision_impairment_moderate,vision_impairment_severe | False |  |
