# 🔓 Auto Deobfuscator

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Automatically decode multiple layers of Python obfuscation**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Examples](#-examples) • [Contact](#-contact)

</div>

---

## 📋 Description

Auto Deobfuscator is a powerful Python tool that automatically detects and decodes multiple layers of obfuscation in Python files. It supports various encoding and compression schemes and iteratively processes files until clean, readable Python code is obtained.

## ✨ Features

- 🔄 **Multi-layer Detection** - Automatically detects and processes multiple obfuscation layers
- 🎯 **Smart Analysis** - Identifies when code is fully deobfuscated
- 🔧 **Multiple Formats Supported**:
  - Marshal (Python bytecode)
  - Base64, Base32, Base85 encoding
  - Zlib, Gzip, Bz2 compression
  - Hexadecimal encoding
  - ROT13 encoding
  - exec() and eval() extraction
- 🔄 **Auto-Update** - Built-in version control with GitHub integration
- 🎨 **Colorful Output** - Beautiful terminal interface with progress tracking
- 📝 **Auto Documentation** - Adds header comments with deobfuscation details
- ⚡ **Fast Processing** - Efficient iterative deobfuscation

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/anbuinfosec/mardec.git
cd mardec
```

### Install Dependencies

```bash
pip3 install -r requirements.txt
```

Or install manually:

```bash
pip3 install requests
```

## 💻 Usage

### Basic Usage

```bash
python3 main.py <input_file> [output_file]
```

### Examples

```bash
# Deobfuscate a file (output to default file)
python3 main.py obfuscated.py

# Deobfuscate with custom output filename
python3 main.py obfuscated.py clean_code.py

# Skip update check
python3 main.py obfuscated.py clean_code.py --no-update
```

### Command Line Options

| Flag | Description |
|------|-------------|
| `--no-update` or `-n` | Skip automatic update check |

## 📊 Example Output

```
[i] Auto Deobfuscator v1.0.0
[i] Checking for updates...
[i] Already on latest version (1.0.0)
[i] Reading file: ofc.py

[i] Starting automatic deobfuscation...
[i] Input size: 13530 bytes
[+] Layer 1: Decoded using exec_extraction → 4478 bytes
[+] Layer 2: Decoded using marshal → 4258 bytes
[+] Layer 3: Decoded using zlib → 10645 bytes

[i] === Iteration 2 ===
[i] Starting automatic deobfuscation...
[+] Layer 1: Decoded using exec_extraction → 10036 bytes
[+] Layer 2: Decoded using base64 → 7525 bytes
[+] Clean Python code detected!

[+] ============================================================
[+] Deobfuscation complete!
[+] Total iterations: 2
[+] Total layers decoded: 7
[+] Output file: clean_code.py
[+] Output size: 7516 bytes
[+] ============================================================
```

## 🛠️ How It Works

1. **Detection Phase**: Scans the input file to identify obfuscation patterns
2. **Extraction Phase**: Extracts obfuscated data from exec(), eval(), or direct encoding
3. **Decoding Phase**: Attempts multiple decoding methods (base64, marshal, zlib, etc.)
4. **Iteration Phase**: Repeats the process on decoded output until clean code is found
5. **Output Phase**: Saves deobfuscated code with documentation header

## 📁 Project Structure

```
mardec/
├── main.py    # Main deobfuscation tool
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── .gitignore              # Git ignore patterns
└── VERSION                 # Version file for auto-update
```

## 🔄 Auto-Update Feature

The tool automatically checks for updates from GitHub on startup. To disable this:

```bash
python3 main.py file.py --no-update
```

## ⚠️ Limitations

- Maximum 10 iterations to prevent infinite loops
- Requires Python 3.7 or higher
- Some advanced obfuscation techniques may not be supported
- Internet connection required for auto-update feature

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

<div align="center">

**@anbuinfosec**

[![Facebook](https://img.shields.io/badge/Facebook-%231877F2.svg?style=for-the-badge&logo=Facebook&logoColor=white)](https://facebook.com/anbuinfosec)
[![GitHub](https://img.shields.io/badge/GitHub-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/anbuinfosec)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/anbuinfosec_official)
[![YouTube](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white)](https://youtube.com/@anbuinfosec)

</div>

---

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

## 📝 Changelog

### Version 1.0.0
- Initial release
- Multi-layer deobfuscation support
- Auto-update feature
- Colorful terminal output
- Support for marshal, base64, zlib, and more

---

<div align="center">

Made with ❤️ by [@anbuinfosec](https://github.com/anbuinfosec)

**[⬆ Back to Top](#-mardec)**

</div>
