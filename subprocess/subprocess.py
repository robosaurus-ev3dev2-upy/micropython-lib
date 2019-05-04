import ffilib
import array
import sys
import io
import os

libc = ffilib.libc()

popen = libc.func("P", "popen", "ss")
fgetc = libc.func("i", "fgetc", "P")
feof = libc.func("i", "feof", "P")
pclose = libc.func("v", "pclose", "P")

fork = libc.func("i", "fork", "v")
dup2 = libc.func("i", "dup2", "ii")
waitpid = libc.func("i", "waitpid", "iPi")
execv = libc.func("i", "execv", "sP")
system = libc.func("i", "system", "s")

print(sys.path)
_sub = ffilib.open(sys.path[1] + "/_subprocess")
run_cmd_in_fork = _sub.func("i", "run_cmd_in_fork", "sii")

def check_output(args, *, stdin=None, stderr=None, shell=False, cwd=None, encoding=None, errors=None, universal_newlines=None, timeout=None, text=None):
    cmd = " ".join(args)
    output = []

    fp = popen(cmd, "r")
    while 0 == feof(fp):
        a = fgetc(fp)
        output.append(a)
    pclose(fp)

    del output[-1] # the last one is EOF, remove it

    # Join the ASCII chars to string
    output = "".join(map(chr, output)).encode()
    return output

class Popen:
    def __init__(self, args, bufsize=-1, executable=None, stdin=None, stdout=None, stderr=None, preexec_fn=None, close_fds=True, shell=False, cwd=None, env=None, universal_newlines=None, startupinfo=None, creationflags=0, restore_signals=True, start_new_session=False, pass_fds=(), *, encoding=None, errors=None, text=None):
        self.args = args
        # stdin/stdout are for other Popen to use
        self.stdin = -1
        self.stdout = -1
        self.returnCode = 0
        self.pid = 0

        # inpipe/outpipe are for this Popen to use internally
        self.inpipe = -1
        self.outpipe = -1

        if stdout == PIPE:
            pipe = os.pipe()
            self.stdout = pipe[0]
            self.outpipe = pipe[1]
        elif stdout != None:
            if io.TextIOWrapper == type(stdout):
                self.outpipe = stdout.fileno()
            else:
                self.outpipe = stdout
        
        if stdin == PIPE:
            pipe = os.pipe()
            self.stdin = pipe[1]
            self.inpipe = pipe[0]
        elif stdin != None:
            if io.TextIOWrapper == type(stdin):
                self.inpipe = stdin.fileno()
            else:
                self.inpipe = stdin

        self.pid = run_cmd_in_fork(" ".join(args), self.inpipe, self.outpipe)

    def wait(self):
        waitpid(self.pid, 0, 0)

PIPE = 0xABCDEFABC
