"IPython line magic showing cProfile SVG graphs using gprof2dot and graphviz."

__version__ = '0.1'

import os
import re
from subprocess import check_output
from tempfile import NamedTemporaryFile
from pathlib import Path
from IPython.display import HTML
from IPython.core.magic import register_line_magic
import cProfile
import gprof2dot


def profilegraph(line):
    tmp = NamedTemporaryFile(suffix='.pstats', mode='w', delete=False)
    try:
        tmp.close()
        cProfile.run(statement=line, filename=tmp.name)
        dtmp = re.sub(".pstats$", ".dot", tmp.name)
        try:
            gprof2dot.main(['-f', 'pstats', '-o', dtmp, tmp.name])
            return HTML(check_output(['dot', '-Tsvg'],
                                     input=Path(dtmp).read_bytes()).decode())
        finally:
            if os.path.isfile(dtmp):
                os.unlink(dtmp)
    finally:
        if os.path.isfile(tmp.name):
            os.unlink(tmp.name)


def load_ipython_extension(ipython):
    register_line_magic(profilegraph)
