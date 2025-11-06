# PowerShell 启动脚本

Write-Host "========================================"
Write-Host "  Telegram 商户管理机器人"
Write-Host "========================================"
Write-Host ""

# 激活虚拟环境（如果存在）
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "正在激活虚拟环境..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# 检查 .env 文件
if (-not (Test-Path ".env")) {
    Write-Host "[错误] .env 文件不存在！" -ForegroundColor Red
    Write-Host "请先创建 .env 文件："
    Write-Host "  Copy-Item env.template .env"
    Write-Host "然后编辑配置。"
    Write-Host ""
    Read-Host "按回车键退出"
    exit 1
}

# 设置 PYTHONPATH
$env:PYTHONPATH = Get-Location

# 启动 Bot
Write-Host "正在启动 Bot..." -ForegroundColor Green
Write-Host ""
python app/main.py

