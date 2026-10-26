$ErrorActionPreference = 'Continue'
$env:PYTHONUTF8 = 1
$py = ".venv\Scripts\python.exe"
$R  = "D:\software\R-4.6.1\bin\x64\Rscript.exe"
$log = ".audit_tmp\restore_chain.log"
"=== chain start $(Get-Date -Format s) ===" | Out-File $log -Encoding utf8

function Step($name, $exe, $argv) {
  "`n##### $name #####" | Out-File $log -Append -Encoding utf8
  $t0 = Get-Date
  & $exe @argv *>&1 | Out-File $log -Append -Encoding utf8
  $code = $LASTEXITCODE
  "--> $name exit=$code elapsed=$([int]((Get-Date)-$t0).TotalSeconds)s" | Out-File $log -Append -Encoding utf8
}

Step "evaluate_knhanes"     $py @("scripts\evaluate_knhanes.py")
Step "evaluate_charls"      $py @("scripts\evaluate_charls.py")
Step "evaluate_charls2015"  $py @("scripts\evaluate_charls2015.py")
Step "survey_export"        $py @("scripts\survey_sensitivity_export.py")
Step "survey_R_svyglm"      $R  @("--vanilla","scripts\survey_sensitivity_R5.R")
Step "apply_survey_var"     $py @("scripts\apply_survey_variance.py")
Step "rebuild_deliverables" $py @("scripts\rebuild_deliverables_R5.py")
Step "paper_tables"         $py @("scripts\generate_paper_tables.py")
"`n=== chain end $(Get-Date -Format s) ===" | Out-File $log -Append -Encoding utf8
