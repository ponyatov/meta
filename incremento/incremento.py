# \ <section:imports>
import os
import sys
import re
# / <section:imports>
# \ <section:executable graph object>
class Object: pass
# / <section:executable graph object>
# \ <section:primitives>
class Primitive(Object): pass
class Name(Primitive): pass
class String(Primitive): pass
class Number(Primitive): pass
class Integer(Number): pass
class Hex(Integer): pass
# / <section:primitives>
