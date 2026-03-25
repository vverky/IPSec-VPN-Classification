# IPSecVPN Traffic Classification - GitHub 快速推送脚本 (PowerShell)
# 用途：初始化Git仓库并推送代码到GitHub
# 用法：.\push_to_github.ps1

$ErrorActionPreference = "Continue"

# 配置变量
$GitHubUsername = "vverky"
$RepoName = "IPSec-VPN-Classification"
$RepoUrl = "https://github.com/$GitHubUsername/$RepoName.git"

# 颜色输出函数
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Info {
    param([string]$Message)
    Write-Host "➜ $Message" -ForegroundColor Cyan
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

# 标题
Write-Host "============================================" -ForegroundColor Green
Write-Host "IPSecVPN - GitHub 快速推送脚本"  -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# 步骤 1: 检查 Git 
Write-Info "检查 Git 是否已安装..."
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git 未安装！请先安装 Git: https://git-scm.com/"
    exit 1
}
Write-Success "Git 已安装"
Write-Host ""

# 步骤 2: 初始化 Git 仓库
Write-Info "检查或初始化 Git 仓库..."
if (Test-Path .\.git) {
    Write-Warning "Git 仓库已存在，跳过初始化"
} else {
    git init
    Write-Success "Git 仓库初始化完成"
}
Write-Host ""

# 步骤 3: 配置 Git 用户
Write-Info "配置 Git 用户信息..."
git config --global user.name "vverky" 2>$null
git config --global user.email "vverky@github.com" 2>$null
Write-Success "Git 用户信息配置完成"
Write-Host ""

# 步骤 4: 添加文件
Write-Info "添加所有文件到暂存区..."
git add . 2>$null
Write-Success "文件添加完成"
Write-Host ""

# 步骤 5: 创建提交
Write-Info "创建初始提交..."
$commitMessage = "Initial commit: Open source IPSecVPN Traffic Classification project"
git commit -m $commitMessage 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "初始提交创建成功"
} else {
    Write-Warning "提交已存在或无变更"
}
Write-Host ""

# 步骤 6: 配置远程仓库
Write-Info "配置远程仓库..."
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Info "远程仓库已存在，更新URL..."
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}
Write-Success "远程仓库配置完成: $RepoUrl"
Write-Host ""

# 步骤 7: 设置主分支
Write-Info "设置主分支为 main..."
git branch -M main 2>$null
Write-Success "主分支设置完成"
Write-Host ""

# 步骤 8: 推送代码
Write-Warning "准备推送代码到 GitHub..."
Write-Host ""
Write-Host "首次推送需要 GitHub 认证。选择以下方式之一:" -ForegroundColor Yellow
Write-Host "1. SSH 密钥（推荐）- 需要提前配置"
Write-Host "2. HTTPS + Personal Access Token"
Write-Host "3. HTTPS + GitHub CLI 登录"
Write-Host ""
Write-Host "正在推送..." -ForegroundColor Cyan
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Success "代码推送成功！"
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Success "项目地址: https://github.com/$GitHubUsername/$RepoName"
    Write-Host ""
    Write-Host "下一步推荐配置:" -ForegroundColor Yellow
    Write-Host "1. 在仓库中启用 GitHub Pages（如需文档网站）"
    Write-Host "2. 配置分支保护规则（Settings > Branches）"
    Write-Host "3. 启用 Discussions（Settings > Features）"
    Write-Host "4. 添加项目标签和描述"
    Write-Host "5. 邀请合作者参与开发"
} else {
    Write-Host ""
    Write-Error "推送失败！"
    Write-Host ""
    Write-Host "常见问题解决:" -ForegroundColor Yellow
    Write-Host "① SSH 密钥未配置："
    Write-Host "   - 生成密钥: ssh-keygen -t ed25519 -C 'your@email.com'"
    Write-Host "   - 添加到GitHub: https://github.com/settings/keys"
    Write-Host ""
    Write-Host "② Personal Access Token 方法："
    Write-Host "   - 创建 Token: https://github.com/settings/tokens"
    Write-Host "   - 使用 Token: git push (输入用户名和token作为密码)"
    Write-Host ""
    Write-Host "③ 仓库不存在："
    Write-Host "   - 访问: https://github.com/new"
    Write-Host "   - 创建仓库: $RepoName"
    exit 1
}

Write-Host ""
Read-Host "按 Enter 关闭此窗口"
