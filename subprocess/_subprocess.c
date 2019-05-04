#include <stdio.h>
#include <unistd.h>

#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <fcntl.h>

#ifdef AS_UPY_MODULE
#include "py/nlr.h"
#include "py/obj.h"
#include "py/qstr.h"
#include "py/runtime.h"
#include "py/binary.h"
#endif

static int _fork_w_args(char *args[], int inpipe, int outpipe) {
    int rvalue = -1;

    pid_t pid = fork();
    if (0 > pid) {
        fprintf(stderr, "Failed to fork\n");
    } else if (0 == pid) {
        // child
        if (0 < inpipe) {
            (void)dup2(inpipe, 0);
        }
        if (0 < outpipe) {
            (void)dup2(outpipe, 1);
        }
        int ret = execv((const char *)args[0], (char * const*)args);
        exit(ret);
    } else {
        // This (parent) process
        if (0 < inpipe) {
            close(inpipe);
        }
        if (0 < outpipe) {
            close(outpipe);
        }
        rvalue = pid;
    }

    return rvalue;
}

int run_cmd_in_fork(char *cmd, int ifd, int ofd) {
    char *args[100] = {0};
    int nargs = 0;

    args[0] = cmd;

    char *p = cmd;
    while ('\0' != *p) {
        if (' ' == *p) {
            nargs++;
            args[nargs] = p + 1;
            *p = '\0';
        }
        p++;
    }
    return _fork_w_args(args, ifd, ofd);
}

#ifdef AS_UPY_MODULE
STATIC mp_obj_t _fork(mp_obj_t arg, mp_obj_t inpipe, mp_obj_t outpipe) {
    mp_obj_t rvalue = mp_const_none;
    size_t nargs = 0;
    mp_obj_t *arglist = NULL;
    int ifd = -1, ofd = -1;

    if (inpipe != mp_const_none) {
        ifd = mp_obj_get_int(inpipe);
    }
    if (outpipe != mp_const_none) {
        ofd = mp_obj_get_int(outpipe);
    }

    mp_obj_list_get(arg, &nargs, &arglist);
    char *args[nargs + 1];
    for (int i = 0; i < nargs; i++) {
        args[i] = (char *)mp_obj_str_get_str(arglist[i]);
    }
    args[nargs] = NULL;
    //fprintf(stderr, "%s %s\n", __FUNCTION__, args[0]);
    rvalue = _fork_w_args(args, ifd, ofd);
    
on_err:
    return rvalue;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(_fork_obj, _fork);

mp_obj_module_t *init__subprocess() {
    printf("%s\n", __FUNCTION__);
    qstr name = qstr_from_str("_subprocess");
    mp_obj_t m = mp_obj_new_module(name);
    //mp_store_attr(m, qstr_from_str("check_output"), (mp_obj_t)&check_output_obj);
    mp_store_attr(m, qstr_from_str("fork"), (mp_obj_t)&_fork_obj);
    //mp_store_attr(m, qstr_from_str("waitpid"), (mp_obj_t)&_waitpid_obj);
    mp_store_name(name, m);

    return m;
}
#endif

