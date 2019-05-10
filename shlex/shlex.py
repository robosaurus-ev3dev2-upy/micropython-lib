
def split(arg):
    args = arg.split(" ")
    for i in range(len(args)):
        args[i] = args[i].strip('"')
    return args

def quote(arg):
    return arg
