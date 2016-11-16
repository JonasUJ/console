import re, sys, os, fp

NAME_OF_FILE = os.path.basename(sys.argv[0])
DIRECTORY_OF_FILE = sys.argv[0].rstrip(NAME_OF_FILE)

class Handler:

    def __init__(self):
        self.MAX_CMD_ARGS = 10 # There'll be one less, since it counts the command as one
        self.COMMAND_PATTERN = re.compile(r'([a-zA-Z]+)' + r''.join([r'(?: (?P<quote%s>\")?((?(quote%s)(?:\\"|[a-zA-Z0-9_.+*/!#&/()=?~<> -])+|[a-zA-Z0-9_.+*/!#&/()=?~<>"-]+))(?(quote%s)"))?' % (x, x, x) for x in range(self.MAX_CMD_ARGS)]))
        self.COMMAND_PROMPT = "\n~ "
        self.COMMANDS = {'exit':self.do_exit, 'quit':self.do_exit, 'cal':self.do_cal, 'say':self.do_say, 'help':self.do_help}

    def default(self, *args):
        print("Error,", *args)
        return "reported error"

    def do_help(self, **kwargs):
        help_dict = fp.parse_file(DIRECTORY_OF_FILE + 'consolepyhelp.txt')
        for cmd in help_dict['help'].keys():
            print('%s - %s' % (cmd, help_dict['help'][cmd]))
        return ""
    
    def do_exit(self, **kwargs):
        sys.exit(1)
        return "exited (unless you're seeing this')"

    def do_say(self, **kwargs):
        return str(kwargs['arg1'])
 
    def do_cal(self, **kwargs):
        try:
            result = eval(kwargs['arg1'])
            return result
        except NameError as e:
            self.default(e)
            return e
        except ZeroDivisionError as e:
            self.default(e)
            return e
        except TypeError as e:
            return e

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
        parsed_inst = self.parse_groups(match.groups())
        for i in range(1, len(parsed_inst.values()) - 1):
            arg = parsed_inst['arg%s' % i]
            if arg:
                if arg.startswith('~'):
                    match = self.COMMAND_PATTERN.match(arg.lstrip('~'))
                    selfcall_outcome = self.handle_inst(match)
                    parsed_inst['arg%s' % i] = selfcall_outcome
        try:
            return self.COMMANDS[parsed_inst['cmd']](**parsed_inst)
        except KeyError as e:
            self.default('Invalid command', e)
            return None

    def main(self):
        while True:
            instruction = input(self.COMMAND_PROMPT)
            match = self.COMMAND_PATTERN.match(instruction)
            if match:
                print(self.handle_inst(match))
                #parsed_inst = self.parse_groups(match.groups())
                #handled_inst = self.handle_inst(parsed_inst)
                #try:
                #    outcome = self.COMMANDS[parsed_inst['cmd']](**parsed_inst)
                #except KeyError as e:
                #    self.default('Invalid command', e)
            else:
                self.default("match =", match)

console = Handler()
console.main()
