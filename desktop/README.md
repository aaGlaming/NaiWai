# 奶蛙世界 Windows 桌面版

桌面版把 Vue 前端、FastAPI 后端、SQLite 数据库和图片资源封装在一起。最终用户不需要安装 Python、Node.js 或 MySQL，也不需要联网。

## 用户数据

程序默认把可变数据保存在：

`%LOCALAPPDATA%\NAIWA`

- `data\naiwa.db`：SQLite 数据库
- `backups`：默认备份目录
- `logs\naiwa.log`：运行日志
- `settings.json`：本机随机密钥

卸载程序不会删除上述个人数据。用户可在“个人中心 → 本地数据管理”中备份、恢复或打开数据目录。

## 构建环境

- Windows 10/11 x64
- Node.js 与 npm
- `backend\venv` 中已安装 `requirements-desktop.txt`
- Inno Setup 7（安装向导使用其官方简体中文语言包）

## 构建

在项目根目录执行：

```powershell
desktop\build_release.ps1
```

生成结果：`desktop\release\NAIWA-Setup-1.0.0.exe`

PyInstaller 中间文件、程序目录和安装包输出均已加入 `.gitignore`。

## 验证独立程序

```powershell
$env:NAIWA_DATA_DIR = (Resolve-Path .\desktop).Path + "\build\smoke-data"
$process = Start-Process .\desktop\dist\NAIWA\NAIWA.exe -ArgumentList "--smoke-test" -Wait -PassThru
$process.ExitCode
```

返回 `0` 表示内置前端、数据库结构和初始化数据均可用。
