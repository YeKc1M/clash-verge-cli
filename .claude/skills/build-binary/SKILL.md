---
name: build-binary
description: Build the clash-verge-cli standalone binary using PyInstaller. Use this skill when the user wants to build, compile, or package the binary, create a distributable executable, or prepare a release build.
---

# Build Binary Skill

This skill helps build the standalone binary for clash-verge-cli using PyInstaller.

## Quick Build

Run the build script from the agent-harness directory:

```bash
cd clash-verge-rev/agent-harness
./build.sh
```

## Manual Build Steps

If the script fails or you need more control:

```bash
cd clash-verge-rev/agent-harness
source venv/bin/activate
pyinstaller clash-verge-cli.spec
```

## Verify Build

Check the binary was created successfully:

```bash
./clash-verge-cli version
```

## Troubleshooting

### Virtual environment not found

```bash
cd clash-verge-rev/agent-harness
python -m venv venv
source venv/bin/activate
pip install -e .
pip install pyinstaller
```

### Spec file issues

The spec file is at `clash-verge-rev/agent-harness/clash-verge-cli.spec`. If build fails, check:
1. All dependencies are installed
2. The entry point path is correct
3. Data files are properly included

## Output Location

The built binary will be at:
- `./clash-verge-cli` (project root)

## What to Do

When the user asks to build the binary:
1. Navigate to `clash-verge-rev/agent-harness/`
2. Run `./build.sh`
3. If it fails, use manual build steps
4. Verify the binary works with `version` command
5. Report the path to the built binary
