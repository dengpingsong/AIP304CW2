# AIP304CW2

AIP304 Machine Learning Coursework 2 的独立项目，已配置中英文 PDF 自动构建。

目标仓库：<https://github.com/dengpingsong/AIP304CW2>

本项目参考 CPT204 报告自动构建的思路，采用 Python 构建脚本、XeLaTeX、xeCJK 和 GitHub Actions。它可以从这个目录直接初始化为新 Git 仓库，无需任何旧项目文件、补丁、Java 程序或子模块。

## 首次上传到已经创建的空仓库

解压 `AIP304CW2-starter.zip` 后，进入其中的 `AIP304CW2` 项目目录。确认当前目录能看到本 README、`report/`、`scripts/` 和 `.github/`。如果使用 macOS，`.github` 是隐藏目录，但 Git 会正常处理。

从项目目录执行以下命令，遇到错误会立即停止：

```bash
bash <<'SH'
set -euo pipefail
test -f report/main.tex
test -f .github/workflows/aip304-cw2-pdf.yml
git init -b main
git add -- .gitignore README.md .github/workflows/aip304-cw2-pdf.yml scripts/build_aip304_report.py report/
git commit -m "Set up bilingual AIP304 CW2 PDF workflow"
git remote add origin https://github.com/dengpingsong/AIP304CW2.git
git push -u origin main
SH
```

这些命令用于新解压的项目，且目标 GitHub 仓库尚未有提交。若已经完成首次提交或配置了 `origin`，无需重复初始化或再次添加同名远端。后续更新使用普通 `git add`、`git commit` 和 `git push`。

推送后，打开 **Actions → AIP304 CW2 PDF**，进入成功的运行，在 **Artifacts** 下载 PDF。也可以在 `main` 分支的 **Run workflow** 中选择语言和模式。

## 平时编辑的位置

| 路径 | 内容 |
| --- | --- |
| `report/report.json` | Option 1/2、标题、成员姓名及学号、AI 使用声明和贡献声明 |
| `report/content/en.tex` | 英文正文 |
| `report/content/zh.tex` | 中文正文 |
| `report/references.bib` | 参考文献 |
| `report/generated/` | notebook 导出的真实图表 |
| `report/main.tex` | 中英文共享版式 |
| `scripts/build_aip304_report.py` | 本地与 CI 共用的构建和检查脚本 |
| `.github/workflows/aip304-cw2-pdf.yml` | GitHub Actions 工作流 |

初始正文是写作模板，包含明确的 `TODO` 和图表占位；请替换为自己的实验和分析。中英文正文独立维护，选择语言不会自动翻译。

## 自动构建和提交前检查

修改 `report/`、构建脚本或工作流并 push，或创建包含这些改动的 pull request，会自动构建两种语言的 `preview`。手动运行可选择：

- `language`: `all`、`en` 或 `zh`。
- `mode`: `preview` 允许明显标记的占位内容；`submission` 拒绝未填写的姓名、学号、声明及正文占位。

两种模式都检查整个 PDF 不超过 5 页、字体嵌入、中文缺字、引用解析及明显的内容溢出。只有所选语言全部通过后，才发布可下载 PDF；失败日志另存为诊断产物。

本地安装好 TeX Live、字体和 Poppler 后运行：

```bash
python3 scripts/build_aip304_report.py --language all --mode preview
python3 scripts/build_aip304_report.py --language en --mode submission
```

安装依赖、排版说明和 notebook 图表接入方式，见 [报告使用说明](report/README.md)。构建脚本只用 Python 标准库。GitHub runner 会自行安装所需排版工具，不需要你为了云端构建先在 Mac 安装 LaTeX。

## CW2 格式约束

根据所提供任务书第 7 页 §6.2–6.5：最终提交一份 PDF，总计最多 5 页，包含图表、参考文献、AI 使用及贡献声明；不加独立封面或附录；注明 Option、所有姓名及学号；图表编号并可由 notebook 重新生成。

本模板使用 A4、11pt、20 mm 页边距及单栏。这些是可读的默认设置，任务书没有规定具体数值，也没有明确规定最终提交语言。英文、中文 PDF 是备选版本，最终选交其中一份。

完整课程提交还需要可在全新 Colab/Kaggle 运行的 notebook 和不超过 3 分钟的演示视频。当前工作流负责编译报告；实验训练和数据派生图表由你的 notebook 完成。

## 项目中的输出

构建结果位于 `dist/aip304-cw2/`；临时文件和失败日志位于 `build/aip304-cw2/`。这两处已加入 `.gitignore`。Starter ZIP 中的双语预览便于直接查看，首次 Git 提交只包含源码。
