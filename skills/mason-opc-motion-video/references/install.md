# 安装与环境

## 完整安装（推荐）

```sh
git clone https://github.com/masonmosen/mason-opc-motion-video.git
cd mason-opc-motion-video
python3 install.py --verify-only
python3 install.py --dest ~/.agents/skills --host codex
```

Windows 使用 `py` 或 `python`，把目标换成本机技能目录。Hermes 用 `--host hermes`，Claude Code 用 `--host claude`；它们建立同源发现入口。其他可读写文件、运行命令的 Agent 用 `--host generic` 并按宿主文档接入。不能只复制 SKILL.md。

本仓库包含完整公开阿杜依赖：1,031 个文件、竖屏 11 风格 / 54 组、横屏 10 风格 / 47 组。所有字体与第三方许可随包保留。个人 `.motion` 不在此整库范围，按 motion-packages.md 使用自己的账号另取。

## 已通过 npx 装入技能

```sh
npx -y skills add masonmosen/mason-opc-motion-video --skill mason-opc-motion-video -a codex -g -y
python3 ~/.agents/skills/mason-opc-motion-video/scripts/bootstrap.py --dest ~/.agents/skills --host codex
```

第一条只安装技能，第二条从公开仓库取得完整包、核对文件并完成依赖。不要把技能被发现当作运行环境已就绪。bootstrap 不删除已有技能，不覆盖个人改文；有冲突时保留并对比版本。`--host hermes|claude|generic` 和 `--adu-root` / `--ffmpeg-bin` / `--state-dir` 传给完整安装器。

## 系统工具与边界

- Python 3.12+（本机实测 3.14），Node 18+（实测 22）与 npm。
- FFmpeg 9+ / ffprobe，含 libx264、colorspace 和显式色域转换；独立部署可用 `--ffmpeg-bin` 指定，不替换全局默认。
- Chrome / Chromium；独立本地无登录渲染实例。
- 安装器复用符合固定快照的阿杜环境，或调用阿杜官方 setup 创建独立 venv 并安装 requirements-runtime.txt / npm 锁定依赖。缺少操作系统工具时，Agent 按目标系统官方渠道补齐后重跑，不虚报完整安装。
- 配置在 `~/.local/share/mason-opc-motion-video/runtime.json`，不写进技能或仓库。自定义 `--state-dir` 后设置 `MASON_MOTION_CONFIG` 指向对应 runtime.json。
- `--source-only` 明确表示离线源收件、运行未验收。其他系统和 Agent 须独立试片验证。

## 第一轮验证

1. 完整安装器和 `scripts/motion.py doctor` 通过。
2. 刷新宿主或新建对话，确认技能被发现；列出 portrait / landscape 模板。
3. 先跑 [公开技术样例](../assets/demo-episode.json) 的生成器，见仓库 README；该样例是合成占位人像与提示音，不含真人或配音，只验证工程、音画和导出。
4. 再用自己的无字口播：重新量 headBox、绑定输入 SHA、对齐真实字幕与语义时钟，输出新工程、MP4、QA 和 STATUS。只有真实片经过连续看听与用户评价才算内容验收。
