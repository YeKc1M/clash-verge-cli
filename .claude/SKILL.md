# Build Binary Skill

## Name
build

## Description
Build the clash-verge-cli binary with PyInstaller

## Usage
/build

## Implementation
1. Activate virtual environment: `source venv/bin/activate`
2. Run PyInstaller: `pyinstaller clash-verge-cli.spec`
3. Verify binary at `dist/clash-verge-cli`
4. Test with: `./dist/clash-verge-cli version`

## Working Directory
/home/dev/repos/clash-verge-cli/clash-verge-rev/agent-harness
