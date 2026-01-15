# hook-test

Test git hooks locally without committing by simulating hook environments with sample data

## Features

- Execute any git hook script (pre-commit, pre-push, commit-msg, etc.) in simulated environment
- Provide sample staged files for pre-commit hook testing with configurable file lists
- Mock git environment variables (GIT_DIR, GIT_INDEX_FILE, etc.) accurately
- Support commit-msg hook testing with sample commit messages
- Display hook output (stdout/stderr) with clear formatting
- Show hook exit codes and interpret success/failure
- Support custom sample data via command-line arguments or config files
- Validate hook scripts exist and are executable before running
- Provide verbose mode for debugging hook execution
- Support testing hooks from custom .git/hooks directory or standalone scripts

## How to Use

Use this project when you need to:

- Quickly solve problems related to hook-test
- Integrate python functionality into your workflow
- Learn how python handles common patterns with click

## Installation

```bash
# Clone the repository
git clone https://github.com/KurtWeston/hook-test.git
cd hook-test

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Built With

- python using click

## Dependencies

- `click>=8.0.0`
- `pytest>=7.0.0`
- `pytest-cov>=4.0.0`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
