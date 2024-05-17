sleeping-functions.py is a script that forms two lists:
1. list of void sfunctions that may sleep in ./res_void.txt;
2. list of non-void functions that may sleep in ./res_not_void.txt.
That lists have format call(func) || call(func) || to be pasted in pointcuts in sleep/common.aspect file.

Parameters that should be changed in .py file: (FIXME)
- build_base_path - absolute path to a build_base on current machine.
- path_in_build_base - path to a build_base on machine where it was built
- funcs - a dictionary with basic sleeping functions and paths to files where they where defined. Also their prototypes should be added to res_v ans res_nv.
- depth - number of layers of sleeping functions added in lists. For example: 1 - all functions that call basic sleeping functions. 2 - all functions that call basic sleeping functions and functions that call them. 