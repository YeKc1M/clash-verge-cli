# Clash Verge CLI Project

## Build Binary

To build the standalone binary, run:

```bash
./build.sh
```

Or manually:
```bash
cd clash-verge-rev/agent-harness
source venv/bin/activate
pyinstaller clash-verge-cli.spec
./dist/clash-verge-cli version
```

## Quick Commands

- `/build` - Build the binary using `./build.sh`
