# AIP304 CW2：自动生成中英文 PDF

这是独立项目 **AIP304CW2** 的 XeLaTeX 报告目录。项目参考此前 CPT204 报告的自动构建方式，英文与中文分别生成 PDF，两种版本都允许中英混排。

工作流使用 GitHub 托管的 `ubuntu-24.04` runner，无需部署自托管服务器，也不需要配置额外 Secrets。它负责编译、检查和上传报告；AIP304 的 Python / PyTorch 实验、模型训练和 notebook 复现仍由你的课程项目完成。

**初始内容是有明确占位提示的报告模板，不是已经完成的实验报告。** 没有预填真实实验指标、学生身份或未经确认的贡献声明。

## 1. 课程要求与模板默认设置

依据所提供《AIP304 CW2 Task Sheet》第 7 页 §6.2–6.5：

| 项目 | 课程要求 | 本实现的处理 |
| --- | --- | --- |
| 报告数量 | 最终提交一份 PDF | `en` 和 `zh` 是备选版本，最终选用其中一份 |
| 页数 | 总计最多 5 页 | 每份 PDF 独立计数，超过 5 页则构建失败 |
| 计数范围 | 图、表、参考文献、AI 披露和贡献声明全部计入 | 检查完整 PDF，不排除任何页面 |
| 封面和附录 | 不得另加封面或附录 | 标题和作者直接放在第一页正文上方；不提供独立封面、目录页或附录 |
| 身份和方案 | 所有成员姓名、学号，以及 Option 1 / Option 2 | 在 `report.json` 集中填写 |
| 图表 | 编号、有用的 caption、清楚的标签；相关时提供样本数 | 提供 LaTeX 图表和交叉引用示例 |
| 实验可复现性 | notebook 能重新生成每个数据派生图及结果表 | 从 notebook 导出到 `generated/`，再引用进报告 |
| AI 披露 | 工具名称、可得的版本、辅助任务及核验方法 | 英文和中文分别填写 `ai_disclosure` |
| 团队贡献 | 说明每名成员的实施、实验、分析、写作及演示工作 | 英文和中文分别填写 `contributions` |

**A4、11pt、20 mm 边距、单栏是本模板的排版选择，不是任务书指定的数值。** 任务书要求排版可读，没有指定具体字体、字号、边距、行距或引用样式。模板采用 Latin Modern 西文字体和 Noto CJK 中文字体。

任务书也没有明确规定最终报告的提交语言。本实现提供中文与英文排版能力，不代表课程已经许可中文提交。两份译本不要合并成一份超过五页的报告，也不要把它们当作要求提交的两份报告。

完整课程提交还包括一个可在全新 Colab / Kaggle 环境运行的 `.ipynb`，以及不超过 3 分钟、讲述时露脸的演示视频；PDF runner 不代替这些交付项。

## 2. 修改哪几个文件

| 文件 | 用途 |
| --- | --- |
| `report/report.json` | 选择方案、报告标题、成员姓名和学号、AI 使用及贡献声明 |
| `report/content/en.tex` | 英文正文 |
| `report/content/zh.tex` | 中文正文 |
| `report/references.bib` | BibTeX 参考文献 |
| `report/main.tex` | 两种语言共用的版式 |
| `report/generated/` | notebook 导出的图和结果表 |
| `scripts/build_aip304_report.py` | 本地与 CI 共用的构建和检查入口 |
| `.github/workflows/aip304-cw2-pdf.yml` | GitHub Actions 自动化 |

先编辑 `report.json`：

- `option` 只能为 `1` 或 `2`，选择你实际完成的方案。正文会显示对应的写作提示。
- `title.en` / `title.zh` 分别设置英文、中文标题。
- `authors` 填写 1–3 名成员，每名成员包含 `name` 和 `id`。不要沿用 CPT204 的成员信息。
- `ai_disclosure.en` / `.zh` 如实写明工具、版本（如可得）、辅助任务及你实际进行的核验。
- `contributions.en` / `.zh` 如实说明成员在实现、实验、分析、写作和演示上的工作。

JSON 字段是普通文字，由脚本进行 LaTeX 转义；不要在这些字段中填写 LaTeX 排版命令。LaTeX 命令写在正文 `.tex` 中。

随后把正文中的 `\todo{...}` 和占位图、占位表替换为真实内容。正文模板围绕任务书推荐的结构组织：问题与动机、相关工作、数据与协议、方法、实验与结果、解释与局限性。参考文献、AI 披露和贡献声明由共用模板排列在文末。Option 2 还提示现行文献、最接近的方法、假设、匹配基线、消融以及重复实验要求。

改变语言选择不会自动翻译正文。需要双语版本时，请维护两份内容，并确保结果与引用一致。

## 3. 在 GitHub 生成和下载

自动触发：

1. 在项目任一分支修改模板目录、构建脚本或新工作流并 push；或者提交包含这些改动的 pull request。
2. 打开仓库 **Actions → AIP304 CW2 PDF**，查看该次运行。
3. 默认以 `all` + `preview` 构建英文和中文两份模板预览。
4. 成功后，在运行页面的 **Artifacts** 下载 `aip304-cw2-all-preview-运行编号`。

手动生成：

1. 工作流合入默认分支 `main` 后，打开 **Actions → AIP304 CW2 PDF → Run workflow**。
2. `language` 选 `en`、`zh` 或 `all`。
3. `mode` 选 `preview` 或 `submission`。
4. 执行并从该次运行的 **Artifacts** 下载。

GitHub 要求带 `workflow_dispatch` 的工作流存在于默认分支，才提供正常的手动运行入口；新分支上的首次验证可以通过 push / pull request 事件完成。参见 [GitHub 官方手动运行说明](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)。

| 模式 | 适用阶段 | 检查方式 |
| --- | --- | --- |
| `preview` | 搭建版式和逐步写作 | 允许明显标记的待填内容，PDF 显示预览提示；仍要求最多 5 页、字体和引用正常 |
| `submission` | 完成正文后的提交前检查 | 额外拒绝未填身份、声明和正文占位；清除预览标识 |

提交前建议只选择实际要提交的语言。例如只完成英文正文时，选择 `en` + `submission`；不要让尚未完成的中文备选版阻断英文检查。

输出文件为：

```text
dist/aip304-cw2/AIP304-CW2-en-preview.pdf
dist/aip304-cw2/AIP304-CW2-zh-preview.pdf
dist/aip304-cw2/manifest.json
```

选择 `submission` 后，文件名中的 `preview` 相应变为 `submission`。`manifest.json` 记录语言、模式、页数及构建来源等信息，便于确认下载的是哪一版。成功产物保留 30 天，建议及时下载。每次构建结果均可在对应 Actions 运行中下载。

## 4. 在本地运行同一套构建

Ubuntu / Debian 安装依赖：

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  latexmk texlive-xetex texlive-lang-chinese \
  texlive-latex-extra texlive-fonts-recommended \
  fonts-lmodern fonts-noto-cjk fontconfig poppler-utils python3
```

在**仓库根目录**运行：

```bash
# 两种语言的预览
python3 scripts/build_aip304_report.py --language all --mode preview

# 英文最终检查
python3 scripts/build_aip304_report.py --language en --mode submission

# 中文最终检查
python3 scripts/build_aip304_report.py --language zh --mode submission
```

脚本通过 XeLaTeX 和 BibTeX 处理 Unicode、参考文献与交叉引用，并禁止 shell escape。中文排版使用 [xeCJK](https://ctan.org/pkg/xecjk)。若使用其他操作系统，需要先安装等效的 TeX Live / MacTeX、Noto CJK 与 Latin Modern 字体，以及包含 `pdfinfo`、`pdffonts`、`pdftotext` 的 Poppler 工具。

## 5. 接入 notebook 生成的真实图表

把 notebook 生成的图导出到 `report/generated/`，例如 `confusion-matrix.png`。在需要的语言正文中用常规 LaTeX 引用：

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.85\linewidth]{generated/confusion-matrix.png}
  \caption{Test confusion matrix. Rows are true classes; columns are predictions.}
  \label{fig:confusion}
\end{figure}
```

结果表也应由 notebook 导出；可以用 `\input{generated/results.tex}` 引入。图表中的类别、计数、单位和色标应清楚可读，caption 应说明评估分区、样本数及需要的实验条件。占位框和 `--` 表格值不代表实验结果，最终报告必须替换。

保持完整的图和各类指标在 notebook 中，报告只选择对结论最有帮助的图表。不要为凑页数把文字或图缩到难以阅读。

## 6. 构建失败时怎么处理

| 错误 | 处理 |
| --- | --- |
| 超过 5 页 | 压缩重复叙述，选择更有信息量的图表；检查参考文献和声明占用的页数，不增加附录 |
| `submission` 存在占位内容 | 填完元数据和正文，删除 `\todo{...}`，替换图表占位框；写作中继续使用 `preview` |
| 字体或中文缺字 | 确认安装 `fonts-noto-cjk`、`fonts-lmodern` 和 `texlive-lang-chinese`；避免字体不支持的特殊符号 |
| 未定义 citation / reference | 核对 `references.bib` 的引用键、`\label` 与 `\ref`，不要忽略编译警告 |
| 缺少图片或结果表 | 确认 notebook 已导出，路径和大小写匹配，且文件已提交到分支 |

失败时工作流上传 `aip304-cw2-diagnostics-...` 日志产物（保留 7 天），失败的 PDF 不会作为通过检查的报告上传。可以在 Actions 日志及 `build/aip304-cw2/` 中查看具体原因。

**构建成功表示技术检查通过，不等于课程内容已经达标。** 提交前仍需人工核对真实实验、引用质量、Option 对应要求、图表是否能由 notebook 重建、AI 披露与贡献声明是否准确，以及 notebook 和视频是否完整。
