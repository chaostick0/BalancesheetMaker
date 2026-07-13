# BalanceSheetMaker

BalanceSheetMaker is a simple and efficient application for generating balance sheets from financial data. It helps users organize assets, liabilities, income, and expenses into a structured balance sheet with minimal effort.

## Features

- Generate balance sheets automatically
- Manage Assets and Liabilities
- Record Income and Expenses
- Export reports
- User-friendly interface
- Fast and lightweight
- Easy to customize

## Project Structure

```
BalanceSheetMaker/
├── src/                # Source code
├── assets/             # Images, icons, and static files
├── data/               # Sample or generated data
├── exports/            # Generated balance sheets
├── docs/               # Documentation
├── package.json
├── README.md
└── ...
```

## Requirements

Depending on the technology stack:

### Node.js

- Node.js 18+
- npm or yarn

### Python (if applicable)

- Python 3.10+
- pip

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/BalanceSheetMaker.git
```

Move into the project directory:

```bash
cd BalanceSheetMaker
```

Install dependencies:

```bash
npm install
```

or

```bash
yarn install
```

## Running the Application

Start the development server:

```bash
npm start
```

or

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Usage

1. Open the application.
2. Enter financial information.
3. Add:
   - Assets
   - Liabilities
   - Income
   - Expenses
4. Review the generated balance sheet.
5. Export or save the report.

## Example Balance Sheet

| Assets | Amount |
|---------|-------:|
| Cash | ₹150,000 |
| Inventory | ₹75,000 |
| Equipment | ₹250,000 |
| **Total Assets** | **₹475,000** |

| Liabilities | Amount |
|-------------|-------:|
| Loans | ₹180,000 |
| Accounts Payable | ₹45,000 |
| **Total Liabilities** | **₹225,000** |

| Equity | Amount |
|---------|-------:|
| Owner's Equity | ₹250,000 |

**Accounting Equation**

```
Assets = Liabilities + Equity
₹475,000 = ₹225,000 + ₹250,000
```

## Configuration

Any configurable values should be stored in:

- `.env`
- `config.json`
- Application settings

Example:

```env
APP_PORT=3000
EXPORT_DIRECTORY=exports
DEFAULT_CURRENCY=INR
```

## Technologies Used

- JavaScript / TypeScript
- Node.js
- HTML/CSS
- Express (if applicable)
- React (if applicable)
- SQLite / MySQL / PostgreSQL (if applicable)

## Future Improvements

- PDF Export
- Excel Export
- Multi-user support
- Authentication
- Dashboard with charts
- Financial analytics
- GST support
- Multi-company management

## Contributing

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/your-feature
```

3. Commit your changes.

```bash
git commit -m "Add new feature"
```

4. Push the branch.

```bash
git push origin feature/your-feature
```

5. Open a Pull Request.

## License

This project is licensed under the MIT License.

## Author

**Prantik**

---

If you find this project useful, consider giving it a ⭐ on GitHub.