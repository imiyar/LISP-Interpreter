"""6.009 Lab 8A: carlae Interpreter"""

import sys    

class EvaluationError(Exception):
    """Exception to be raised if there is an error during evaluation."""      
    pass

def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    # Separate all the tokens with blank space, and then split the string into a list
    source = source.replace('(', ' ( ').replace(')', ' ) ').replace('\n', ' \n ').replace('\t', ' ')
    source = source.split(' ')

    # Keep all the meaningful tokens by checking which part is the comment
    semicolon = False
    result = []
    for i in range(len(source)):      
        token = source[i]  
        if token == '\n':
            semicolon = False
            continue
        elif token == ';' or semicolon: 
            semicolon = True
            continue            
        if token != '': result.append(source[i])                
    return result

def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    
    # Check if all the parentheses are matched
    def check_parenthese(tokens):
        paren = 0
        for token in tokens:
            if token == '(': paren += 1
            elif token == ')': paren -= 1
            if paren < 0: raise SyntaxError("Parentheses are mismatched!")
        if paren != 0: raise SyntaxError("Parentheses are mismatched!")
    
    # Convert each token into a Python data type
    def convert(token):
        try: sym = int(token)
        except: 
            try: sym = float(token)
            except: sym = str(token)
        return sym
    
    # Recursivly convert the tokens into a nested Python list
    def add_token(tokens):
        i = 0
        result = []
        while i < len(tokens):
            sym = convert(tokens[i])
            if sym == '(':
                i += 1
                parsed, num = add_token(tokens[i::])
                result.append(parsed)
                i += num
            elif sym == ')':
                i += 1
                return result, i
            else:
                result.append(sym)
                i += 1
        return result, i
    
    check_parenthese(tokens)
    return convert(tokens[0]) if len(tokens) == 1 else add_token(tokens[1:len(tokens)-1])[0]

def mul(args):
    """ Multiply the all the numbers in the list
    
    Args(list): A list of number
    Return(int or float): The computing result
    """
    result = 1
    for num in args:
        result *= num
    return result

# These are the constraints for the compare function
def inc(left, right):
    return left < right

def nondec(left, right):
    return left <= right

def dec(left, right):
    return left > right

def noninc(left, right):
    return left >= right

def equal(left, right):
    return left == right

def compare(args, func):
    """ Check if all the numbers in the list satisfy the constraint
    
    Args:
        args(list): a list of numbers to be checked
        func(function): the constraint function
        
    Return(Boolean): True/False represents if the list satisfies the constraint
    """
    
    for i in range(len(args)-1):
        if not func(args[i], args[i+1]):
            return False
    return True

def makelist(args):
    """ Make a python list into a LinkedList"""
    return LinkedList(args[0], makelist(args[1::])) if len(args) > 0 else LinkedList()

def concat(args):  
    """ Concatenate all the LinkedList 
    
    Args(list): an arbitrary number of LinkedLists
    Return(LinkedList): a new LinkedList representing the concatenation of the original LinkedLists
    """
    result = LinkedList()
    head = result
    for llist in args:
        # Only add the non-empty LinkedList to the end
        if not llist.isempty():
            while llist != None:
                result = result.add(llist.elt)
                llist = llist.next
    return head
    
def maplist(func, llist):
    """ Get the result of applying a given function to each element in the given LinkedList 
    
    Args:
        func(func): the function to be applied
        llist(LinkedList): The LinkedList of all the values
        
    Return(LinkedList): a new LinkedList representing the result
    """
    result = LinkedList()
    head = result
    while llist != None:
        try:
            value = func([llist.elt])
        except:
            value = func.call([llist.elt])
            
        result = result.add(value)
        llist = llist.next
    return head

def filterlist(func, llist):
    """ Get the elements of the given LinkedList for which the given function return true """
    
    result = LinkedList()
    head = result
    while llist != None:
        try:
            value = func([llist.elt])
        except:
            value = func.call([llist.elt])
            
        if value:
            result = result.add(llist.elt)           
        llist = llist.next
    return head

def reduce(func, llist, initval):
    """ Successively applying the given function to the elements in the LinkedList with an initial value """
    while llist != None:
        try:
            initval = func([initval, llist.elt])
        except:
            initval = func.call([initval, llist.elt]) 
        llist = llist.next
    return initval

def evaluate_file(file, env = None):
    """ Get the evaluated result from the expressions in a given file
    
    Args:
        file(string): The name of the file to be evaluated
        env(environment): The environment in which to evaluate the expression
        
    Return: The evaluated result
    """
    if env == None:
        env = environment()
    f = open(file)
    text = f.read()
    return evaluate(parse(tokenize(text)), env)

class buildins_env:
    """ The globle environment that has all the build-in operations/varibles
    
    Attributes:
        vardict(dict): all the build-in operations/varibles
        parent(environment): the parent environment, None by default
        
    Methods:
        hasvar: check if a varible/operation is defined in this environment
        getvar: get the expression of operation or the value of varible in this environment
        getparent: get the parent environment
    """
    
    def __init__(self, vardict = None, parent = None):
        if vardict == None:
            self.vardict = {
                '+': sum,
                '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
                '*': mul,
                '/': lambda args: args[0] if len(args) == 1 else (args[0] / mul(args[1::])),
                '>': lambda args: compare(args, dec),
                '>=': lambda args: compare(args, noninc),
                '<': lambda args: compare(args, inc),
                '<=': lambda args: compare(args, nondec),
                '=?': lambda args: compare(args, equal),
                '#t': True,
                '#f': False,
                'not': lambda args: not args[0],
                'list': makelist,
                'car': lambda args: args[0].car(),
                'cdr': lambda args: args[0].cdr(),
                'length': lambda args: args[0].length(),
                'elt-at-index': lambda args: args[0].elt_at_index(args[1]),
                'concat': concat,
                'map': lambda args: maplist(args[0], args[1]),
                'filter': lambda args: filterlist(args[0], args[1]),
                'reduce': lambda args: reduce(args[0], args[1], args[2]),
                'evaluate_file': lambda args: evaluate_file(args[0], args[1::]),
                'begin': lambda args: args[-1]
                }
        else:
            self.vardict = vardict
        self.parent = parent
        
    def hasvar(self, var):
        return True if var in self.vardict else False
    
    def getvar(self, var):
        if self.hasvar(var):
            return self.vardict[var]
           
    def getparent(self):
        return self.parent

        
class environment(buildins_env): 
    """ User defined environment, which is a sub-class of the globle environment
    
    Attributes:
        vardict(dict): all the build-in operations/varibles, empty dict by default
        parent(environment): the parent environment, buildins_env by default
        
    Methods:
        addvar: add a varible-value definition to this environment
    """      
    def __init__(self, vardict = None, parent = None):
        if vardict == None:
            vardict = {}
        if parent == None:
            parent = buildins_env()
        super(environment, self).__init__(vardict, parent)
        
    def addvar(self, newdict):
        for key in newdict:
            self.vardict[key] = newdict[key]

class func:
    """ User-defined function
    
    Attributes:
        params(list): all the required parameters for this function (in order)
        expr(list): function expressions
        env(environment): the environment where this function is defined
        
    Methods:
        call: call this function with the given values and the environment where the function is called
    """
    def __init__(self, params, expr, env = None):
        if env == None:
            env = environment()
        self.params = params
        self.expr = expr
        self.env = env
        
    def call(self, values):
        # Create a new environment (lexical scope) and evaluate the expressions
        lexical_env = environment(None, self.env)
        for i in range(len(values)):
            evaluate(['define', self.params[i], values[i]], lexical_env)
        return evaluate(self.expr, lexical_env)

    def __repr__(self):
        return "function object"
    
class LinkedList:
    """ An instance of a LinkedList structure
    
    Attributes:
        elt(any): the element at this position in the LinkedList
        next(LinkedList): an instance of LinkedList representing the next element in the LinkedList
        
    Methods:
        isempty:        return whether this LinkedList is empty
        car:            return the first element in this LinkedList
        cdr:            return the LinkedList containing all but the first element
        length:         return the length of this LinkedList
        	elt_at_index:   take an index as argument, and return the element at the given index in this LinkedList
        add:            Add an instance of LinkedList at the end of this LinkedList
    """
    def __init__(self, elt = None, next = None):
        self.elt = elt  
        self.next = None
        if type(next) == LinkedList:
            if next.elt != None:
                self.next = next
                
    def isempty(self):
        return self.elt == None
            
    def car(self):
        if not self.isempty():
            return self.elt
        else:
            raise EvaluationError("Empty list: No head element.")
    
    def cdr(self):
        return self.next
    
    def length(self):
        if self.isempty():
            return 0        
        if self.next == None:
            return 1
        return self.next.length() + 1
    
    def elt_at_index(self, index):
        if index == 0:
            return self.car()
        llist = self.next
        for i in range(index-1):
            llist = llist.next
        return llist.car()
    
    def add(self, value):
        # If this LinkedList is empty, change the empty element into the new instance
        if self.isempty():
            self.elt = value
            return self
        
        # If this LinkedList is not empty, add the new instance to the end
        elif self.next == None:
            self.next = LinkedList(value)
            return self.next
        else:
            raise EvaluationError("Not an end node!")
            
    def __repr__(self):
        return str(self.elt) + "->" + str(self.next)
        

def evaluate(tree, env = None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    
    # Create a new environment if no environment passed in
    if env == None:
        env = environment()
    
    # if the expression is a number, return itself
    if isinstance(tree, (int, float)): 
        return tree
    
    # if the expression is a string, return the value in this environment or its parent environment
    if isinstance(tree, str):        
        if env.hasvar(tree): 
            return env.getvar(tree)
        else:
            parent = env.getparent()
            if parent:
                return evaluate(tree, parent)
        raise EvaluationError("Varible/Function has not been defined!")
    
    # if the expression is an S-expression         
    if isinstance(tree, list):
        if len(tree) > 0:
            
            # If this expression is a special form starting with a keyword:
            # Conditions:
            if tree[0] == 'if':
                # Only evaluate the argument that it needs according to the boolean value
                return evaluate(tree[2], env) if evaluate(tree[1], env) else evaluate(tree[3], env)
            
            # Varible definations
            if tree[0] == 'define':
                # Easier function definitions 
                if isinstance(tree[1], list):
                    name = tree[1][0]
                    params = tree[1][1::]
                    tree[1] = name
                    tree[2] = ['lambda', params, tree[2]]
                # Add definition to the environment
                env.addvar({tree[1]: evaluate(tree[2], env)})
                return env.getvar(tree[1])               
                
            # User-defined functions
            if tree[0] == "lambda":
                return func(tree[1], tree[2], env)
            
            # Combinators
            # Evaluate the arguments in order
            if tree[0] == 'and':
                for sym in tree[1::]:
                    if not evaluate(sym, env):
                        return False
                return True
            
            if tree[0] == 'or':
                for sym in tree[1::]:
                    if evaluate(sym, env):
                        return True
                return False
            
            # Local varible definations
            if tree[0] == 'let':        
                # Create a new environment whose parent is the current environment
                new_env = environment(None, env)
                # Bind the varibles with the values and evaluate the expressions in this environment
                for defination in tree[1]:
                    evaluate(['define', defination[0], defination[1]], new_env)
                return evaluate(tree[2], new_env)
            
            # Changing the value of existing varible
            if tree[0] == 'set!':
                current_env = env
                while current_env != None:                   
                    # Find the first environment in which the varible is defined
                    if current_env.hasvar(tree[1]): 
                        # Update its binding in this environment to be the result of evaluating the expressions
                        val = evaluate(tree[2], env)
                        return evaluate(['define', tree[1], val], current_env)
                    else:
                        current_env = current_env.getparent()
                raise EvaluationError("Set! error: varible has not been defined!")
            
            # If this expression is a function-call
            evaluated = []
            for sym in tree:
                evaluated.append(evaluate(sym, env))
            try:
                # First try to use it as a build-in function
                return evaluated[0](evaluated[1::])
            except:
                # If there is an error, use it as a user-defined function
                if type(evaluated[0]) == func:
                    return evaluated[0].call(evaluated[1::])
                
            raise EvaluationError("Not a valid S-expression!")
                
        raise EvaluationError("Empty S-expression!")
            
    raise EvaluationError("Not valid syntax!")
    
def result_and_env(tree, env = None):
    """ A function for automatic checking"""
    
    if env == None:
        env = environment()
    return evaluate(tree, env), env

if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    env = environment()
    for filename in sys.argv[1::]:
        print(filename)
        print(evaluate_file(filename, env))
        
    source = input("in> ")
    while source != 'QUIT':
        tokens = tokenize(source)          
        try:
            expression = parse(tokens)
            print(">>>> Parsed:", expression)
            value = evaluate(expression, env)
            print("out>", value)
        except SyntaxError as detail:
            print("out> Syntax error:", detail)
        except EvaluationError as detail:
            print("out> Evaluation error:", detail)
        except:
            print("Unexpected error:", sys.exc_info()[0])
   
        source = input("in> ")
        
