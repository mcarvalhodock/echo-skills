# Invólucro do loop SLE. Três linhas em vez de um pacote: o repositório não tem
# empacotamento, e criar um para isto traria versionamento e ciclo de release
# que ninguém pediu.
$ErrorActionPreference = 'Stop'
$clone = Split-Path -Parent $PSScriptRoot
& python (Join-Path $clone 'tooling/loop/driver.py') @args
exit $LASTEXITCODE
