import re, sys, os, fp

NAME_OF_FILE = os.path.basename(sys.argv[0])
DIRECTORY_OF_FILE = sys.argv[0].rstrip(NAME_OF_FILE)

class Handler:

    def __init__(self):
        self.MAX_CMD_ARGS = 10 # There'll be one less
        self.COMMAND_PATTERN = re.compile(r'([a-zA-Z]+)' + r''.join([r'(?: (?P<quote%s>\")?((?(quote%s)[a-zA-Z0-9_.+*/!#&/()=?~<> -]+|[a-zA-Z0-9_.+*/!#&/()=?~<>-]+))(?(quote%s)"))?' % (x, x, x) for x in range(self.MAX_CMD_ARGS)]))
        self.COMMAND_PROMPT = "\n~ "
        self.COMMANDS = {'exit':self.do_exit, 'cal':self.do_cal, 'say':self.do_say, 'help':self.do_help}

    def default(self, *args):
        print("Error,", *args)

    def do_help(self, **kwargs):
        help_dict = fp.parse_file(DIRECTORY_OF_FILE + 'consolepyhelp.txt')
        for cmd in help_dict['help'].keys():
            print('%s - %s' % (cmd, help_dict['help'][cmd]))
    
    def do_exit(self, **kwargs):
        sys.exit(1)

    def do_say(self, **kwargs):
        print(kwargs['arg1'])
 
    def do_cal(self, **kwargs):
        try:
            print(eval(kwargs['arg1']))
        except Exception as e:
            self.default(e)

    def parse_groups(self, groups):
        result = [('cmd', groups[0])]
        result.extend([('arg%s' % str(int((x / 2))), groups[x]) for x in range(2, self.MAX_CMD_ARGS * 2, 2)])
        return dict(result)

    def main(self):
        while True:
            instruction = input(console.COMMAND_PROMPT)
            match = console.COMMAND_PATTERN.match(instruction)
            if match:
                parsed_inst = self.parse_groups(match.groups())
                try:
                    self.COMMANDS[parsed_inst['cmd']](**parsed_inst)
                except KeyError as e:
                    self.default('Invalid command', e)
            else:
                self.default("match =", match)

console = Handler()
console.main()
