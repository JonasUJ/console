import re, sys, os, fp
from ber2 import dictdb

class Handler:

    def __init__(self):
        self.NAME_OF_FILE = os.path.basename(sys.argv[0])
        self.DIRECTORY_OF_FILE = sys.argv[0].rstrip(self.NAME_OF_FILE)
        self.MAX_CMD_ARGS = 5 # There'll be one less, since it counts the command as one
        self.COMMAND_PATTERN_UNCOMPILED = r'([a-zA-Z]+)' + r''.join([r'(?: (?P<quote%s>\"|~)?((?(quote%s)(?:\\"|[a-zA-Z0-9_.+*/!#&/()=?~<>: -])+|[a-zA-Z0-9_.+*/!#&/()=?~<>:"-]+))(?(quote%s)(?P=quote%s)))?' % (x, x, x, x) for x in range(self.MAX_CMD_ARGS)])
        self.COMMAND_PATTERN = re.compile(self.COMMAND_PATTERN_UNCOMPILED)
        self.EMBEDDED_COMMAND_PATTERN = re.compile('~' + self.COMMAND_PATTERN_UNCOMPILED + '~')
        self.PATH_PATTERN = re.compile(r'^[a-zA-Z]:/(?:[^\\/:*?"<>|\r\n]+/)*[^\\/:*?"<>|\r\n]*$')
        self.COMMAND_PROMPT = "\n~ "
        self.RESERVED_NAMES = []
        self.COMMANDS = {'exit': self.do_exit, 'quit': self.do_exit, 'cal': self.do_cal, 'say': self.do_say, 'help': self.do_help, 'py': self.do_py, 'create': self.do_create, 'set': self.do_set, 'get': self.do_get}
        self.save_dict = dictdb(self.DIRECTORY_OF_FILE + 'save.txt')

    def default(self, error, restart):
        if restart: 
            return (restart, 'Error: ' + str(error))
        else:
            return 'Error, ' + str(error)

    def do_help(self, **kwargs):
        help_dict = fp.parse_file(self.DIRECTORY_OF_FILE + 'consolepyhelp.txt')
        sorted_keys = sorted(list(help_dict['help'].keys()))
        for cmd in sorted_keys:
           print('%s - %s' % (cmd, help_dict['help'][cmd]))
        return ''
    
    def do_exit(self, **kwargs):
        self.save_dict.save()
        sys.exit(1)
        return 'exited (unless you\'re seeing this)'

    def do_say(self, **kwargs):
        return str(kwargs['arg1'])
 
    def do_cal(self, **kwargs):
        try:
            result = eval(kwargs['arg1'])
            return float(result)
        except NameError as e:
            return self.default(e, False)
        except ZeroDivisionError as e:
            return self.default(e, False)
        except SyntaxError as e:
            return self.default('Invalid cal syntax' , False)
        except TypeError:
            return kwargs['arg1']

    def do_py(self, **kwargs):
        os.system('py')
        return ''
    
    def do_create(self, **kwargs):
        try:
            if self.PATH_PATTERN.match(kwargs['arg1']):
                try:
                    with open(kwargs['arg1'], 'w') as f:
                        return ''
                except PermissionError:        
                    return 'Couldn\'t create ' + kwargs['arg1']
            elif kwargs['arg2'] == None and kwargs['arg1'] != None:
                try:
                    with open(self.save_dict['standard_dir'] + kwargs['arg1'], 'w') as f:
                        return ''
                except PermissionError:        
                    return 'Couldn\'t create ' + kwargs['arg1']
            elif self.PATH_PATTERN.match(kwargs['arg2']):
                try:
                    with open(kwargs['arg2'] + kwargs['arg1'], 'w') as f:
                        return ''
                except PermissionError:        
                    return 'Couldn\'t create ' + kwargs['arg1']
        except TypeError:
            return 'No input'

    def do_set(self, **kwargs):
        if kwargs['arg1'] not in self.RESERVED_NAMES:
            self.save_dict[kwargs['arg1']] = kwargs['arg2']
            self.save_dict.save()
            return ''
        else:
            return '\'' + kwargs['arg1'] + '\' is a reserved name and can\'t be changed'

    def do_get(self, **kwargs):
        try:
            return self.save_dict[kwargs['arg1']]
        except KeyError as e:
            return 'Couldn\'t find ' + e.__str__()

    def parse_groups(self, groups):
        result = [('cmd', groups[0])]
        for x in range(2, self.MAX_CMD_ARGS * 2, 2):
            try:
                value = groups[x].replace(r'\"', '"')
            except AttributeError:
                value = groups[x]
            result.append(('arg%s' % str(int((x / 2))), value))
        return dict(result)

    def handle_inst(self, match):
        try:
            parsed_inst = self.parse_groups(match.groups())
            #print('after parsed ', parsed_inst)
        except AttributeError:
            return self.default('Invalid imbedded command', True)

        for i in range(1, len([x for x in parsed_inst.values() if x != None])):
            arg = parsed_inst['arg%s' % i]

            if '~' in arg:
                new_match = self.EMBEDDED_COMMAND_PATTERN.search(arg)
                if new_match:
                    selfcall_outcome = self.handle_inst(new_match)
                    #print('sends off ', new_match)
                else:
                    new_match = self.COMMAND_PATTERN.match(arg)
                    selfcall_outcome = arg
                try:
                    parsed_inst['arg%s' % i] = list(parsed_inst['arg%s' % i])
                    parsed_inst['arg%s' % i][new_match.span()[0]: new_match.span()[1]] = list(str(selfcall_outcome))
                    parsed_inst['arg%s' % i] = ''.join(parsed_inst['arg%s' % i])
                    return parsed_inst['arg%s' % i]
                except AttributeError:
                    return self.default('Invalid imbedded command', True)
            '''
            if self.COMMAND_PATTERN.match(parsed_inst['arg%s' % i]) and self.COMMAND_PATTERN.match(parsed_inst['arg%s' % i]).group(1) in self.COMMANDS:
                #print('command ', self.COMMAND_PATTERN.match(parsed_inst['arg%s' % i]).group(1))
                #print('got invoked by ', parsed_inst)
                new_match = self.COMMAND_PATTERN.match(parsed_inst['arg%s' % i])
                #print('sends off ', new_match)
                selfcall_outcome = self.handle_inst(new_match)
                parsed_inst['arg%s' % i] = list(parsed_inst['arg%s' % i])
                parsed_inst['arg%s' % i][new_match.span()[0]: new_match.span()[1]] = list(str(selfcall_outcome))
                parsed_inst['arg%s' % i] = ''.join(parsed_inst['arg%s' % i])      
            '''
        try:
            #print('before call ', parsed_inst)
            return self.COMMANDS[parsed_inst['cmd']](**parsed_inst)
        except KeyError as e:
            return self.default('Invalid command ' + e.__str__(), False)

    def main(self):
        while True:
            instruction = input(self.COMMAND_PROMPT)
            match = self.COMMAND_PATTERN.match(instruction)
            if match:
                cmd_outcome = self.handle_inst(match)
                try:
                    if cmd_outcome[0] == True:
                        print(cmd_outcome[1])
                        break
                except TypeError:
                    print(cmd_outcome)
                except IndexError:
                    print(cmd_outcome)
                else:
                    print(cmd_outcome)
            else:
                self.default('match = ' + match.__str__(), False)

console = Handler()
while True:
    console.main()

