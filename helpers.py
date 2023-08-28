# -*- coding: utf-8 -*-
"""
@author: jorgehuck@gmail.com
"""

def readFile( _file, _encoding = "utf-8-sig" ):
  """
  Lee un archivo y devuelve su contenido.
  """
  f = open( _file, encoding = _encoding )
  text = f.read()
  f.close()
  return text