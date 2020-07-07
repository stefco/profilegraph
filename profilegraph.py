"IPython magic for cProfile graphs w gprof2dot and graphviz in Jupyter/iterm."

__version__ = '0.2.0'

import os
import re
import sys
from base64 import b64encode
from subprocess import check_output
from tempfile import NamedTemporaryFile
import cProfile
import gprof2dot


def graphviz_plot(imgfile, fmt):
    with open(imgfile, 'rb') as f:
        return check_output(['dot', '-Gbgcolor=transparent', '-T%s'%fmt],
                            input=f.read())


def imgcat(img, wb):
    tmux = os.environ['TERM'].startswith('screen')
    # needed for tmux
    wb.write(b'\x1bPtmux;\x1b\x1b]' if tmux else b'\x1b]')
    wb.write(b'1337;File=')
    wb.write(b'name=%s;'%b64encode(b'ProfileResults.png'))
    wb.write(b'size=%d;'%len(img))
    wb.write(b'inline=1:')
    wb.write(b64encode(img))
    wb.write(b'\x07\x1b\\' if tmux else b'\x07')
    wb.write(b'\n')


def profilegraph(line, cell=None):
    line = line if cell is None else cell
    tmp = NamedTemporaryFile(suffix='.pstats', mode='w', delete=False)
    try:
        tmp.close()
        print("Profiling (output will be here)... ", end='')
        cProfile.run(statement=line, filename=tmp.name)
        print("done.\nMaking dotfile... ", end='')
        dtmp = re.sub(".pstats$", ".dot", tmp.name)
        try:
            gprof2dot.main(['-f', 'pstats', '-o', dtmp, tmp.name])
            print("done.\nMaking image... ", end='')
            if sys.stdout.isatty():
                if not any('iterm' in e.lower() for e in os.environ):
                    raise RuntimeError("TTY output detected, but no iTerm "
                                       "support detected; must run this in a "
                                       "Jupyter notebook OR a python session "
                                       "in iTerm.")
                img = graphviz_plot(dtmp, 'png')
                print("done.\nDisplaying...")
                return imgcat(img, getattr(sys.stdout, 'buffer', sys.stdout))
            img = graphviz_plot(dtmp, 'svg').decode()
            print("done.\nDisplaying...")
            from IPython.display import HTML
            return HTML(img)
        finally:
            if os.path.isfile(dtmp):
                os.unlink(dtmp)
    finally:
        if os.path.isfile(tmp.name):
            os.unlink(tmp.name)


def load_ipython_extension(ipython):
    from IPython.core.magic import register_line_magic, register_cell_magic

    register_line_magic(profilegraph)
    register_cell_magic(profilegraph)
