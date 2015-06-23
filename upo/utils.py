# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# Copyright 2015 Marco Guazzone (marco.guazzone@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import importlib
import inspect
import sys


def raise_undefined_method():
    fileName = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print('[ERROR] Method not implemented: %s at line %s of %s' % (method, line, fileName))
    sys.exit(1)


def import_lib(lib):
    """
    Dynamically import a library symbol (e.g., a class, a function) whose fully qualified name is given as argument.
    """
    #-- Alternative #1
    #parts = lib.split('.')
    #module = ".".join(parts[:-1])
    #m = importlib.__import__(module)
    #for comp in parts[1:]:
    #    m = getattr(m, comp)
    #return m
    #-- Alternative #2
    # Extracts the symbol name 
    d = lib.rfind(".")
    lib_name = lib[d+1:len(lib)]
    # Import the module
    #module = importlib.__import__(sym[0:d], globals(), locals(), [lib_name])
    module = importlib.import_module(lib[0:d])
    return getattr(module, lib_name)
