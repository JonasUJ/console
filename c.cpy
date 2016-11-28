func create c.incr "set <get args 0> <cal <get args 1>+<get <get args 0>>>"
func create c.append "set <get args 0> <int <cal <len <get <get args 0>>>-1>> <get <get args 0> <int <cal <len <get <get args 0>>>-1>>>;<get args 1>"
