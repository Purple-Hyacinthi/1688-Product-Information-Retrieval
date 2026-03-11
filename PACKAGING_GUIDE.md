# 1688商品搜索工具打包指南

本文档详细说明如何将1688商品搜索工具打包为可执行应用程序，支持Windows和macOS平台。

## 目录

1. [准备工作](#准备工作)
2. [Windows打包](#windows打包)
3. [macOS打包](#macos打包)
4. [高级配置](#高级配置)
5. [故障排除](#故障排除)

## 准备工作

### 1. 安装必要工具

确保已安装以下工具：

- Python 3.8+
- pip（Python包管理器）
- Git（可选，用于克隆仓库）

### 2. 克隆项目代码

```bash
git clone <项目仓库地址>
cd 1688-product-search
```

### 3. 安装项目依赖

```bash
pip install -r requirements.txt
```

### 4. 安装打包工具

```bash
pip install pyinstaller
```

### 5. 准备图标文件（可选）

为应用程序准备图标文件：

- **Windows**: `.ico` 格式，建议尺寸：256x256、128x128、64x64、32x32、16x16
- **macOS**: `.icns` 格式，建议包含多种尺寸

将图标文件放置在 `icons/` 目录下：
- Windows图标: `icons/app.ico`
- macOS图标: `icons/app.icns`

如果没有图标文件，打包时将使用默认图标。

## Windows打包

### 方法一：使用提供的spec文件（推荐）

```bash
# 清理之前的构建
pyinstaller --clean build.spec

# 或者不显示确认提示
pyinstaller --clean --noconfirm build.spec
```

### 方法二：使用命令行参数

```bash
# 基本打包命令
pyinstaller --name="1688 Product Search" \
            --windowed \
            --icon=icons/app.ico \
            --add-data="config;config" \
            --add-data="README.md;." \
            --hidden-import=openai \
            --hidden-import=requests \
            --hidden-import=tkinter \
            --hidden-import=src.config_manager \
            --hidden-import=src.alibaba_client \
            --hidden-import=src.llm_agent \
            --hidden-import=src.main_window \
            --hidden-import=src.product_model \
            --exclude-module=pytest \
            --exclude-module=test \
            --exclude-module=tests \
            main.py
```

### 打包结果

打包完成后，可在以下目录找到可执行文件：

- **单个可执行文件**: `dist/1688_Product_Search/1688_Product_Search.exe`
- **完整分发目录**: `dist/1688_Product_Search/`

### 测试打包结果

1. 导航到分发目录：
   ```bash
   cd dist/1688_Product_Search
   ```

2. 运行应用程序：
   ```bash
   ./1688_Product_Search.exe
   ```

3. 验证功能：
   - 应用程序应正常启动
   - 配置窗口应能打开
   - 搜索功能应正常工作（需配置API密钥）

## macOS打包

### 1. 环境要求

- macOS 10.15+
- Python 3.8+
- 建议使用虚拟环境

### 2. 安装依赖

```bash
# 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller
```

### 3. 准备macOS特定文件

#### 图标文件
创建macOS应用程序图标（.icns格式）：

```bash
# 使用iconutil工具（需要准备多尺寸PNG）
mkdir MyIcon.iconset
# 将不同尺寸的PNG图标放入iconset目录
# 然后运行：
iconutil -c icns MyIcon.iconset -o icons/app.icns
```

#### 权限配置
macOS应用程序可能需要以下权限：
- 网络访问（用于API调用）
- 文件系统访问（用于读写配置）

### 4. 打包命令

#### 使用spec文件（推荐）

```bash
# 确保在项目根目录
pyinstaller --clean build.spec
```

spec文件已包含macOS特定配置，将生成 `.app` 应用程序包。

#### 自定义打包

```bash
pyinstaller --name="1688 Product Search" \
            --windowed \
            --icon=icons/app.icns \
            --add-data="config:config" \
            --add-data="README.md:." \
            --osx-bundle-identifier="com.example.1688productsearch" \
            --hidden-import=openai \
            --hidden-import=requests \
            --hidden-import=tkinter \
            --hidden-import=src.config_manager \
            --hidden-import=src.alibaba_client \
            --hidden-import=src.llm_agent \
            --hidden-import=src.main_window \
            --hidden-import=src.product_model \
            main.py
```

### 5. 打包结果

打包完成后，将生成以下文件：

- **macOS应用程序包**: `dist/1688 Product Search.app`
- **可执行文件位置**: `dist/1688 Product Search.app/Contents/MacOS/1688_Product_Search`

### 6. 测试和签名

#### 测试应用程序

```bash
# 直接运行应用程序包
open "dist/1688 Product Search.app"
```

或

```bash
# 运行内部可执行文件
./dist/1688\ Product\ Search.app/Contents/MacOS/1688_Product_Search
```

#### 应用程序签名（发布前必需）

```bash
# 使用开发者证书签名
codesign --force --deep --sign "Developer ID Application: Your Name (TeamID)" "dist/1688 Product Search.app"

# 验证签名
codesign -vvv --deep --strict "dist/1688 Product Search.app"
```

#### 公证（适用于App Store分发）

```bash
# 创建压缩包
ditto -c -k --keepParent "dist/1688 Product Search.app" "1688_Product_Search.zip"

# 提交公证
xcrun notarytool submit "1688_Product_Search.zip" \
  --keychain-profile "AC_PASSWORD" \
  --wait
```

### 7. 创建DMG安装包（可选）

```bash
# 安装create-dmg
brew install create-dmg

# 创建DMG
create-dmg \
  --volname "1688 Product Search" \
  --volicon "icons/app.icns" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "1688 Product Search.app" 200 190 \
  --hide-extension "1688 Product Search.app" \
  --app-drop-link 600 185 \
  "dist/1688_Product_Search.dmg" \
  "dist/1688 Product Search.app"
```

## 高级配置

### 自定义spec文件

`build.spec` 文件包含完整的打包配置。您可以修改以下部分：

#### 1. 数据文件

```python
# 添加额外数据文件
datas.append(('path/to/file', 'destination/directory'))
```

#### 2. 隐藏导入

```python
# 添加额外的隐藏导入
hiddenimports.append('module.name')
```

#### 3. 排除模块

```python
# 排除不必要的模块以减少体积
excludes.append('unnecessary.module')
```

#### 4. 应用程序信息（macOS）

```python
info_plist={
    'CFBundleName': '1688 Product Search',
    'CFBundleDisplayName': '1688 Product Search',
    'CFBundleVersion': '1.0.0',
    'CFBundleShortVersionString': '1.0.0',
    'CFBundleExecutable': '1688_Product_Search',
    'CFBundleDevelopmentRegion': 'English',
    'CFBundlePackageType': 'APPL',
    'NSHumanReadableCopyright': 'Copyright © 2026. All rights reserved.',
    'NSHighResolutionCapable': 'True',
    'NSRequiresAquaSystemAppearance': False,
}
```

### 优化打包体积

1. **使用UPX压缩**（已默认启用）
   ```python
   upx=True  # 在spec文件中
   ```

2. **排除开发依赖**
   ```python
   excludes=['pytest', 'test', 'tests', '__pycache__']
   ```

3. **使用虚拟环境**确保只包含必要的包

### 多平台打包

要为多个平台打包，需要在各自的操作系统上运行PyInstaller：

1. **Windows**: 在Windows上打包
2. **macOS**: 在macOS上打包
3. **Linux**: 在Linux上打包

## 故障排除

### 常见问题

#### 1. 应用程序启动失败

**症状**: 双击应用程序无反应或立即退出

**解决方案**:
- 检查控制台输出（Windows: 在命令提示符中运行exe；macOS: 在终端中运行）
- 验证所有依赖是否包含
- 检查数据文件路径

#### 2. 缺少模块错误

**症状**: `ModuleNotFoundError` 或 `ImportError`

**解决方案**:
- 在spec文件的 `hiddenimports` 中添加缺少的模块
- 确保所有源文件都正确包含

#### 3. 配置文件无法访问

**症状**: 配置无法保存或加载

**解决方案**:
- 检查数据文件是否正确包含
- 验证文件路径（打包后路径可能变化）
- 确保应用程序有写入权限

#### 4. macOS应用程序被阻止

**症状**: "无法打开应用程序，因为无法验证开发者"

**解决方案**:
1. 临时解决方案：右键点击 → 打开
2. 永久解决方案：对应用程序进行签名
3. 在系统设置中允许来自任何来源的应用（不推荐）

#### 5. 打包体积过大

**症状**: 可执行文件超过100MB

**解决方案**:
- 使用虚拟环境避免包含不必要的包
- 启用UPX压缩
- 排除测试和开发模块
- 使用 `--exclude-module` 排除不必要的标准库模块

### 调试技巧

1. **查看详细打包日志**:
   ```bash
   pyinstaller --debug=all build.spec
   ```

2. **测试未打包版本**:
   ```bash
   python main.py
   ```

3. **检查包含的文件**:
   ```bash
   # Windows
   dir /s dist\1688_Product_Search
   
   # macOS/Linux
   find dist/1688_Product_Search -type f
   ```

4. **查看导入跟踪**:
   ```python
   # 在代码中添加
   import traceback
   traceback.print_stack()
   ```

## 发布准备

### 1. 版本管理

- 更新 `build.spec` 中的版本号
- 更新README文档
- 创建发布标签

### 2. 测试清单

- [ ] 应用程序在目标平台启动
- [ ] 所有功能正常工作
- [ ] 配置文件可读写
- [ ] 网络功能正常（API调用）
- [ ] 用户界面显示正确
- [ ] 无控制台错误

### 3. 分发文件

#### Windows
- `1688_Product_Search.exe`（单个可执行文件）
- 或 `1688_Product_Search.zip`（完整目录）

#### macOS
- `1688 Product Search.app`（应用程序包）
- `1688_Product_Search.dmg`（安装镜像）

#### 通用
- `requirements.txt`（依赖列表）
- `README.md`（使用说明）
- `PACKAGING_GUIDE.md`（打包指南）

## 支持与反馈

如果在打包过程中遇到问题：

1. 查看PyInstaller官方文档：https://pyinstaller.org
2. 检查项目GitHub Issues
3. 提供以下信息寻求帮助：
   - 操作系统版本
   - Python版本
   - PyInstaller版本
   - 完整错误信息
   - 使用的打包命令

---

*最后更新: 2026-03-11*