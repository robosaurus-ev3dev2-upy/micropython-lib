import io
import os

def check_output(args, *, stdin=None, stderr=None, shell=False, cwd=None, encoding=None, errors=None, universal_newlines=None, timeout=None, text=None):
    cmd = " ".join(args)
    output = ""

    fp = os.popen(cmd, "r")
    print(fp)
    a = "output"
    while "" != a:
        a = fp.readline()
        output = output + a
    fp.close()

    return output.encode()

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
            r, w = os.pipe()
            self.stdout = io.open(r, "r") # for other Popen to read
            self.outpipe = w
        elif stdout != None:
            self.outpipe = stdout.fileno()
        
        if stdin == PIPE:
            r, w = os.pipe()
            self.stdin = io.open(w, "w") # for other Popen to write
            self.inpipe = r
        elif stdin != None:
            self.inpipe = stdin.fileno()

        pid = os.fork()
        if 0 > pid:
            print("Error fork")
        elif 0 == pid:
            # chold process
            if -1 != self.inpipe:
                os.dup2(self.inpipe, 0)
                os.close(self.inpipe)
            if -1 != self.outpipe:
                os.dup2(self.outpipe, 1)
                os.close(self.outpipe)

            os._exit(os.execvp(args[0], args))
        else:
            # parent process
            if -1 != self.inpipe:
                os.close(self.inpipe)
            if -1 != self.outpipe:
                os.close(self.outpipe)
            self.pid = pid

    def wait(self):
        os.waitpid(self.pid, 0)

PIPE = 0xABCDEFABC
