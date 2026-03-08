# CloudVault Test Automation Framework

A PyTest-based automated test framework simulating validation of a
distributed cloud file system — modeled after real-world SDET practices
in distributed storage environments.

## Project Structure
```
cloudvault-test-framework/
├── services/          # Simulated distributed system components
├── tests/             # PyTest test suites (53 tests)
├── utils/             # Log analyzer and report generator
├── logs/              # Auto-generated test logs
├── reports/           # Auto-generated HTML + JSON reports
└── .github/workflows/ # CI/CD pipeline via GitHub Actions
```

## Tech Stack
- **Language**: Python 3.11
- **Framework**: PyTest
- **CI/CD**: GitHub Actions
- **Environment**: Linux (Ubuntu/WSL)
- **Version Control**: Git

## Test Suites

| Suite | Tests | Coverage |
|---|---|---|
| test_file_upload.py | 12 | Cloud node upload behaviors |
| test_file_sync.py | 14 | Edge-to-cloud sync behaviors |
| test_integration.py | 14 | End-to-end distributed system |
| test_regression.py | 13 | Regression guards |
| **Total** | **53** | **Full system coverage** |

## Setup & Run
```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/cloudvault-test-framework.git
cd cloudvault-test-framework

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific suite
pytest tests/test_integration.py -v

# Generate reports
python3 -c "
from utils.report_generator import ReportGenerator
r = ReportGenerator()
r.generate_json_report()
r.generate_text_report()
"
```

## Key Features
- **Distributed system simulation** across cloud, edge, and storage layers
- **Failure scenario testing** — node offline, sync failures, recovery
- **Parameterized tests** for multiple file types and sizes
- **Automated log analysis** with failure pattern detection
- **HTML + JSON test reports** auto-generated after every run
- **CI/CD integration** via GitHub Actions on every push