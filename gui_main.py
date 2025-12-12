"""
Khamseena Programming Language - GUI Compiler Interface
Complete GUI for Scanner, Parser, and Semantic Analysis
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from scanner import Scanner, LexicalError
from khamseena_parser import Parser, ParseError, print_ast
from semantic_analyzer import SemanticAnalyzer
import io
import sys
import os


class KhamseenaIDE:
    """GUI IDE for Khamseena Programming Language"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Khamseena Programming Language - Compiler IDE")
        self.root.geometry("1400x900")
        
        # Current file path
        self.current_file = None
        
        # Color scheme
        self.bg_color = "#2b2b2b"
        self.fg_color = "#d4d4d4"
        self.accent_color = "#007acc"
        
        # Create GUI
        self.create_menu()
        self.create_widgets()
        self.load_sample_code()
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Analyze", command=self.analyze, accelerator="F5")
        run_menu.add_command(label="Clear Output", command=self.clear_outputs, accelerator="Ctrl+K")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<F5>", lambda e: self.analyze())
        self.root.bind("<Control-k>", lambda e: self.clear_outputs())
    
    def create_widgets(self):
        """Create main GUI widgets"""
        # Main container with PanedWindow for resizable sections
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ========== TOP SECTION: Code Editor ==========
        editor_frame = ttk.LabelFrame(main_paned, text="Source Code Editor", padding=5)
        main_paned.add(editor_frame, weight=1)
        
        # Line numbers frame
        line_frame = ttk.Frame(editor_frame)
        line_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.line_numbers = tk.Text(
            line_frame,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background="#1e1e1e",
            foreground="#858585",
            state="disabled",
            font=("Consolas", 11)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Code editor
        editor_scroll_frame = ttk.Frame(editor_frame)
        editor_scroll_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.code_text = scrolledtext.ScrolledText(
            editor_scroll_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            selectbackground="#264f78",
            undo=True,
            maxundo=-1
        )
        self.code_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind events for line numbers
        self.code_text.bind("<KeyRelease>", self.update_line_numbers)
        self.code_text.bind("<MouseWheel>", self.update_line_numbers)
        self.code_text.bind("<Button-1>", self.update_line_numbers)
        
        # ========== CONTROL BUTTONS ==========
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Style for buttons
        style = ttk.Style()
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"))
        
        ttk.Button(
            btn_frame,
            text="▶ Analyze (F5)",
            command=self.analyze,
            style="Action.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="🗑️ Clear Output",
            command=self.clear_outputs
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="📂 Open File",
            command=self.open_file
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="💾 Save",
            command=self.save_file
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="📝 New",
            command=self.new_file
        ).pack(side=tk.LEFT, padx=5)
        
        # ========== BOTTOM SECTION: Output Tabs ==========
        output_frame = ttk.Frame(main_paned)
        main_paned.add(output_frame, weight=1)
        
        self.notebook = ttk.Notebook(output_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Tokens (Scanner Output)
        self.tokens_text = self.create_output_tab("📋 Tokens (Scanner)")
        
        # Tab 2: AST (Parser Output)
        self.ast_text = self.create_output_tab("🌳 AST (Parser)")
        
        # Tab 3: Semantic Analysis
        self.semantic_text = self.create_output_tab("✅ Semantic Analysis")
        
        # Tab 4: Complete Output
        self.all_output_text = self.create_output_tab("📊 Complete Output")
        
        # ========== STATUS BAR ==========
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.file_label = ttk.Label(
            status_frame,
            text="Untitled",
            relief=tk.SUNKEN,
            anchor=tk.E
        )
        self.file_label.pack(side=tk.RIGHT)
    
    def create_output_tab(self, title):
        """Create a scrolled text widget in a new tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        
        text_widget = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white"
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        return text_widget
    
    def update_line_numbers(self, event=None):
        """Update line numbers in the editor"""
        line_numbers_text = ""
        line_count = int(self.code_text.index('end-1c').split('.')[0])
        
        for i in range(1, line_count + 1):
            line_numbers_text += f"{i}\n"
        
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.config(state="disabled")
    
    def load_sample_code(self):
        """Load sample Khamseena code"""
        sample_code = """fetch basics;

# Simple Khamseena Program
recipe main() {
    count age = 25;
    measure pi = 3.14;
    note message = "Hello, Khamseena!";
    flavor isValid = sweet;
    
    serve "Age: ";
    serve age;
    
    taste (age >= 18) {
        serve "Adult";
    } retaste {
        serve "Minor";
    }
    
    count i = 0;
    stir (i < 5) {
        serve i;
        i = i + 1;
    }
    
    deliver 0;
}"""
        self.code_text.insert("1.0", sample_code)
        self.update_line_numbers()
    
    def analyze(self):
        """Run the complete compiler pipeline"""
        self.clear_outputs()
        code = self.code_text.get("1.0", tk.END)
        
        if not code.strip():
            messagebox.showwarning("Warning", "Please enter some code first!")
            return
        
        try:
            all_output = []
            
            # ========== STEP 1: SCANNER ==========
            self.status_var.set("🔍 Scanning...")
            self.root.update()
            
            scanner = Scanner(code)
            tokens = scanner.tokenize()
            
            # Capture token output
            token_output = self.capture_output(lambda: scanner.print_tokens())
            self.tokens_text.insert("1.0", token_output)
            all_output.append("="*70 + "\n1. SCANNER OUTPUT\n" + "="*70 + "\n" + token_output)
            
            # ========== STEP 2: PARSER ==========
            self.status_var.set("📝 Parsing...")
            self.root.update()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Capture AST output
            ast_output = self.capture_output(lambda: print_ast(ast))
            ast_display = "Abstract Syntax Tree:\n" + "="*50 + "\n" + ast_output
            self.ast_text.insert("1.0", ast_display)
            all_output.append("\n" + "="*70 + "\n2. PARSER OUTPUT (AST)\n" + "="*70 + "\n" + ast_output)
            
            # ========== STEP 3: SEMANTIC ANALYZER ==========
            self.status_var.set("🔬 Analyzing semantics...")
            self.root.update()
            
            analyzer = SemanticAnalyzer()
            semantic_output = self.capture_output(lambda: analyzer.analyze(ast))
            self.semantic_text.insert("1.0", semantic_output)
            all_output.append("\n" + "="*70 + "\n3. SEMANTIC ANALYSIS\n" + "="*70 + "\n" + semantic_output)
            
            # ========== COMPLETE OUTPUT ==========
            complete_output = "\n".join(all_output)
            self.all_output_text.insert("1.0", complete_output)
            
            # ========== RESULTS ==========
            if analyzer.errors:
                self.status_var.set(f"❌ Compilation failed with {len(analyzer.errors)} error(s)")
                messagebox.showerror(
                    "Compilation Failed",
                    f"Found {len(analyzer.errors)} semantic error(s).\nCheck the Semantic Analysis tab for details."
                )
            else:
                self.status_var.set("✅ Compilation successful!")
                success_msg = "✅ Compilation completed successfully!"
                if analyzer.warnings:
                    success_msg += f"\n⚠️  Found {len(analyzer.warnings)} warning(s)"
                messagebox.showinfo("Success", success_msg)
            
        except LexicalError as e:
            error_msg = f"❌ LEXICAL ERROR\n\n{str(e)}"
            self.all_output_text.insert("1.0", error_msg)
            self.status_var.set("❌ Lexical error")
            messagebox.showerror("Lexical Error", str(e))
            
        except ParseError as e:
            error_msg = f"❌ PARSE ERROR\n\n{str(e)}"
            self.all_output_text.insert("1.0", error_msg)
            self.status_var.set("❌ Parse error")
            messagebox.showerror("Parse Error", str(e))
            
        except Exception as e:
            error_msg = f"❌ UNEXPECTED ERROR\n\n{str(e)}"
            self.all_output_text.insert("1.0", error_msg)
            self.status_var.set("❌ Error occurred")
            messagebox.showerror("Error", str(e))
    
    def capture_output(self, func):
        """Capture print statements from a function"""
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        try:
            func()
            output = buffer.getvalue()
        finally:
            sys.stdout = old_stdout
        
        return output
    
    def clear_outputs(self):
        """Clear all output tabs"""
        self.tokens_text.delete("1.0", tk.END)
        self.ast_text.delete("1.0", tk.END)
        self.semantic_text.delete("1.0", tk.END)
        self.all_output_text.delete("1.0", tk.END)
        self.status_var.set("Ready")
    
    def new_file(self):
        """Create a new file"""
        if messagebox.askyesno("New File", "Clear current code and start new?"):
            self.code_text.delete("1.0", tk.END)
            self.clear_outputs()
            self.current_file = None
            self.file_label.config(text="Untitled")
            self.update_line_numbers()
    
    def open_file(self):
        """Open a Khamseena source file"""
        file_path = filedialog.askopenfilename(
            title="Open Khamseena File",
            filetypes=[("Khamseena Files", "*.kh"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                self.code_text.delete("1.0", tk.END)
                self.code_text.insert("1.0", code)
                self.current_file = file_path
                self.file_label.config(text=os.path.basename(file_path))
                self.update_line_numbers()
                self.status_var.set(f"Opened: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{e}")
    
    def save_file(self):
        """Save current file"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save file with new name"""
        file_path = filedialog.asksaveasfilename(
            title="Save Khamseena File",
            defaultextension=".kh",
            filetypes=[("Khamseena Files", "*.kh"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            self.file_label.config(text=os.path.basename(file_path))
    
    def save_to_file(self, file_path):
        """Save code to file"""
        try:
            code = self.code_text.get("1.0", tk.END)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            self.status_var.set(f"Saved: {file_path}")
            messagebox.showinfo("Success", "File saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Khamseena Programming Language
Compiler IDE v1.0

A complete compiler implementation featuring:
• Lexical Analysis (Scanner)
• Syntax Analysis (Parser)
• Semantic Analysis

Academic Project
© 2025"""
        messagebox.showinfo("About Khamseena IDE", about_text)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = KhamseenaIDE(root)
    root.mainloop()


if __name__ == "__main__":
    main()
