"""
Semantic Analyzer for Khamseena Programming Language
Handles symbol tables, data type checking, and scope management
"""

from ast_nodes import *


class SemanticError(Exception):
    """Exception for semantic analysis errors"""
    pass


class SymbolTable:
    """Symbol table for variable and function tracking with scope support"""
    
    def __init__(self, parent=None, scope_name="global"):
        self.symbols = {}  # name -> {'type': type, 'kind': 'variable'/'function'/'parameter'}
        self.parent = parent  # Parent scope for nested scopes
        self.scope_name = scope_name
        self.children = []  # Child scopes
    
    def define(self, name, symbol_type, kind='variable'):
        """Add a symbol to the current scope"""
        if name in self.symbols:
            raise SemanticError(f"Symbol '{name}' already defined in {self.scope_name} scope")
        self.symbols[name] = {'type': symbol_type, 'kind': kind}
    
    def lookup(self, name):
        """Look up a symbol (checks parent scopes)"""
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        return None
    
    def lookup_local(self, name):
        """Look up symbol only in current scope"""
        return self.symbols.get(name)
    
    def exists(self, name):
        """Check if symbol exists in any scope"""
        return self.lookup(name) is not None
    
    def get_type(self, name):
        """Get type of a symbol"""
        symbol = self.lookup(name)
        return symbol['type'] if symbol else None


class SemanticAnalyzer:
    """Semantic analyzer with type checking and scope management"""
    
    def __init__(self):
        self.global_scope = SymbolTable(scope_name="global")
        self.current_scope = self.global_scope
        self.errors = []
        self.warnings = []
        self.scope_counter = 0
        
        # Type mapping from Khamseena to internal types
        self.type_map = {
            'count': 'INTEGER',
            'measure': 'FLOAT',
            'note': 'STRING',
            'flavor': 'BOOLEAN'
        }
    
    def analyze(self, ast):
        """Main entry point for semantic analysis"""
        print("\n" + "="*60)
        print("SEMANTIC ANALYSIS")
        print("="*60)
        
        try:
            self.visit(ast)
            
            # Print symbol table
            self.print_symbol_table()
            
            # Print results
            if self.errors:
                print("\n❌ Semantic Errors Found:")
                for i, error in enumerate(self.errors, 1):
                    print(f"  {i}. {error}")
                return False
            else:
                print("\n✅ Semantic Analysis Passed!")
                if self.warnings:
                    print("\n⚠️  Warnings:")
                    for i, warning in enumerate(self.warnings, 1):
                        print(f"  {i}. {warning}")
                return True
                
        except SemanticError as e:
            self.errors.append(str(e))
            print(f"\n❌ Fatal Semantic Error: {e}")
            return False
    
    def enter_scope(self, scope_name=None):
        """Create and enter a new nested scope"""
        if scope_name is None:
            self.scope_counter += 1
            scope_name = f"block_{self.scope_counter}"
        
        new_scope = SymbolTable(parent=self.current_scope, scope_name=scope_name)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
    
    def exit_scope(self):
        """Exit current scope and return to parent"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def visit(self, node):
        """Dispatch to appropriate visitor method"""
        method_name = f'visit_{node.__class__.__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)
    
    def generic_visit(self, node):
        """Default visitor for unknown nodes"""
        pass
    
    # ========== Visitor Methods ==========
    
    def visit_Program(self, node):
        """Visit program node"""
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_VarDeclaration(self, node):
        """Visit variable declaration - add to symbol table"""
        var_type = self.type_map.get(node.var_type, node.var_type.upper())
        
        # Check if already declared in current scope
        if self.current_scope.lookup_local(node.name):
            self.errors.append(
                f"Variable '{node.name}' already declared in {self.current_scope.scope_name} scope"
            )
            return
        
        # Type check initializer if present
        if node.initializer:
            init_type = self.get_expression_type(node.initializer)
            if not self.is_compatible(var_type, init_type):
                self.errors.append(
                    f"Type mismatch in variable '{node.name}': Cannot assign {init_type} to {var_type}"
                )
        
        # Add to symbol table
        self.current_scope.define(node.name, var_type, 'variable')
    
    def visit_Assignment(self, node):
        """Visit assignment - check variable exists and types match"""
        # Check if variable exists in any scope
        if not self.current_scope.exists(node.name):
            self.errors.append(f"Undefined variable '{node.name}'")
            return
        
        # Get variable type
        var_type = self.current_scope.get_type(node.name)
        
        # Get assigned value type
        value_type = self.get_expression_type(node.value)
        
        # Check type compatibility
        if not self.is_compatible(var_type, value_type):
            self.errors.append(
                f"Type mismatch in assignment to '{node.name}': Cannot assign {value_type} to {var_type}"
            )
    
    def visit_FunctionDef(self, node):
        """Visit function definition - create new scope"""
        # Add function to current scope
        try:
            self.current_scope.define(node.name, 'FUNCTION', 'function')
        except SemanticError as e:
            self.errors.append(str(e))
            return
        
        # Create new scope for function
        self.enter_scope(f"function_{node.name}")
        
        # Add parameters to function scope
        for param in node.parameters:
            param_type = self.type_map.get(param.param_type, param.param_type.upper() if param.param_type else 'ANY')
            try:
                self.current_scope.define(param.name, param_type, 'parameter')
            except SemanticError as e:
                self.errors.append(f"In function '{node.name}': {e}")
        
        # Visit function body
        self.visit(node.body)
        
        # Exit function scope
        self.exit_scope()
    
    def visit_Block(self, node):
        """Visit block - create new scope for {}"""
        # Create new scope for this block
        self.enter_scope()
        
        # Visit statements in this scope
        for stmt in node.statements:
            self.visit(stmt)
        
        # Exit block scope
        self.exit_scope()
    
    def visit_IfStatement(self, node):
        """Visit if statement - check condition type"""
        # Check condition is boolean
        cond_type = self.get_expression_type(node.condition)
        if cond_type not in ['BOOLEAN', 'ANY']:
            self.warnings.append(
                f"Condition in 'taste' statement should be BOOLEAN, got {cond_type}"
            )
        
        # Visit then branch (creates its own scope if it's a Block)
        self.visit(node.then_stmt)
        
        # Visit else branch if exists
        if node.else_stmt:
            self.visit(node.else_stmt)
    
    def visit_WhileStatement(self, node):
        """Visit while statement - check condition type"""
        # Check condition is boolean
        cond_type = self.get_expression_type(node.condition)
        if cond_type not in ['BOOLEAN', 'ANY']:
            self.warnings.append(
                f"Loop condition in 'stir' statement should be BOOLEAN, got {cond_type}"
            )
        
        # Visit body (creates its own scope if it's a Block)
        self.visit(node.body)
    
    def visit_PrintStatement(self, node):
        """Visit print statement"""
        # Just check the expression is valid
        self.get_expression_type(node.expression)
    
    def visit_InputStatement(self, node):
        """Visit input statement"""
        self.get_expression_type(node.expression)
    
    def visit_ReturnStatement(self, node):
        """Visit return statement"""
        if node.value:
            self.get_expression_type(node.value)
    
    def visit_FunctionCall(self, node):
        """Visit function call - check function exists"""
        if not self.current_scope.exists(node.name):
            self.errors.append(f"Undefined function '{node.name}'")
            return
        
        # Check it's actually a function
        symbol = self.current_scope.lookup(node.name)
        if symbol and symbol['kind'] != 'function':
            self.errors.append(f"'{node.name}' is not a function")
    
    def visit_ExpressionStatement(self, node):
        """Visit expression statement"""
        self.get_expression_type(node.expression)
    
    def visit_CommentStatement(self, node):
        """Visit comment - nothing to check"""
        pass
    
    def visit_FetchStatement(self, node):
        """Visit fetch statement - nothing to check for now"""
        pass
    
    # ========== Type Checking Methods ==========
    
    def get_expression_type(self, expr):
        """Get the type of an expression"""
        if isinstance(expr, Literal):
            return expr.type
        
        elif isinstance(expr, Variable):
            var_type = self.current_scope.get_type(expr.name)
            if not var_type:
                self.errors.append(f"Undefined variable '{expr.name}'")
                return 'ANY'
            return var_type
        
        elif isinstance(expr, BinaryOp):
            left_type = self.get_expression_type(expr.left)
            right_type = self.get_expression_type(expr.right)
            
            # Arithmetic operators: +, -, *, /, %
            if expr.operator in ['+', '-', '*', '/', '%']:
                if left_type in ['INTEGER', 'FLOAT'] and right_type in ['INTEGER', 'FLOAT']:
                    # If either is FLOAT, result is FLOAT
                    return 'FLOAT' if 'FLOAT' in [left_type, right_type] else 'INTEGER'
                else:
                    self.errors.append(
                        f"Invalid operands for '{expr.operator}': {left_type} and {right_type} (expected numeric types)"
                    )
                    return 'ANY'
            
            # Comparison operators: >, <, >=, <=, ==, !=
            elif expr.operator in ['>', '<', '>=', '<=', '==', '!=']:
                # Can compare same types
                if left_type != right_type and left_type != 'ANY' and right_type != 'ANY':
                    self.warnings.append(
                        f"Comparing different types: {left_type} {expr.operator} {right_type}"
                    )
                return 'BOOLEAN'
            
            # Logical operators: &&, ||
            elif expr.operator in ['&&', '||']:
                if left_type not in ['BOOLEAN', 'ANY']:
                    self.warnings.append(f"Left operand of '{expr.operator}' should be BOOLEAN, got {left_type}")
                if right_type not in ['BOOLEAN', 'ANY']:
                    self.warnings.append(f"Right operand of '{expr.operator}' should be BOOLEAN, got {right_type}")
                return 'BOOLEAN'
            
            return 'ANY'
        
        elif isinstance(expr, UnaryOp):
            operand_type = self.get_expression_type(expr.operand)
            
            # Unary minus: -
            if expr.operator == '-':
                if operand_type in ['INTEGER', 'FLOAT']:
                    return operand_type
                else:
                    self.errors.append(f"Cannot apply unary '-' to {operand_type} (expected numeric type)")
                    return 'ANY'
            
            # Logical NOT: !
            elif expr.operator == '!':
                if operand_type not in ['BOOLEAN', 'ANY']:
                    self.warnings.append(f"Logical NOT '!' should operate on BOOLEAN, got {operand_type}")
                return 'BOOLEAN'
            
            return 'ANY'
        
        elif isinstance(expr, FunctionCall):
            # For now, we don't track function return types
            return 'ANY'
        
        return 'ANY'
    
    def is_compatible(self, target_type, source_type):
        """Check if source type can be assigned to target type"""
        if source_type == 'ANY' or target_type == 'ANY':
            return True
        
        if target_type == source_type:
            return True
        
        # Allow INTEGER to FLOAT implicit conversion
        if target_type == 'FLOAT' and source_type == 'INTEGER':
            return True
        
        return False
    
    def print_symbol_table(self, scope=None, indent=0):
        """Print the symbol table with scope hierarchy"""
        if scope is None:
            scope = self.global_scope
            print("\n" + "-"*60)
            print("SYMBOL TABLE (Scope Hierarchy)")
            print("-"*60)
        
        prefix = "  " * indent
        print(f"\n{prefix}Scope: {scope.scope_name}")
        print(f"{prefix}{'-' * 40}")
        
        if scope.symbols:
            print(f"{prefix}{'Name':<15} {'Type':<12} {'Kind':<12}")
            print(f"{prefix}{'-' * 40}")
            for name, info in scope.symbols.items():
                print(f"{prefix}{name:<15} {info['type']:<12} {info['kind']:<12}")
        else:
            print(f"{prefix}(empty)")
        
        # Print child scopes
        for child in scope.children:
            self.print_symbol_table(child, indent + 1)
        
        if indent == 0:
            print("-"*60)
