# 🍳 Khamseena Programming Language

**Khamseena** is a toy programming language and compiler front-end (Scanner → Parser → Semantic Analyzer) built as an academic project, with a cooking-themed syntax — variables are "measured," functions are "recipes," and output is "served." It includes a full lexer, a recursive-descent parser, a scope-aware semantic analyzer, a Tkinter GUI IDE, a CLI, and unit tests.

---

## ✨ Features

- 🔤 **Lexical analysis** — tokenizes keywords, identifiers, numbers, strings (with escape sequences), operators, delimiters, and comments, with full line/column tracking
- 🌳 **Recursive-descent parser** — builds an Abstract Syntax Tree (AST) from tokens, with dedicated error messages for missing parentheses, braces, and semicolons
- ✅ **Semantic analysis** — scope-aware symbol table (global/function/block scopes), type checking (`INTEGER`, `FLOAT`, `STRING`, `BOOLEAN`), undefined variable/function detection, redeclaration checks, and implicit `INTEGER → FLOAT` conversion
- 🖥️ **GUI IDE** (`gui_main.py`) — a Tkinter-based code editor with line numbers, one-click "Analyze" pipeline (Scanner → Parser → Semantic Analyzer), tabbed output (Tokens / AST / Semantic Analysis / Complete Output), and file open/save
- ⌨️ **CLI tools** — scan a file and dump its tokens (`token_main.py`), or run the full parse + semantic pipeline on a file (`parser_main.py`)
- 🧪 **Unit tests** — scanner tests (`test_scanner.py`) and parser tests (`test_parser.py`)
- 📄 Sample `.kh` programs demonstrating valid code and common syntax/semantic errors

---

## 📁 Project Structure

```
khamseena/
├── khamseena_token.py     # Token, TokenType, and KEYWORDS mapping
├── scanner.py              # Lexer: turns source code into a token stream
├── ast_nodes.py             # AST node classes (Program, FunctionDef, IfStatement, etc.)
├── khamseena_parser.py       # Recursive-descent Parser + print_ast() utility
├── semantic_analyzer.py       # SymbolTable + SemanticAnalyzer (scope & type checking)
├── gui_main.py               # Tkinter GUI IDE (editor + Scanner/Parser/Semantic tabs)
├── token_main.py             # CLI: scan a .kh file and print/save its tokens
├── parser_main.py            # CLI: run scan → parse → semantic analysis on a .kh file
├── test_scanner.py           # Unit tests for the scanner (unittest)
├── test_parser.py            # Basic tests for the parser
├── tokens.txt                # Example token-dump output
├── test.kh                   # Valid sample program (types, functions, scopes, loops)
├── syntax_errors.kh          # Sample file with intentional syntax errors
├── semantic_errors.kh        # Sample file with intentional semantic errors
├── missing_semicolons.kh     # Sample file demonstrating missing-semicolon errors
├── __init__.py
└── README.md
```

---

## 🧠 Language Overview

Khamseena uses a "cooking" vocabulary mapped onto familiar programming constructs:

| Keyword | Meaning | Keyword | Meaning |
|---|---|---|---|
| `fetch` | include/import | `taste` | if |
| `brew` | main | `retaste` | else |
| `recipe` | function | `stir` | while |
| `count` | int | `mix` | for |
| `measure` | float | `stop` | break |
| `note` | string | `skip` | continue |
| `flavor` | bool | `deliver` | return |
| `sweet` / `sour` | true / false | `serve` / `pour` | print / input |

**Operators:** `+ - * / %` (arithmetic), `= == != > < >= <=` (assignment/comparison), `&& \|\| !` (logical)
**Delimiters:** `( ) { } ; ,`
**Comments:** start with `#` and run to end of line

### Example program (`test.kh`)
```
fetch basics;

count x = 42;
measure y = 3.14;
note msg = "Hello Khamseena";
flavor flag = sweet;

recipe calculateSum(count a, count b) {
    count result = a + b;
    deliver result;
}

recipe main() {
    count num = 100;
    measure pi = 3.14159;
    measure result = num + pi;          # valid: INTEGER -> FLOAT
    flavor isValid = num > 50 && pi < 4.0;

    count i = 0;
    stir (i < 5) {
        serve i;
        i = i + 1;
    }

    deliver 0;
}
```

The repo also ships with `syntax_errors.kh`, `missing_semicolons.kh`, and `semantic_errors.kh` — handy for testing the analyzer's error reporting (undefined variables, type mismatches, redeclarations, missing parens/braces/semicolons, etc.).

---

## 🔧 The Compiler Pipeline

1. **Scanner** (`scanner.py`) — reads raw source text and produces a list of `Token` objects (type, value, line, column). Raises `LexicalError` on invalid characters or unterminated strings.
2. **Parser** (`khamseena_parser.py`) — a recursive-descent parser that consumes the token stream and builds an AST out of the node classes defined in `ast_nodes.py` (e.g., `Program`, `FunctionDef`, `VarDeclaration`, `IfStatement`, `WhileStatement`, `BinaryOp`). Raises `ParseError` with line info on malformed syntax.
3. **Semantic Analyzer** (`semantic_analyzer.py`) — walks the AST using the visitor pattern, maintaining a `SymbolTable` per scope (global, function, block). Checks for undefined variables/functions, redeclarations, type mismatches in declarations/assignments, and reports warnings (e.g., non-boolean loop/if conditions) without failing the build.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+ (Tkinter is included with most standard Python installs; on Linux you may need `sudo apt install python3-tk`)
- No external pip packages are required — the project uses only the standard library

### 2. Project layout
Keep all `.py` files in the same folder (or a `modules/`-style package) since they import from each other directly (e.g., `from scanner import Scanner`).

### 3. Run the GUI IDE
```bash
python gui_main.py
```
This opens a code editor pre-loaded with a sample program. Click **▶ Analyze (F5)** to run the full Scanner → Parser → Semantic Analyzer pipeline and inspect results across the **Tokens**, **AST**, **Semantic Analysis**, and **Complete Output** tabs. Use **File → Open/Save** to work with `.kh` files.

### 4. Run the scanner from the command line
```bash
python token_main.py test.kh
python token_main.py test.kh tokens_output.txt   # optionally save token dump to a file
```

### 5. Run the full parser + semantic pipeline from the command line
```bash
python parser_main.py test.kh
```
Or run the parser's built-in example tests:
```bash
python parser_main.py test
```

### 6. Run the unit tests
```bash
python test_scanner.py
python test_parser.py
```

---

## 🖼️ Sample Token Output

Running the scanner on a short `fetch/recipe/serve/deliver` program produces output like (`tokens.txt`):
```
TOKEN TYPE           VALUE                POSITION
----------------------------------------------------------------------
INCLUDE              fetch                1:1
IDENTIFIER           basics               1:7
FUNCTION              recipe               3:1
IDENTIFIER            main                 3:8
...
```

---

## 📌 Notes & Possible Improvements

- `test_scanner.py`'s `test_conditional_statement` uses a `refill` block that isn't a recognized keyword (the language uses `retaste` for `else`) — worth double-checking that test's intent.
- `ast_nodes.py`'s `VarDeclaration.__str__` and `semantic_analyzer.py`'s `type_map` both hardcode the same `count/measure/note/flavor → INTEGER/FLOAT/STRING/BOOLEAN` mapping in two places; centralizing it (e.g., in `khamseena_token.py`) would avoid drift if the type system changes.
- The parser doesn't yet appear to handle `mix` (for-loops), `stop` (break), or `skip` (continue) in the AST node list, even though they're defined as keywords — these could be natural next additions.
- Consider adding a `requirements.txt` (even if empty/standard-library-only) and a `LICENSE` file for completeness.
