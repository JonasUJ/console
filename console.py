#TODO additions: func args, bools, conditions, if/else, imports, 
#TODO checks: check every error and improve return (what's currently being handled), 

import re, sys, os, time, copy
from ber2 import dictdb

class Handler:

    def __init__(self, path):
        self.HELP = '''
help - Shows this text

exit or quit - Terminates the script

say - Prints the first argument
e.g "say "Hello World!"" will print "Hello World!"
"
cal - Calculates the first argument
e.g "cal "4 + 2 * 2" will print "8"

set - Sets a keyword to reference a value
e.g "set kw v" will set "kw" to "v"

get - Gets the value of a keyword
e.g "get kw" will get the value og "kw"

create - Creates a file at the given path. Can be done in three different ways:
"create file.txt c:/" creates file.txt at c:/
"create c:/file.txt" does the same as above
"create file.txt" creates file.txt at standard_dir which is set with "set standard_dir dir"

open - Opens a file at the given path, if only the filename is given, it will try to look for the file in standard_dir
e.g "open file.txt" will open file.txt for editing

py - Enters the python interpeter

wait - Stops the script for x seconds

int - turns any decimal number into a whole number
e.g "int 2.0" will return "2" and "int 2.9563" will return "2"

ask - Prints the first argument and pauses the script until the user presses enter. Return whatever the user wrote
        '''
        self.NAME_OF_FILE = os.path.basename(path)
        self.DIRECTORY_OF_FILE = path.rstrip(self.NAME_OF_FILE)
        self.PATH_PATTERN = re.compile(r'^[a-zA-Z]:/(?:[^\\/:*?"<>|\r\n]+/)*[^\\/:*?"<>|\r\n]*$')
        self.COMMAND_PROMPT = "\n:: "
        self.RESERVED_NAMES = ['args']
        self.RESERVED_FUNC_NAMES = ['create']
        self.SAVES_DIRECTORY = self.DIRECTORY_OF_FILE + '/' + self.NAME_OF_FILE + '.saves/'
        if not os.path.exists(self.SAVES_DIRECTORY):
            os.makedirs(self.SAVES_DIRECTORY)
        self.CURRENTLY_HANDELING = ''
        self.COMMANDS = {
            'exit': (self.do_exit,), 
            'quit': (self.do_exit,), 
            'cal': (self.do_cal, True), 
            'say': (self.do_say, True),
            'help': (self.do_help,),
            'py': (self.do_py,), 
            'create': (self.do_create, True, True), 
            'set': (self.do_set, True, True), 
            'get': (self.do_get, True), 
            'open': (self.do_open, True),
            'func': (self.do_func, True, True),
            'wait': (self.do_wait, True),
            'int': (self.do_int, True),
            'ask': (self.do_ask, True),
            'repeat': (self.do_repeat, True, False)
            }
        if not os.path.exists(self.SAVES_DIRECTORY + 'save.txt'):
            with open(self.SAVES_DIRECTORY + 'save.txt', 'w'):
                pass
        self.cross_vars = dictdb(self.SAVES_DIRECTORY + 'save.txt')
        self.cross_vars_names = ['standard_dir']
        for var_name in self.cross_vars_names:
            if var_name not in self.cross_vars:
                self.cross_vars[var_name] = ''
        self.vars = {}
        if not os.path.exists(self.SAVES_DIRECTORY + 'funcs.txt'):
            with open(self.SAVES_DIRECTORY + 'funcs.txt', 'w'):
                pass
        self.funcs = dictdb(self.SAVES_DIRECTORY + 'funcs.txt')

    def default(self, error):
        return 'Error, %s\n%s' % (str(error), self.CURRENTLY_HANDELING)

    def do_help(self, **kwargs):
        return self.HELP
    
    def do_exit(self, **kwargs):
        self.cross_vars.save()
        sys.exit(1)
        return 'exited (unless you\'re seeing this)'

    def do_say(self, **kwargs):
        try:
            print(str(kwargs['arg1']))
            return ''
        except KeyError:
            return self.default('Not enough input to \'say\'')
        except ValueError:
            return self.default('Can\'t say that')
 
    def do_cal(self, **kwargs):
        try:
            result = eval(kwargs['arg1'])
            return float(result)
        except NameError as e:
            return self.default(e)
        except ZeroDivisionError as e:
            return self.default(e)
        except SyntaxError:
            return self.default('Invalid cal syntax')
        except TypeError:
            return kwargs['arg1']
        except KeyError:
            return self.default('Not enough \'cal\' input')

    def do_py(self, **kwargs):
        os.system('python')
        return ''
    
    def do_create(self, **kwargs):
        try:

            if self.PATH_PATTERN.match(kwargs['arg1']) and len(kwargs) == 2:            
                with open(kwargs['arg1'], 'w') as f:
                    return ''

            elif len(kwargs) <= 2:            
                with open(self.cross_vars['standard_dir'] + kwargs['arg1'], 'w') as f:
                    return ''

            elif self.PATH_PATTERN.match(kwargs['arg2']) and len(kwargs) >= 3:
                with open(kwargs['arg2'] + kwargs['arg1'], 'w') as f:
                    return ''
                
            else:
                return self.default('Not enough \'create\' input')
        except PermissionError:        
            return self.default('Couldn\'t create ' + kwargs['arg1'])
        except FileNotFoundError as e:
            return self.default(e.__str__())

    def do_set(self, **kwargs):
        try:
            if kwargs['arg1'] in self.cross_vars and len(kwargs) == 3:
                self.cross_vars[kwargs['arg1']] = kwargs['arg2']
                self.cross_vars.save()
                return ''
            elif kwargs['arg1'] not in self.RESERVED_NAMES and ';' in kwargs['arg2'] and len(kwargs) == 3:
                self.vars[kwargs['arg1']] = ['list', kwargs['arg2'].split(';')]
                return ''
            elif kwargs['arg1'] not in self.RESERVED_NAMES  and len(kwargs) == 3:
                self.vars[kwargs['arg1']] = ['var', kwargs['arg2']]
                return ''  
            elif self.vars[kwargs['arg1']][0] == 'list' and len(kwargs) >= 4:
                try:
                    self.vars[kwargs['arg1']][1][int(kwargs['arg2'])] = kwargs['arg3']
                    return ''
                except IndexError as e:
                    return self.default(e.__str__())  
            else:
                return self.default('\'' + kwargs['arg1'] + '\' is a reserved name and can\'t be changed')
        except KeyError:
            return self.default('Not enough input to \'set\'')

    def do_get(self, **kwargs):
        try:
            if kwargs['arg1'] in self.cross_vars and len(kwargs) == 2:
                return self.cross_vars[kwargs['arg1']]
            else:
                if self.vars[kwargs['arg1']][0] == 'var':
                    return self.vars[kwargs['arg1']][1]
                elif self.vars[kwargs['arg1']][0] == 'list' and len(kwargs) >= 3:
                    try:
                        return self.vars[kwargs['arg1']][1][int(kwargs['arg2'])]
                    except IndexError as e:
                        return self.default(e.__str__())
                    except ValueError:
                        return self.default('Can\'t get index \'%s\' of \'%s\'' % (kwargs['arg2'], kwargs['arg1']))
                elif self.vars[kwargs['arg1']][0] == 'list':
                    return ';'.join(self.vars[kwargs['arg1']][1])
                    
        except KeyError as e:
            return self.default('Couldn\'t find ' + e.__str__())

    def do_open(self, **kwargs):
        try:
            if self.PATH_PATTERN.match(kwargs['arg1']):
                os.startfile(kwargs['arg1'])
                return ''
            else:
                os.startfile(self.cross_vars['standard_dir'] + kwargs['arg1'])
                return ''
        except FileNotFoundError:
            return self.default('Couldn\'t find ' + kwargs['arg1'])

    def do_wait(self, **kwargs):
        try:
            time.sleep(float(kwargs['arg1']))
            return ''
        except ValueError:
            return self-default('Can\'t wait \'%s\'' % kwargs['arg1'])
        except OverflowError:
            return self.default('Can\'t wait that long')

    def do_func(self, **kwargs):
        try:
            if kwargs['arg1'] == 'create':
                if kwargs['arg2'] not in self.RESERVED_FUNC_NAMES:
                    try:
                        with open(self.SAVES_DIRECTORY + kwargs['arg2'] + '.cpy', 'w') as f:
                            self.funcs[kwargs['arg2']] = self.SAVES_DIRECTORY + kwargs['arg2'] + '.cpy'
                            self.funcs.save()
                            inst = ''
                            while inst != 'end\n':
                                inst = input(kwargs['arg2'] + '> ') + '\n'
                                f.write(inst if inst != 'end\n' else '')
                        return ''
                    except PermissionError:
                        return self.default('\'%s\' is an invalid name' % kwargs['arg2'])
                    except FileNotFoundError:
                        return self.default('\'%s\' is an invalid name' % kwargs['arg2'])
                else:
                    return self.default('Func name can\'t be \'%s\'' % kwargs['arg1'])
            elif kwargs['arg1'] in self.funcs:
                return self.handle_cpy_file(self.funcs[kwargs['arg1']])
            else:
                return self.default('No func named \'%s\'' % kwargs['arg1'])

        except KeyError as e:
            return self.default('Not enough \'func\' input')
            

    def do_int(self, **kwargs):
        try:
            return str(int(float(kwargs['arg1'])))
        except ValueError:
            return self.default('Can\'t int \'%s\'' % kwargs['arg1'])
    
    def do_ask(self, **kwargs):
        return input('' if len(kwargs) < 2 else kwargs['arg1'])

    def do_repeat(self, **kwargs):
        try:
            for i in range(int(float(kwargs['arg1']))):
                self.CURRENTLY_HANDELING = kwargs               
                print(self.handle_inst(kwargs['arg2']))
            return ''
        except KeyError as e:
            return self.default('Not enough \'repeat\' input')
        except ValueError:
            return self.default('Can\'t repeat \'%s\' times' % kwargs['arg1'])

    def handle_cpy_file(self, cpy_file):
        with open(cpy_file, 'r') as cpy:
            for inst in cpy.readlines():
                if inst != '\n':
                    self.CURRENTLY_HANDELING = inst
                    print(self.handle_inst(inst.strip('\n')))
        return ''
    
    def validate_cmd(self, cmd):
        for tup in self.COMMANDS:
            if tup[0] == cmd:
                return True
        else:
            return False

    def find_embed(self, inst):
        inst += ' '
        token = ''
        result = []
        start = 0
        embeds = found = started = 0
        for i in range(len(inst)):
            if inst[i] == '<':
                if started != 1:
                    start = i
                embeds += 1
                found = 1
                started = 1
            elif inst[i] == '>': embeds -= 1

            if found == 1 and embeds == 1:
                token = ''
            
            found = 0
            token += inst[i]
            if embeds == 0 and started > 0:
                result.append((token, start, i+1))
                started = 0
        return result          

    def parse_inst(self, parse_inst):
        parse_inst += ' '
        result = {'cmd': ''}
        token = ''
        embeds = quote = 0
        cur_arg = 1
        for i in range(len(parse_inst)):
            if result['cmd'] == '' and parse_inst[i] == ' ':
                result['cmd'] = token
                token = ''
            elif parse_inst[i] == '<': embeds += 1
            elif parse_inst[i] == '>': embeds -= 1
            elif parse_inst[i] == '"' and parse_inst[i - 1] != '\\': quote = 1 if quote == 0 else 0
            elif parse_inst[i] == ' ' and quote == 0 and embeds == 0:
                token = token.lstrip(' ').replace(r'\"', '"')
                token = token[1:len(token)-1] if token.startswith('"') and token.endswith('"') else token
                if token:
                    result['arg%s' % cur_arg] = token
                cur_arg += 1
                token = ''
            token += parse_inst[i]
        return result      

    def handle_inst(self, inst):
        parsed_inst = self.parse_inst(inst)
        if self.validate_cmd(parsed_inst['cmd']):
            return self.default('Invalid command \'%s\'' % parsed_inst['cmd'])
        for i in range(1, len(parsed_inst.values())):
            if '<' in parsed_inst['arg%s' % i] and self.COMMANDS[parsed_inst['cmd']][i]:
                embed = self.find_embed(parsed_inst['arg%s' % i])
                for tup in reversed(embed):
                    new_inst = tup[0][1:len(tup[0])-1] if tup[0].startswith('<') and tup[0].endswith('>') else tup[0][1:] if tup[0].startswith('<') else tup[0][:len(tup[0])-1]
                    self.CURRENTLY_HANDELING = new_inst
                    selfcall_outcome = self.handle_inst(new_inst)
                    parsed_inst['arg%s' % i] = list(parsed_inst['arg%s' % i])
                    parsed_inst['arg%s' % i][tup[1]: tup[2]] = list(str(selfcall_outcome))
                    parsed_inst['arg%s' % i] = ''.join(parsed_inst['arg%s' % i])
        try:
            for i in range(len(parsed_inst)):
                self.CURRENTLY_HANDELING += ' ' + parsed_inst['arg%s' % i] if i else parsed_inst['cmd']
            return self.COMMANDS[parsed_inst['cmd']][0](**parsed_inst)
        except KeyError as e:
            return self.default('Invalid command ' + e.__str__())

    def main(self):
        while True:
            instruction = input(self.COMMAND_PROMPT)
            if instruction:
                cmd_outcome = self.handle_inst(instruction)
                if cmd_outcome:
                    print(cmd_outcome)

try:
    os.system('cls')
    handler = Handler(sys.argv[1])
    handler.handle_cpy_file(sys.argv[1])
    input()
except IndexError:
    console = Handler(sys.argv[0])
    console.main()
