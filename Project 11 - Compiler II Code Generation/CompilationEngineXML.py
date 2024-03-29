import SymbolTable as d


class CompilationEngineXML:

    def __init__(self, tokenizer, output_file):
        """
        Creates a new compilation
        engine with the given input and
        output. The next routine called
        must be compileClass() .
        """
        self.output_file = output_file
        self.token = tokenizer

        # get first token
        self.advance()

        if self.type() != d.KEYWORD or self.key_word() != d.K_CLASS:
            raise CompilerError(self, "File must begin with \"class\"")

        self.compile_class()

    def compile_class(self):
        """
        Compiles a complete class.
        """
        this = "class"
        self.xml_open(this)
        self.write("\n")

        # class
        self.xml_keyword()
        self.advance()

        # name
        if self.type() != d.IDENTIFIER:
            raise CompilerError(self, "Class must begin with class name")
        self.xml_identifier()
        self.advance()

        self.compile_symbol_check("{", "Class must begin with {")

        self.compile_class_body()

        self.xml_close(this)

    def compile_class_var_dec(self):
        """
        Compiles a static declaration or a field declaration.
        """

        this = "classVarDec"
        self.xml_open(this)
        self.write("\n")

        # ( 'static' | 'field' ) type varName ( ',' varName)* ';'

        # static | field
        self.xml_keyword()
        self.advance()

        # type
        self.compile_type()

        # single varname
        self.compile_var_name()

        # possible additional ',' varname  's
        while self.type() == d.SYMBOL and self.symbol() == ",":
            self.xml_symbol()
            self.advance()
            self.compile_var_name()

        # ;
        self.compile_symbol_check(";", "expected closing \";\" for declaration")

        self.xml_close(this)

    def compile_subroutine(self):
        """
        Compiles a complete method, function, or constructor.
        """
        this = "subroutineDec"
        self.xml_open(this)
        self.write("\n")
        # ( 'constructor' | 'function' | 'method' )
        # ( 'void' | type) subroutineName '(' parameterList ')'
        # subroutineBody

        # 'constructor' | 'function' | 'method'
        self.xml_keyword()
        self.advance()

        # 'void' | type
        if self.type() == d.KEYWORD and self.key_word() == d.K_VOID:
            self.xml_keyword()
            self.advance()
        else:
            self.compile_type()

        # subroutineName
        self.compile_subroutine_name()

        # (
        self.compile_symbol_check("(", "expected opening \"(\" for parameterList ")

        # parameterList
        self.compile_parameter_list()

        # )
        self.compile_symbol_check(")", "expected closing \")\" for parameterList  ")

        # subroutineBody
        self.compile_subroutine_body()

        self.xml_close(this)

    def compile_parameter_list(self):
        """
        compiles a (possibly empty) parameter list,
        not including the enclosing ()
        :return:
        """
        this = "parameterList"
        self.xml_open(this)
        self.write("\n")
        # ( (type varName) ( ',' type varName)*)?

        # if empty - ?
        if self.type() == d.SYMBOL and self.symbol() == ")":
            self.xml_close(this)
            return

        # otherwise first (type varname) must exist

        # single type varName
        self.compile_type()
        self.compile_var_name()

        # possible additional type varname  's
        while self.type() == d.SYMBOL and self.symbol() == ",":
            self.xml_symbol()
            self.advance()
            self.compile_type()
            self.compile_var_name()

        self.xml_close(this)

    def compile_var_dec(self):
        """
        Compiles a var declaration.
        """
        this = "varDec"
        self.xml_open(this)
        self.write("\n")
        # 'var' type varName ( ',' varName)* ';'

        # var
        if self.type() != d.KEYWORD and self.key_word() != d.K_VAR:
            raise CompilerError(self, "expected \"var\" in variable declaration")
        self.xml_keyword()
        self.advance()

        # single type varName
        self.compile_type()
        self.compile_var_name()

        # possible additional "," varname  's
        while self.type() == d.SYMBOL and self.symbol() == ",":
            self.xml_symbol()
            self.advance()
            self.compile_var_name()

        # ';'
        self.compile_symbol_check(";", "expected ; at end of variable declaration")

        self.xml_close(this)

    def compile_statements(self):
        """
        Compiles a sequence of statements,
        not including the enclosing {}.
        """
        this = "statements"
        self.xml_open(this)
        self.write("\n")
        # statement*  0 or more times

        while self.type() == d.KEYWORD and self.key_word() in d.statement_types:
            statement_type = self.key_word()

            if statement_type == d.K_LET:
                self.compile_let()
            elif statement_type == d.K_IF:
                self.compile_if()
            elif statement_type == d.K_WHILE:
                self.compile_while()
            elif statement_type == d.K_DO:
                self.compile_do()
            elif statement_type == d.K_RETURN:
                self.compile_return()

        self.xml_close(this)

    def compile_let(self):
        """
        Compiles a let statement.
        """
        this = "letStatement"
        self.xml_open(this)
        self.write("\n")

        # 'let' varName ( '[' expression ']' )? '=' expression ';'

        # let
        self.xml_keyword()
        self.advance()

        # varname
        self.compile_var_name()

        # possible [ expression ]
        if self.type() == d.SYMBOL and self.symbol() == "[":
            self.xml_symbol()
            self.advance()
            self.compile_expression()
            self.compile_symbol_check("]", "expected to match [")

        # =
        self.compile_symbol_check("=", "expected in assignment")

        # expression
        self.compile_expression()

        # ;
        self.compile_symbol_check(";", "expected ; at end of assignment")

        self.xml_close(this)

    def compile_do(self):
        """
        Compiles a do statement.
        """
        this = "doStatement"
        self.xml_open(this)
        self.write("\n")

        # 'do' subroutineCall ';'

        # do
        self.xml_keyword()
        self.advance()

        # subroutineCall
        self.compile_subroutine_call()

        # ;
        self.compile_symbol_check(";", "expected ; after subroutine call")

        self.xml_close(this)

    def compile_while(self):
        """
        Compiles a while statement.
        """
        this = "whileStatement"
        self.xml_open(this)
        self.write("\n")

        # 'while' '(' expression ')' '{' statements '}'


        # while
        self.xml_keyword()
        self.advance()

        # '(' expression ')
        self.compile_symbol_check("(", "expected ( in (expression) for while")
        self.compile_expression()
        self.compile_symbol_check(")", "expected ) in (expression) for while")

        # '{' statements '}'
        self.compile_symbol_check("{", "expected { in {statements} for while")
        self.compile_statements()
        self.compile_symbol_check("}", "expected } in {statements} for while")

        self.xml_close(this)

    def compile_return(self):
        """
        Compiles a return statement.
        """
        this = "returnStatement"
        self.xml_open(this)
        self.write("\n")

        # 'return' expression? ';'

        # return
        self.xml_keyword()
        self.advance()

        # expression?
        if not (self.type() == d.SYMBOL and self.symbol() == ";"):
            self.compile_expression()

        # ';'
        self.compile_symbol_check(";", "expected ; for return")

        self.xml_close(this)

    def compile_if(self):
        """
        Compiles a if statement,
        possibly with a trailing else clause.
        """
        this = "ifStatement"
        self.xml_open(this)
        self.write("\n")

        # 'if' '(' expression ')' '{' statements '}' ( 'else' '{' statements '}' )?

        self.xml_keyword()
        self.advance()

        # '(' expression ')'
        self.compile_symbol_check("(", "expected ( in (expression) for if")
        self.compile_expression()
        self.compile_symbol_check(")", "expected ) in (expression) for if")

        # '{' statements '}'
        self.compile_symbol_check("{", "expected { in {statements} for if")
        self.compile_statements()
        self.compile_symbol_check("}", "expected } in {statements} for if")

        # else
        if self.type() == d.KEYWORD and self.key_word() == d.K_ELSE:
            # else
            self.xml_keyword()
            self.advance()

            # '{' statements '}'
            self.compile_symbol_check("{", "expected { in {statements} for else")
            self.compile_statements()
            self.compile_symbol_check("}", "expected } in {statements} for else")

        self.xml_close(this)

    def compile_expression(self):
        """
        Compiles a expression.
        """
        this = "expression"
        self.xml_open(this)
        self.write("\n")

        # term (op term)*

        # term
        self.compile_term()

        # (op term)*  0 or more times
        while self.type() == d.SYMBOL and self.symbol() in d.op:
            self.compile_op()
            self.compile_term()

        self.xml_close(this)

    def compile_term(self):

        this = "term"
        self.xml_open(this)
        self.write("\n")

        first_type = self.type()

        if first_type == d.INT_CONST:
            self.compile_int_const()

        elif first_type == d.STRING_CONST:
            self.compile_str_const()

        elif first_type == d.KEYWORD:
            if self.key_word() in d.keyword_constant:
                self.compile_keyword_const()

        elif first_type == d.IDENTIFIER:
            # could be varname, varname[expression], subroutine call ( "(" )
            self.advance()
            if self.type() == d.SYMBOL:

                if self.symbol() == "[":
                    # varname[expression]
                    self.retreat()

                    # varname
                    self.compile_var_name()

                    # [
                    self.compile_symbol_check("[", "[ expected for array index")

                    #  expression
                    self.compile_expression()

                    # [
                    self.compile_symbol_check("]", "] expected for array index")

                elif self.symbol() in {"(", "."}:
                    self.retreat()
                    self.compile_subroutine_call()

                else:
                    self.retreat()
                    self.xml_identifier()
                    self.advance()

            else:
                self.retreat()
                self.xml_identifier()
                self.advance()

        elif first_type == d.SYMBOL and self.symbol() == "(":
            # (expression)

            # (
            self.xml_symbol()
            self.advance()

            # expression
            self.compile_expression()

            # )
            self.compile_symbol_check(")", "expression should end with ) ")

        elif first_type == d.SYMBOL and self.symbol() in d.unary_op:
            # unOp term
            self.xml_symbol()
            self.advance()

            self.compile_term()

        else:
            raise CompilerError(self, "invalid term")

        self.xml_close(this)

    def compile_expression_list(self):
        """
        Compiles a (possibly empty) comma-separated list of expressions.
        """
        this = "expressionList"
        self.xml_open(this)
        self.write("\n")

        # (expression ( ',' expression)* )?
        # nothing, an expression, or many

        # empty
        if self.type() == d.SYMBOL and self.symbol() == ")":
            self.xml_close(this)
            return

        # one expression
        self.compile_expression()

        # possible additional expressions  's
        while self.type() == d.SYMBOL and self.symbol() == ",":
            self.xml_symbol()
            self.advance()
            self.compile_expression()

        self.xml_close(this)

    # sub compiler functions

    def compile_class_body(self):
        """
        Complies the body of a class
        """
        # we are now at first line in class

        # while next toks match classVarDec, compile class var dec
        while self.type() == d.KEYWORD and self.key_word() in d.static_field:
            #  static or field)
            self.compile_class_var_dec()

        # while next toks match subroutineDec, compile subroutineDec
        while self.type() == d.KEYWORD and self.key_word() in d.func:
            self.compile_subroutine()

        # ensure next token is }
        self.compile_symbol_check("}", "Class must contain only variable declarations and then subroutine declarations")

    def compile_type(self):
        """
        Compiles a type
        :return:
        """
        if self.type() == d.KEYWORD and self.key_word() in d.type:
            self.xml_keyword()
        elif self.type() == d.IDENTIFIER:
            self.xml_identifier()
        else:
            raise CompilerError(self, "type expected")
        self.advance()

    def compile_var_name(self):
        """
        write a variable name
        """
        self.xml_identifier()
        self.advance()

    def compile_symbol_check(self, symbol, message):
        if self.type() != d.SYMBOL or self.symbol() != symbol:
            raise CompilerError(self, message)
        self.xml_symbol()
        self.advance()

    def compile_subroutine_call(self):
        
        # subroutineName '(' expressionList ')' | (className |varName) '.' subroutineName '(' expressionList ')'
        # possibilities are
        # func(list)
        # class.func(list)
        # var.func(list)

        self.advance()
        if self.type() == d.SYMBOL and self.symbol() == "(":
            # subroutineName '(' expressionList ')'
            self.retreat()

            # subroutineName
            self.xml_identifier()
            self.advance()

            # (
            self.compile_symbol_check("(", "expected ( for function arguments")

            # expressionList
            self.compile_expression_list()

            # )
            self.compile_symbol_check(")", "expected ) for function arguments")

        elif self.type() == d.SYMBOL and self.symbol() == ".":
            # (className |varName) '.' subroutineName '(' expressionList ')'
            self.retreat()

            # (className |varName)
            self.xml_identifier()
            self.advance()

            # '.'
            self.compile_symbol_check(".", "expected . for class.method")

            # subroutineName
            self.xml_identifier()
            self.advance()

            # '('
            self.compile_symbol_check("(", "expected ( for function arguments")

            # expressionList
            self.compile_expression_list()

            # )
            self.compile_symbol_check(")", "expected ) for function arguments")

        else:
            raise CompilerError(self, "Expected func(list) or class.func(list)")

    def compile_subroutine_name(self):
        """
        Complies a subroutine name
        """
        self.xml_identifier()
        self.advance()

    def compile_subroutine_body(self):
        """
        :return:
        """
        this = "subroutineBody"
        self.xml_open(this)
        self.write("\n")
        # '{' varDec* statements '}'

        # '{'
        self.compile_symbol_check("{", "Expected { to open method body")

        #  varDec*
        while self.type() == d.KEYWORD and self.key_word() == d.K_VAR:
            self.compile_var_dec()

        # statements
        self.compile_statements()

        # '}'
        self.compile_symbol_check("}", "Expected } to close method body")

        self.xml_close(this)

    def compile_op(self):
        """
        compiles an operator
        """
        self.xml_symbol()
        self.advance()

    def compile_int_const(self):
        self.xml_open("integerConstant")
        self.write(str(self.int_val()))
        self.xml_close("integerConstant")
        self.advance()

    def compile_str_const(self):
        self.xml_open("stringConstant")
        self.write_string_constant(self.string_val())
        self.xml_close("stringConstant")
        self.advance()

    def compile_keyword_const(self):
        self.xml_keyword()
        self.advance()

    # HELPER FUNCTIONS

    def write(self, string):
        """
        writes a string to output file
        """
        self.output_file.write(string)

    def write_string_constant(self, string):
        """
        writes a string litral to xml
        """
        lst = list(string)
        new_str = ""
        for char in lst:
            if char in d.symbol_switch:
                new_str += d.symbol_switch[char]
            else:
                new_str += char
        self.write(new_str)

    def xml_open(self, string):
        """
        writes <string> to output file
        """
        self.write("<" + string + ">")

    def xml_close(self, string):
        """
        writes <string> to output file
        """
        self.write("</" + string + ">\n")

    def xml_keyword(self):
        """
        writes a keyword to output file
        """
        self.xml_open("keyword")
        self.write(d.keyword_switch[self.key_word()])
        self.xml_close("keyword")

    def xml_identifier(self):
        """
        writes a identifier to output file
        """
        self.xml_open("identifier")
        self.write(self.identifier())
        self.xml_close("identifier")

    def xml_symbol(self):
        """
        writes a symbol to output file
        """
        self.xml_open("symbol")
        self.write(d.symbol_switch[self.symbol()])
        self.xml_close("symbol")

    def advance(self):
        self.token.advance()

    def retreat(self):
        self.token.go_back()

    def line_num(self):
        return self.token.get_cur_line()

    def type(self):
        return self.token.token_type()

    def key_word(self):
        return self.token.key_word()

    def symbol(self):
        return self.token.symbol()

    def identifier(self):
        return self.token.identifier()

    def int_val(self):
        return self.token.int_val()

    def string_val(self):
        return self.token.string_val()


class CompilerError(SyntaxError):
    def __init__(self, engine, message=""):
        self.msg = "error in file\n" + engine.output_file.name + \
                   "\nerror in line " + str(engine.line_num()) + "\n" + \
                   message + "\n"