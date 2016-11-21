import re, sys, os, fp, time, copy
from ber2 import dictdb

class Handler:

    def __init__(self, path):
        self.NAME_OF_FILE = os.path.basename(path)
        self.DIRECTORY_OF_FILE = path.rstrip(self.NAME_OF_FILE)
        #self.MAX_CMD_ARGS = 5 # There'll be one less, since it counts the command as one
        #self.COMMAND_PATTERN_UNCOMPILED = r'([a-zA-Z]+)' + r''.join([r'(?: (?P<quote%s>\")?((?(quote%s)(?:\\"|[a-zA-Z0-9_.+*/!#&/()=?~<>: -])+|[a-zA-Z0-9_.+*/!#&/()=?~<>:"-]+))(?(quote%s)(?P=quote%s)))?' % (x, x, x, x) for x in range(self.MAX_CMD_ARGS)])
        #self.COMMAND_PATTERN = re.compile(self.COMMAND_PATTERN_UNCOMPILED) # I don't know why I keep this, it isn't used
        #self.EMBEDDED_COMMAND_PATTERN = re.compile('<' + self.COMMAND_PATTERN_UNCOMPILED + '>')
        self.PATH_PATTERN = re.compile(r'^[a-zA-Z]:/(?:[^\\/:*?"<>|\r\n]+/)*[^\\/:*?"<>|\r\n]*$')
        self.COMMAND_PROMPT = "\n:: "
        self.RESERVED_NAMES = []
        self.RESERVED_FUNC_NAMES = ['create']
        self.SAVES_DIRECTORY = self.DIRECTORY_OF_FILE + '/' + self.NAME_OF_FILE + '.saves/'
        if not os.path.exists(self.SAVES_DIRECTORY):
            os.makedirs(self.SAVES_DIRECTORY)
        self.COMMANDS = {
            'exit': (self.do_exit), 
            'quit': (self.do_exit), 
            'cal': (self.do_cal, True), 
            'say': (self.do_say, True),
            'help': (self.do_help),
            'py': (self.do_py), 
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
        self.vars = {}
        if not os.path.exists(self.SAVES_DIRECTORY + 'funcs.txt'):
            with open(self.SAVES_DIRECTORY + 'funcs.txt', 'w'):
                pass
        self.funcs = dictdb(self.SAVES_DIRECTORY + 'funcs.txt')

    def default(self, error):
        #if restart: 
        #   return (restart, 'Error: ' + str(error))
        #else:
        return 'Error, ' + str(error)

    def do_help(self, **kwargs):
        help_dict = fp.parse_file(self.DIRECTORY_OF_FILE + 'consolepyhelp.fp')
        sorted_keys = sorted(list(help_dict['help'].keys()))
        for cmd in sorted_keys:
           print('%s - %s' % (cmd, help_dict['help'][cmd]))
        return ''
    
    def do_exit(self, **kwargs):
        self.cross_vars.save()
        sys.exit(1)
        return 'exited (unless you\'re seeing this)'

    def do_say(self, **kwargs):
        try:
            return str(kwargs['arg1'])
        except KeyError:
            return self.default('Not enough input to say')
 
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
        os.system('py')
        return ''
    
    def do_create(self, **kwargs):
        try:

            if self.PATH_PATTERN.match(kwargs['arg1']):            
                with open(kwargs['arg1'], 'w') as f:
                    return ''

            elif len(kwargs) <= 2:            
                with open(self.cross_vars['standard_dir'] + kwargs['arg1'], 'w') as f:
                    return ''

            elif self.PATH_PATTERN.match(kwargs['arg2']):
                with open(kwargs['arg2'] + kwargs['arg1'], 'w') as f:
                    return ''
                
        except KeyError:
            return self.default('Not enough \'create\' input')
        except PermissionError:        
            return 'Couldn\'t create ' + kwargs['arg1']

    def do_set(self, **kwargs):
        if kwargs['arg1'] not in self.RESERVED_NAMES and kwargs['arg1'] not in self.cross_vars:
            self.vars[kwargs['arg1']] = kwargs['arg2']
            return ''
        elif kwargs['arg1'] in self.cross_vars:
            self.cross_vars[kwargs['arg1']] = kwargs['arg2']
            self.cross_vars.save()
        else:
            return '\'' + kwargs['arg1'] + '\' is a reserved name and can\'t be changed'

    def do_get(self, **kwargs):
        try:
            if kwargs['arg1'] in self.cross_vars:
                return self.cross_vars[kwargs['arg1']]
            else:
                return self.vars[kwargs['arg1']]
        except KeyError as e:
            return 'Couldn\'t find ' + e.__str__()

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
                            self.funcs[kwargs['arg2']] = self.DIRECTORY_OF_FILE + kwargs['arg2'] + '.cpy'
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
            arg = copy.deepcopy(kwargs['arg2'])
            for i in range(int(kwargs['arg1'])):               
                print(self.handle_inst(arg))
            return ''
        except KeyError:
            return self.default('Not enough \'repeat\' input')
        except ValueError:
            return self.default('Can\'t repeat \'%s\' times' % kwargs['arg1'])

    def handle_cpy_file(self, cpy_file):
        with open(cpy_file, 'r') as cpy:
            for inst in cpy.readlines():
                if inst != '\n':
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
                result['arg%s' % cur_arg] = token
                cur_arg += 1
                token = ''
            token += parse_inst[i]
        return result      

    def handle_inst(self, inst):
        parsed_inst = self.parse_inst(inst)
        #print(parsed_inst)
        if self.validate_cmd(parsed_inst['cmd']):
            return self.default('Invalid command \'%s\'' % parsed_inst['cmd'])
        for i in range(1, len(parsed_inst.values())):
            if '<' in parsed_inst['arg%s' % i] and self.COMMANDS[parsed_inst['cmd']][i]:
                embed = self.find_embed(parsed_inst['arg%s' % i])
                for tup in reversed(embed):
                    #print(tup)
                    new_inst = tup[0][1:len(tup[0])-1] if tup[0].startswith('<') and tup[0].endswith('>') else tup[0][1:] if tup[0].startswith('<') else tup[0][:len(tup[0])-1]
                    selfcall_outcome = self.handle_inst(new_inst)
                    parsed_inst['arg%s' % i] = list(parsed_inst['arg%s' % i])
                    parsed_inst['arg%s' % i][tup[1]: tup[2]] = list(str(selfcall_outcome))
                    parsed_inst['arg%s' % i] = ''.join(parsed_inst['arg%s' % i])
        try:
            #print(parsed_inst)
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
    handler = Handler(sys.argv[1])#r'C:\Users\jonas\OneDrive\Dokumenter\GitHub\console\fakerer.cpy')
    handler.handle_cpy_file(sys.argv[1])#r'C:\Users\jonas\OneDrive\Dokumenter\GitHub\console\fakerer.cpy')
    input()
except IndexError:
    console = Handler(sys.argv[0])
    console.main()
