import re, sys, os, fp

class Handler:

    def __init__(self):
        self.NAME_OF_FILE = os.path.basename(sys.argv[0])
        self.DIRECTORY_OF_FILE = sys.argv[0].rstrip(self.NAME_OF_FILE)
        self.MAX_CMD_ARGS = 10 # There'll be one less, since it counts the command as one
        self.COMMAND_PATTERN_UNCOMPILED = r'([a-zA-Z]+)' + r''.join([r'(?: (?P<quote%s>\")?((?(quote%s)(?:\\"|[a-zA-Z0-9_.+*/!#&/()=?~<> -])+|[a-zA-Z0-9_.+*/!#&/()=?~<>"-]+))(?(quote%s)"))?' % (x, x, x) for x in range(self.MAX_CMD_ARGS)])
        self.COMMAND_PATTERN = re.compile(self.COMMAND_PATTERN_UNCOMPILED)
        self.EMBEDDED_COMMAND_PATTERN = re.compile('~' + self.COMMAND_PATTERN_UNCOMPILED + '~')
        self.COMMAND_PROMPT = "\n~ "
        self.COMMANDS = {'exit':self.do_exit, 'quit':self.do_exit, 'cal':self.do_cal, 'say':self.do_say, 'help':self.do_help}

    def default(self, restart, error):
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
        sys.exit(1)
        return "exited (unless you're seeing this')"

    def do_say(self, **kwargs):
        return str(kwargs['arg1'])
 
    def do_cal(self, **kwargs):
        try:
            result = eval(kwargs['arg1'])
            return float(result)
        except NameError as e:
            return self.default(False, e)
        except ZeroDivisionError as e:
            return self.default(False, e)
        except SyntaxError as e:
            return self.default(False, 'Invalid syntax')
        #except TypeError as e:
        #    return e

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
        except AttributeError:
            return self.default(True, 'Invalid imbedded command')
        for i in range(1, len(parsed_inst.values()) - 1):
            arg = parsed_inst['arg%s' % i]
            if arg:
                if '~' in arg:
                    match = self.EMBEDDED_COMMAND_PATTERN.search(arg)
                    selfcall_outcome = self.handle_inst(match)
                    quote = arg[arg.index('~') - 1] == '"'
                    try:
                        parsed_inst['arg%s' % i] = list(parsed_inst['arg%s' % i])
                        parsed_inst['arg%s' % i][match.span()[0] - quote: match.span()[1] + quote] = str(selfcall_outcome).split()
                        parsed_inst['arg%s' % i] = ''.join(parsed_inst['arg%s' % i])
                    except AttributeError:
                        return self.default(True, 'Invalid imbedded command')
        try:
            return self.COMMANDS[parsed_inst['cmd']](**parsed_inst)
        except KeyError as e:
            return self.default('Invalid command', e)

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
                self.default("match =", match)
console = Handler()
while True:
    console.main()
