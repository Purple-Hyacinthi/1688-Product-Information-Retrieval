# GitHub Actions自动构建配置指南

## 已完成的配置

项目已包含完整的GitHub Actions配置（`.github/workflows/build.yml`），支持：
- 自动构建Windows可执行文件（.exe）
- 自动构建macOS应用程序包（.app）
- 测试运行
- 创建GitHub Release（当推送版本标签时）

## 下一步操作

### 1. 推送代码到GitHub仓库

由于网络连接问题，需要手动配置git认证或使用其他方式上传代码。

#### 方法A：使用GitHub Personal Access Token（推荐）

1. 生成GitHub Token：
   - 访问 https://github.com/settings/tokens
   - 点击"Generate new token"
   - 选择"classic" token
   - 权限：至少选择`repo`（完全控制仓库）
   - 生成并复制token

2. 配置git使用token：
   ```bash
   # 设置远程仓库（如果尚未设置）
   git remote add origin https://github.com/Purple-Hyacinthi/1688-Product-Information-Retrieval.git
   
   # 使用token推送（将YOUR_TOKEN替换为实际token）
   git push https://YOUR_TOKEN@github.com/Purple-Hyacinthi/1688-Product-Information-Retrieval.git master
   
   # 或配置credential helper
   git config --global credential.helper store
   # 然后推送，输入用户名和token作为密码
   ```

#### 方法B：使用GitHub CLI（gh）

1. 安装GitHub CLI：https://cli.github.com
2. 认证：
   ```bash
   gh auth login
   ```
3. 推送代码：
   ```bash
   git push origin master
   ```

#### 方法C：GitHub网页上传

1. 访问仓库：https://github.com/Purple-Hyacinthi/1688-Product-Information-Retrieval
2. 点击"Add file" → "Upload files"
3. 上传整个项目目录（除了`dist/`, `APP/`, `__pycache__/`, `.git`等）
4. 或只上传必要的文件：
   - `.github/workflows/build.yml`
   - 所有源代码文件
   - 配置文件
   - 文档文件

### 2. 触发自动构建

代码推送到GitHub后，GitHub Actions会自动运行：

#### 手动触发构建：
1. 访问仓库的"Actions"标签页
2. 选择"Build and Release"工作流
3. 点击"Run workflow"
4. 选择分支（master）并运行

#### 通过标签触发发布：
```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0
```

### 3. 下载构建产物

构建完成后：
1. 访问仓库的"Actions"标签页
2. 点击最新的工作流运行
3. 在"Artifacts"部分下载：
   - `1688-product-search-windows` (Windows版本)
   - `1688-product-search-macos` (macOS版本)

### 4. 创建正式发布（可选）

当推送版本标签（如`v1.0.0`）时：
1. GitHub Actions会自动创建Release
2. 包含Windows和macOS构建产物
3. 自动生成发布说明

## 构建产物说明

### Windows版本
- `1688_Product_Search.exe` - 主程序
- `config/` - 配置文件目录
- `README.md` - 说明文档
- `run.bat` - 运行脚本

### macOS版本
- `1688 Product Search.app` - 应用程序包
- 或 `1688_Product_Search` - 可执行文件
- `config/` - 配置文件目录
- `README.md` - 说明文档
- `run.sh` - 运行脚本

## macOS应用程序注意事项

### 代码签名
生成的macOS应用程序**未进行代码签名**。用户首次打开时需要：
1. 右键点击应用程序
2. 选择"打开"
3. 在安全对话框中点击"打开"

### 签名建议（如需分发）
```bash
# 使用开发者证书签名
codesign --force --deep --sign "Developer ID Application: Your Name (TeamID)" "1688 Product Search.app"

# 验证签名
codesign -vvv --deep --strict "1688 Product Search.app"
```

## 故障排除

### 构建失败
1. 检查Python版本兼容性
2. 确保所有依赖在`requirements.txt`中
3. 查看GitHub Actions日志中的具体错误

### 应用程序无法运行
1. Windows：在命令行中运行查看错误信息
2. macOS：在终端中运行查看错误信息
   ```bash
   ./1688\ Product\ Search.app/Contents/MacOS/1688_Product_Search
   ```

### 配置文件问题
确保配置文件正确包含：
- `config/settings.example.json` → 复制为 `config/settings.json`
- 配置正确的API密钥

## 自定义构建配置

如需修改构建配置，编辑`.github/workflows/build.yml`：

### 修改Python版本
```yaml
matrix:
  python-version: ['3.9', '3.10', '3.11']  # 添加或删除版本
```

### 添加构建步骤
参考PyInstaller文档：https://pyinstaller.org

### 修改应用程序信息
编辑`build.spec`文件中的macOS应用程序配置。

## 支持

如有问题：
1. 查看GitHub Actions文档：https://docs.github.com/en/actions
2. 查看PyInstaller文档：https://pyinstaller.org
3. 检查项目GitHub Issues

---

*配置完成时间：2026-03-11*