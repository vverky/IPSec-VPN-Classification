@echo off
REM IPSecVPN Traffic Classification - GitHub 快速推送脚本 (Windows)
REM 用途：初始化Git仓库并推送代码到GitHub

setlocal enabledelayedexpansion

echo.
echo ===== IPSecVPN Traffic Classification - GitHub 推送脚本 =====
echo.

set GITHUB_USERNAME=vverky
set REPO_NAME=IPSec-VPN-Classification
set REPO_URL=https://github.com/!GITHUB_USERNAME!/!REPO_NAME!.git

echo 请确保已在GitHub上创建仓库:
echo https://github.com/!GITHUB_USERNAME!/!REPO_NAME!
echo.

REM 1. 检查是否已初始化
if exist .git (
    echo Git仓库已存在，跳过初始化
) else (
    echo 初始化Git仓库...
    git init
    echo ✓ Git仓库初始化完成
    echo.
)

REM 2. 配置Git用户信息
echo 配置Git用户信息...
git config --global user.name "vverky" 2>nul
git config --global user.email "vverky@github.com" 2>nul
echo ✓ 用户信息配置完成
echo.

REM 3. 添加所有文件
echo 添加所有文件...
git add .
echo ✓ 文件添加完成
echo.

REM 4. 创建首次提交
echo 创建首次提交...
git commit -m "Initial commit: Open source IPSecVPN Traffic Classification project"
if errorlevel 1 (
    echo 提交已存在或无变更
)
echo ✓ 首次提交完成
echo.

REM 5. 检查和添加远程仓库
echo 配置远程仓库: !REPO_URL!
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    git remote add origin "!REPO_URL!"
) else (
    git remote set-url origin "!REPO_URL!"
)
echo ✓ 远程仓库配置完成
echo.

REM 6. 设置主分支
echo 设置主分支为main...
git branch -M main
echo ✓ 主分支设置完成
echo.

REM 7. 推送代码
echo 准备推送代码到GitHub...
echo 如果这是第一次推送，将需要GitHub认证。
echo 建议方法：使用SSH密钥或GitHub Personal Access Token
echo.

git push -u origin main
if errorlevel 0 (
    echo.
    echo ===== 推送成功! =====
    echo ✓ 代码已成功上传到 GitHub
    echo ✓ 访问: https://github.com/!GITHUB_USERNAME!/!REPO_NAME!
    echo.
    echo 下一步:
    echo 1. 在 GitHub 上配置分支保护规则
    echo 2. 启用 Issues 和 Discussions
    echo 3. 配置项目信息和标签
) else (
    echo.
    echo ===== 推送失败 =====
    echo ✗ 请检查以下内容:
    echo 1. GitHub仓库是否已创建
    echo 2. 是否已配置SSH密钥或Personal Access Token
    echo 3. 网络连接是否正常
)

pause
