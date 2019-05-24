import re
from Automata import Automata
from anytree.dotexport import DotExporter


def nodenamefunc(node):
   return '%s:%s' % (node.name, node.nodeId)

def nodeattrfunc(node):
   return 'label="%s"' % (node.name)

er="(ab|r)*123|(otro)a*"
test="([a-z]*|[0-9]+)|(0*1+)"
#er = "(1|[a-z])|z?y"
automata = Automata(er)
DotExporter(automata.raiz, nodenamefunc=nodenamefunc, nodeattrfunc=nodeattrfunc).to_picture("arbol.png")
automata.dibujarAFD()

print(automata.er)
print(automata.tokens)