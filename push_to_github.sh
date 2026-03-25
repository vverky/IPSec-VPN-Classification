#!/bin/bash
#
# IPSecVPN Traffic Classification - GitHub 快速推送脚本
# 用途：初始化Git仓库并推送代码到GitHub
#

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== IPSecVPN Traffic Classification - GitHub 推送脚本 ===${NC}\n"

# 配置变量
#GITHUB_USERNAME="vverky"
#REPO_NAME="IPSec-VPN-Classification"

#echo -e "${YELLOW}请确保已在GitHub上创建仓库:${NC}"
#echo "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
#read -p "按Enter继续..." 

# 1. 检查是否已初始化
if [ -d .git ]; then
    echo -e "${YELLOW}Git仓库已存在，跳过初始化${NC}"
else
    echo -e "${GREEN}初始化Git仓库...${NC}"
    git init
    echo -e "${GREEN}✓ Git仓库初始化完成${NC}\n"
fi

# 2. 配置Git用户信息
echo -e "${GREEN}配置Git用户信息...${NC}"
git config --global user.name "vverky" 2>/dev/null || true
git config --global user.email "vverky@github.com" 2>/dev/null || true
echo -e "${GREEN}✓ 用户信息配置完成${NC}\n"

# 3. 添加所有文件
echo -e "${GREEN}添加所有文件...${NC}"
git add .
echo -e "${GREEN}✓ 文件添加完成${NC}\n"

# 4. 创建首次提交
echo -e "${GREEN}创建首次提交...${NC}"
git commit -m "Initial commit: Open source IPSecVPN Traffic Classification project" || echo -e "${YELLOW}提交已存在或无变更${NC}"
echo -e "${GREEN}✓ 首次提交完成${NC}\n"

# 5. 检查和添加远程仓库
REPO_URL="https://github.com/vverky/IPSec-VPN-Classification.git"
echo -e "${GREEN}配置远程仓库: $REPO_URL${NC}"

if git remote | grep -q origin; then
    echo -e "${YELLOW}远程仓库已存在，更新URL...${NC}"
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi
echo -e "${GREEN}✓ 远程仓库配置完成${NC}\n"

# 6. 设置主分支
echo -e "${GREEN}设置主分支为main...${NC}"
git branch -M main
echo -e "${GREEN}✓ 主分支设置完成${NC}\n"

# 7. 推送代码
echo -e "${YELLOW}准备推送代码到GitHub...${NC}"
echo -e "${YELLOW}如果这是第一次推送，将需要GitHub认证。${NC}"
echo -e "${YELLOW}建议方法：使用SSH密钥或GitHub Personal Access Token${NC}\n"

git push -u origin main

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}=== 推送成功! ===${NC}"
    echo -e "${GREEN}✓ 代码已成功上传到 GitHub${NC}"
    echo -e "${GREEN}✓ 访问: https://github.com/vverky/IPSec-VPN-Classification${NC}"
else
    echo -e "\n${RED}=== 推送失败 ===${NC}"
    echo -e "${RED}✗ 请检查以下内容:${NC}"
    echo "1. GitHub仓库是否已创建"
    echo "2. 是否已配置SSH密钥或Personal Access Token"
    echo "3. 网络连接是否正常"
    exit 1
fi

echo -e "\n${GREEN}下一步:${NC}"
echo "1. 在 GitHub 上配置分支保护规则"
echo "2. 启用 Issues 和 Discussions"
echo "3. 配置项目信息和标签"
