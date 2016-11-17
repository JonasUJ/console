


# console
A tool thats shitty and buggy, but i'm still creating it.

command syntax = CMD ARG1 "ARG 2" "ARG \"3\""

type "help" for a list of commands

embed commands in commands by enclosing the command in ~'s (tildas) like this: cmd "~cmd arg~"
the command will then run, if it returns anything it gets put in ~cmd arg~'s place
e.g 'say "~cal 1+1~"' will become 'say 2' which will print 2

# fp
A file parser i created just for the purpose of reading consolepyhelp.txt

fp's purpose is only to read files, it therefore can't write them and you'll have to do that yourself
fp.parse_file(filepath) returns a dict with headers as keys and values as a dict of contents corrosponding to the header.

the syntax:
lines that start with # are comments
lines that start with '- ' (dash space) are headers, these lines must be followed be content
content can stretch over multiple lines, it starts with { (start curly bracer) and then it reads the following lines as key-value pairs, until it sees a } (end curly bracer)
key-value pair is some text followed by ': ' (colon space) followed by some more text

an example:

file.txt-------------------------------

\# Here i've made a comment

\- header
\{key: value}

\- another header
\{
foo: bar
hello: world
}
---------------------------------------

would return
\{'header': {'key': 'value'}, 'another header':{'foo': 'bar', 'hello': 'world'}}

