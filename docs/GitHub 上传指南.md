# 🚀 GitHub 上传指南

> 手把手教你把这个仓库推送到 GitHub，开始你的开源量化学习之旅。

---

## 前置条件

1. **已安装 Git**
   - 在终端输入 `git --version`，如果显示版本号则说明已安装
   - 未安装请前往 [git-scm.com](https://git-scm.com/) 下载安装

2. **已有 GitHub 账号**
   - 前往 [github.com](https://github.com) 注册

3. **已配置 Git 用户名和邮箱**
   ```bash
   git config --global user.name "你的GitHub用户名"
   git config --global user.email "你的GitHub邮箱"
   ```

---

## 方式一：通过 HTTPS 推送（推荐新手）

### 步骤 1：在 GitHub 上创建空仓库

1. 登录 GitHub，点击右上角 `+` → `New repository`
2. 填写仓库信息：
   - **Repository name**: `quant-learning`（或其他你喜欢的名字）
   - **Description**: 我的量化交易开源学习笔记
   - **Visibility**: 选择 `Public`（公开，推荐开源）或 `Private`（私有）
   - **Initialize this repository with**: **什么都不要勾选**（不要勾选 README、.gitignore、license）
3. 点击 `Create repository`

### 步骤 2：在本地初始化并推送

打开 PowerShell 或 CMD，执行以下命令：

```powershell
# 进入仓库目录
cd E:\PYcharm\Python_code\quant-learning

# 初始化 Git 仓库
git init

# 添加所有文件到暂存区
git add .

# 提交第一次更改
git commit -m "init: 量化交易学习仓库初始化"

# 关联远程仓库（把下面的用户名换成你的 GitHub 用户名）
git remote add origin https://github.com/你的用户名/quant-learning.git

# 推送到 GitHub 主分支
git branch -M main
git push -u origin main
```

推送时会弹窗让你输入 GitHub 的用户名和密码。注意：
- **密码不是你的登录密码**，而是 GitHub 的 **Personal Access Token（PAT）**
- 如果你不知道 PAT，建议看下面的「关于 Personal Access Token」

---

## 方式二：通过 SSH 推送（推荐长期使用者）

### 步骤 1：生成 SSH 密钥

如果你还没有配置过 SSH，先执行：

```bash
ssh-keygen -t ed25519 -C "你的GitHub邮箱"
```

一路按回车，默认保存到 `C:\Users\你的用户名\.ssh\`。

### 步骤 2：将公钥添加到 GitHub

1. 打开文件 `C:\Users\你的用户名\.ssh\id_ed25519.pub`，复制里面的全部内容
2. 登录 GitHub → 右上角头像 → `Settings` → 左侧 `SSH and GPG keys`
3. 点击 `New SSH key`，粘贴公钥，Title 随便写（如 "我的电脑"），保存

### 步骤 3：推送代码

```powershell
cd E:\PYcharm\Python_code\quant-learning
git init
git add .
git commit -m "init: 量化交易学习仓库初始化"

# SSH 地址
git remote add origin git@github.com:你的用户名/quant-learning.git
git branch -M main
git push -u origin main
```

---

## 🔑 关于 Personal Access Token（PAT）

GitHub 从 2021 年起不再支持用密码直接通过 HTTPS 推送，需要用 Token 代替密码。

### 创建 Token 的步骤

1. 登录 GitHub → 右上角头像 → `Settings`
2. 左侧最下方 `Developer settings` → `Personal access tokens` → `Tokens (classic)`
3. 点击 `Generate new token (classic)`
4. **Note**: 写个备注，比如 "quant-learning-push"
5. **Expiration**: 选择过期时间（建议 90 天或 No expiration）
6. **Scopes**: 至少勾选 `repo`
7. 点击 `Generate token`
8. **立刻复制显示的 token**（只显示一次！）

### 使用 Token

在 `git push` 时，弹出的密码框里**粘贴这个 Token** 即可。

---

## 📝 日常更新流程

以后每次有新内容，按这个流程推送：

```powershell
cd E:\PYcharm\Python_code\quant-learning

# 查看文件改动状态
git status

# 添加所有改动
git add .

# 提交（写清楚这次做了什么）
git commit -m "feat: 添加了双均线策略的回测代码"

# 推送到 GitHub
git push origin main
```

### 提交信息规范（推荐）

| 前缀 | 含义 | 示例 |
|------|------|------|
| `init:` | 初始化 | `init: 仓库初始化` |
| `feat:` | 新功能/新内容 | `feat: 添加布林带均值回归策略` |
| `fix:` | 修复 bug | `fix: 修正收益率计算错误` |
| `docs:` | 文档更新 | `docs: 更新学习路线图` |
| `refactor:` | 代码重构 | `refactor: 优化数据清洗逻辑` |
| `data:` | 数据更新 | `data: 添加 2025 年样本数据` |

---

## 🛠️ 常见问题

### Q1: `git push` 提示 "fatal: not a git repository"
**A**: 你没有在正确的目录下执行命令。先 `cd` 到 `quant-learning` 文件夹里。

### Q2: `git push` 提示 "fatal: Authentication failed"
**A**: 你的用户名或 Token 输错了。重新检查 Token 是否正确，或换 SSH 方式。

### Q3: GitHub 仓库已经勾选了 README，导致 push 失败
**A**: 远程仓库和本地仓库历史不一致。解决方法：
```bash
git pull origin main --rebase
git push origin main
```

### Q4: 我想改仓库名字怎么办？
**A**: 
- GitHub 上：进入仓库 → `Settings` → 修改 `Repository name`
- 本地：用 `git remote set-url origin 新的仓库地址`

---

## 🎉 推送成功后的检查清单

- [ ] 在 GitHub 上能看到所有文件
- [ ] `README.md` 能正常渲染
- [ ] `.gitignore` 生效（数据文件、环境变量没有上传）
- [ ] 给仓库点一个 ⭐ Star（自己先支持自己！）

---

*祝你开源学习愉快！*
