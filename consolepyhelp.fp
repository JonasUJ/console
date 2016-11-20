# Description of every command in console.py

- help
{
help: Shows this text
exit: Exits the console
say: Prints the first argument (e.g "say "Hello World!"" will print "Hello World!")
cal: Calculates the first argument (e.g "cal "4 + 2 * 2" will print "8")
set: Sets a keyword to reference a value (e.g "set kw v" will set "kw" to "v")
get: Gets the value of a keyword (e.g "get kw" will get the value og "kw")
create: Creates a file at the given path. You can do this three different ways, "create file.txt c:/", "create c:/file.txt" or "create file.txt". the latter will create the file at standard_dir which is set with "set standard_dir dir"
open: Opens a file at the given path, if only the filename is given, it will try to look for the file at standard_dir
}