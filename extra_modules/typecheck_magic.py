"""
Add mypy type-checking cell magic to jupyter/ipython.
Save this script to your ipython profile's startup directory.
IPython's directories can be found via `ipython locate [profile]` to find the current ipython directory and ipython profile directory, respectively.
For example, this file could exist on a path like this on mac:
/Users/yourusername/.ipython/profile_default/startup/typecheck.py
where /Users/yourusername/.ipython/profile_default/ is the ipython directory for
the default profile.
The line magic is called "typecheck" to avoid namespace conflict with the mypy
package.
"""
from IPython.core.magic import register_cell_magic, register_line_magic

@register_cell_magic
def typecheck(line, cell):
    """
    Run the following cell though mypy.
    Any parameters that would normally be passed to the mypy cli
    can be passed on the first line, with the exception of the
    -c flag we use to pass the code from the cell we want to execute
     i.e.
    %%typecheck --ignore-missing-imports
    ...
    ...
    ...
    mypy stdout and stderr will print prior to output of cell. If there are no conflicts,
    nothing will be printed by mypy.
    """

    from IPython import get_ipython
    from mypy import api

    if not hasattr(typecheck, '_context'):
        typecheck_clear(None)

    args = line.split()
    valid_cmds = ['run']

    cmds = []

    for ii, arg in enumerate(args):
        if arg == '--':
            ii += 1

        if arg not in valid_cmds:
            line_opts = args[ii:]
            break

        cmds.append(arg)
    else:
        line_opts = []

    # Turn commands into flags
    run = 'run' in cmds

    if line_opts and line_opts[0] == 'report':
        line_opts.pop(0)
        report = True

    # inserting a newline at the beginning of the cell
    # ensures mypy's output matches the the line
    # numbers in jupyter

    # For now, fake the context until I can figure out how to properly
    # include the inter-cell contexts
    cell_original = cell
    cell = '\n'.join([''] + typecheck._context + [cell])

    mypy_result = api.run(['-c', cell] + line_opts)

    if mypy_result[0]:  # print mypy stdout
        print(mypy_result[0])

    if mypy_result[1]:  # print mypy stderr
        print(mypy_result[1])

    no_issues = not (mypy_result[0] or mypy_result[1])

    if no_issues and not run:
        print("No type issues")

    if run:
        shell = get_ipython()
        shell.run_cell(cell_original)

    if no_issues and run:
        typecheck._context.extend(cell_original.split('\n'))


@register_line_magic
def typecheck_clear(line):
    typecheck._context = ['from typing import *']

