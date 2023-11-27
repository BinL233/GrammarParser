import re
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.type == other.type and self.value == other.value
        return False

    def __repr__(self):
        return f'Token({self.type}, {self.value})'

class Lexer:
    def __init__(self, input):
        self.input = input
        self.position = 0

    def tokenize(self):
        tokens = []
        
        while self.position < len(self.input):
            char = self.input[self.position]

            if char.isspace():
                self.position += 1
                continue

            # Find token string
            curr_part = ""
            i = self.position
            while i < len(self.input):
                # Find type
                if re.match(r'float|char|int', curr_part + self.input[i]):
                    curr_part += self.input[i]
                    break
                # Find others
                elif re.match(r'(?:|[0-9]+.[0-9]+|[a-zA-Z]+|[0-9]+|\'[a-zA-Z]+\'|[+\-*/;=()])', curr_part + self.input[i]):
                    curr_part += self.input[i]
                    i += 1
                else:
                    break
            
            if re.match(r'float|char|int', curr_part):
                match = re.match(r'float|char|int', curr_part)
                value = match.group(0)
                self.position += len(value)
                tokens.append(Token('TYPE', value))

            elif re.match(r'(?:[0-9]+.[0-9]+|[a-zA-Z]+|[0-9]+|\'[a-zA-Z]+\'|[+\-*/;=()])', curr_part):
                match = re.match(r'(?:[0-9]+.[0-9]+|[a-zA-Z]+|[0-9]+|\'[a-zA-Z]+\'|[+\-*/;=()])', curr_part)
                value = match.group(0)
                self.position += len(value)

                # Check integer
                if re.match(r'[0-9]+.[0-9]+', value):
                    tokens.append(Token('FLOAT', float(value)))
                elif re.match(r'[0-9]+', value):
                    tokens.append(Token('INTEGER', int(value)))
                # Check char
                elif re.match(r'\'[a-zA-Z]+\'', value):
                    tokens.append(Token('CHAR', value.strip("'")))
                else:
                    # Check operator
                    if value == '=':
                        tokens.append(Token("ASSIGN", value))
                    elif value == '+' or value == '-' or value == '*' or value == '/':
                        tokens.append(Token("OPERATOR", value))
                    elif value == ';':
                        tokens.append(Token("SEMICOLON", value))
                    elif value == '(' or value == ')':
                        tokens.append(Token("PARENTHESIS", value))

                    # Check variable
                    elif value.isalpha():
                        tokens.append(Token("VARIABLE", value))

                    # Invalid Token
                    else:
                        raise Exception("Invalid character")
            
            # Invalid Token
            else:
                print("curr_part:", curr_part)
                raise Exception('Invalid character')

        return tokens




class SymbolTable:
    def __init__(self):
        self.table = {}

    def add(self, identifier, type, initialized=False):
        if identifier in self.table:
            raise Exception("Invalid character")
        
        self.table[identifier] = [type, initialized]

    def is_initialized(self, identifier):
        if self.table[identifier][1]:
            return True
        
        return False

    def set_initialized(self, identifier):
        if identifier not in self.table:
            raise Exception("Invalid character")
        
        self.table[identifier][1] = True

    def lookup(self, identifier):
        if identifier not in self.table:
            raise Exception("Invalid character")

        return self.table[identifier][0]

    def update(self, identifier, newType):
        if identifier not in self.table:
            raise Exception("Invalid character")

        self.table[identifier][0] = newType

class TypeChecker:

    @staticmethod
    def check_assignment(target_type, value_type):
        if value_type == target_type:
            return True
        elif target_type == "FLOAT":
            if value_type == "INTEGER" or value_type == "FLOAT":
                return True
        
        return False
    
    @staticmethod
    def result_type_of_op(left_type, op, right_type):
        """
        Determines the resulting type of a binary operation given the types of its operands.

        Args:
            left_type (str): The type of the left operand.
            op (str): The operator being applied.
            right_type (str): The type of the right operand.

        Returns:
            str: The resulting type of the operation.
        """
        valid_ops = ['+', '-', '*', '/'] #Hint

        if left_type not in ["FLOAT", "INTEGER", "CHAR"] or right_type not in ["FLOAT", "INTEGER", "CHAR"]:
            raise Exception("Type mismatch")

        elif left_type == "FLOAT" or right_type == "FLOAT":
            return "FLOAT"
        
        elif left_type == "INTEGER" or right_type == "INTEGER":
            return "INTEGER"
        
        elif (left_type == "CHAR" or right_type == "CHAR") and op == '+':
            return "CHAR"
        
        else:
            raise Exception("Type mismatch")
        


    @staticmethod
    def check_op(left_type, op, right_type):
        if left_type == "INTEGER" or left_type == "FLOAT":
            if right_type == "INTEGER" or right_type == "FLOAT":
                return True
        
        return False

class Node:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children if children is not None else []

    def __str__(self, level=0):
        ret = "\t" * level + f'{self.type}: {self.value}\n'
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.symbol_table = SymbolTable()

    def consume(self, expected_type=None):
        if self.tokens[self.position].type == expected_type:
            self.position += 1
            return self.tokens[self.position-1]
        else:
            raise Exception("Syntax error")

    def peek(self):
        return self.tokens[self.position]

    # Traverse tree to find difference
    def find_diff(self, root, target_type, curr_op):
        # print("root_type:", root.type, "target_type:", target_type, "curr_op:", curr_op, "value:", root.value)
        if root.type in ["ASSIGN", "OPERATOR"]:
            curr_op = root.type
        if root.type in ["VARIABLE"]:
            root.type = self.symbol_table.lookup(root.value)
        if root.type in ["CHAR", "FLOAT", "INTEGER"]:
            if not TypeChecker.check_assignment(target_type, root.type):
                return curr_op, TypeChecker.check_assignment(target_type, root.type)

        for x in root.children:
            self.find_diff(x, target_type, curr_op)

        return None, None

    def parse(self):
        # Create root
        root = Node("Program")
        temp = root.children
        temp.append(Node("StatementList"))
        temp = temp[0].children

        # Traverse statements
        while self.position < len(self.tokens):
            temp.append(self.parse_statement())

        return root

    def parse_statement(self):
        state = Node("Statement")

        token = self.peek()
        # Parse declaration if token is TYPE
        if token.type == 'TYPE':
            return self.parse_declaration()

        temp = state.children
        temp.append(self.parse_assignment())
        return state

    def parse_declaration(self):
        # Need to consume TYPE token

        curr_type = Node(self.peek().type, self.peek().value)
        type_token = self.consume('TYPE')
        variable = Node(self.peek().type, self.peek().value)
        var_token = self.consume('VARIABLE')
        expression_node = None

        declared_type = type_token.value.upper()
        if declared_type == 'INT':
            declared_type = 'INTEGER'  

        if self.tokens[self.position].type == "ASSIGN":
            assign = Node("ASSIGN", "=")
            self.consume("ASSIGN")
            declaration = Node("Declaration", "DECLARATION_WITH_ASSIGNMENT")

            declaration.children.append(assign)
            declaration.children.append(curr_type)
            temp = assign.children
            temp.append(variable)

            expre = self.parse_expression()

            # Call expressions
            temp.append(expre)

            # Add Symbol
            self.symbol_table.add(variable.value, declared_type, True)

            # Check diff
            op, is_valid = self.find_diff(expre, declared_type, "ASSIGN")

            if op != None and not is_valid:
                if op == "ASSIGN":
                    raise Exception("Type mismatch")
                else:
                    raise Exception("Incompatible types for operation")


            # Check types
            # TypeChecker.check_assignment(decleared_type, self.symbol_table.lookup(expre))

        else:
            declaration = Node("Declaration", "DECLARATION")
            declaration.children.append(curr_type)
            declaration.children.append(variable)

            # Add Symbol
            self.symbol_table.add(variable.value, declared_type)

        # Check SEMICOLON
        self.consume("SEMICOLON")

        return declaration

    def parse_assignment(self):
        assignment = Node("Assignment")

        # Check VARIABLE
        variable = Node(self.peek().type, self.peek().value)
        self.consume("VARIABLE")

        # Check ASSIGN
        assign = Node("ASSIGN", '=')
        self.consume("ASSIGN")

        assignment.children.append(assign)
        temp = assign.children

        temp.append(variable)

        # Call expressions
        expre = self.parse_expression()
        temp.append(expre)

        # Add symbol
        # self.symbol_table.add(variable.value, self.symbol_table.lookup(expre.value))

        if variable.value in self.symbol_table.table:
            op, is_valid = self.find_diff(expre, self.symbol_table.lookup(variable.value), "ASSIGN")

            if not is_valid:
                if op == "ASSIGN":
                    raise Exception("Type mismatch")
                else:
                    raise Exception("Incompatible types for operation")

        # Check SEMICOLON
        self.consume("SEMICOLON")
        
        return assignment

    def parse_expression(self):
        # Check SEMICOLON
        if self.position == len(self.tokens)-1 and self.peek().type != "SEMICOLON":
            raise Exception('Syntax error: unexpected end of input')

        # Assign to signle token
        if self.tokens[self.position+1].type != "OPERATOR" and (self.tokens[self.position].type == "CHAR" or self.tokens[self.position].type == "FLOAT" or self.tokens[self.position].type == "INTEGER" or self.tokens[self.position].type == "VARIABLE"):
            term = self.parse_term()
            # if term.type == "INTEGER" or term.type == "FLOAT":
            #     self.symbol_table.add(term.value, term.type)

            self.position += 1
            return term

        # Parenthesis
        if self.peek().value == '(':
            self.position += 1
            expression = self.parse_expression()
            self.consume("PARENTHESIS")
            if self.peek().type != "SEMICOLON":
                oper = Node(self.peek().type, self.peek().value)
                self.consume("OPERATOR")
                expre = self.parse_expression()
                oper.children.append(expression)
                oper.children.append(expre)

                # result_type = TypeChecker.result_type_of_op(self.symbol_table.lookup(expression.value), oper.value, self.symbol_table.lookup(expre.value))
                # self.symbol_table.add(oper.value, result_type)

                return oper

            #self.symbol_table.add(self.symbol_table.lookup(expression.value), expression.type)
            return expression                   
        
        # Define term
        variable = self.parse_term()

        # if variable.type == "INTEGER" or variable.type == "FLOAT":
        #     self.symbol_table.add(variable.value, variable.type)

        self.position += 1
        
        oper = Node(self.peek().type, self.peek().value)
        self.consume("OPERATOR")
        oper.children.append(variable)
        expre = self.parse_expression()
        oper.children.append(expre)

        # if variable.type == "INTEGER" or variable.type == "FLOAT":
        #     print(variable.type, self.symbol_table.lookup(expre.value))
        #     result_type = TypeChecker.result_type_of_op(variable.type, oper.value, self.symbol_table.lookup(expre.value))
        # else:
        #     print(self.symbol_table.lookup(variable.value), self.symbol_table.lookup(expre.value))
        #     result_type = TypeChecker.result_type_of_op(self.symbol_table.lookup(variable.value), oper.value, self.symbol_table.lookup(expre.value))

        # print("last:", oper.value, result_type)
        # self.symbol_table.add(oper.value, result_type)
        return oper

    def parse_term(self):
        token_type = self.peek().type
        if token_type == "INTEGER":
            return Node("INTEGER", self.peek().value)
        elif token_type == "FLOAT":
            return Node("FLOAT", self.peek().value)
        elif token_type == "CHAR":
            return Node("CHAR", self.peek().value)
        elif token_type == "VARIABLE":
            return Node("VARIABLE", self.peek().value)
        else:
            raise Exception("Syntax error")