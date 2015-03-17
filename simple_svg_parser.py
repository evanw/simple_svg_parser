import re
import math
import xml.dom.minidom

# The entry point for this library
def parse(text, handler):
  doc = xml.dom.minidom.parseString(text)
  _Parser(handler).visit(doc)

# Implement this interface and pass it to parse()
class HandlerInterface:
  def metadata(self, data): pass
  def beginPath(self): pass
  def moveTo(self, x, y): pass
  def lineTo(self, x, y): pass
  def curveTo(self, x1, y1, x2, y2, x3, y3): pass
  def closePath(self): pass
  def fill(self, r, g, b, a): pass
  def stroke(self, r, g, b, a, width): pass

# Derivation: http://en.wikipedia.org/wiki/Bezier_spline
_CIRCLE_APPROXIMATION_CONSTANT = 4.0 / 3.0 * (math.sqrt(2) - 1)

# From: http://www.w3.org/TR/SVG11/types.html#ColorKeywords
_color_table = {
  'aliceblue': '#F0F8FF',
  'antiquewhite': '#FAEBD7',
  'aqua': '#00FFFF',
  'aquamarine': '#7FFFD4',
  'azure': '#F0FFFF',
  'beige': '#F5F5DC',
  'bisque': '#FFE4C4',
  'black': '#000000',
  'blanchedalmond': '#FFEBCD',
  'blue': '#0000FF',
  'blueviolet': '#8A2BE2',
  'brown': '#A52A2A',
  'burlywood': '#DEB887',
  'cadetblue': '#5F9EA0',
  'chartreuse': '#7FFF00',
  'chocolate': '#D2691E',
  'coral': '#FF7F50',
  'cornflowerblue': '#6495ED',
  'cornsilk': '#FFF8DC',
  'crimson': '#DC143C',
  'cyan': '#00FFFF',
  'darkblue': '#00008B',
  'darkcyan': '#008B8B',
  'darkgoldenrod': '#B8860B',
  'darkgray': '#A9A9A9',
  'darkgreen': '#006400',
  'darkgrey': '#A9A9A9',
  'darkkhaki': '#BDB76B',
  'darkmagenta': '#8B008B',
  'darkolivegreen': '#556B2F',
  'darkorange': '#FF8C00',
  'darkorchid': '#9932CC',
  'darkred': '#8B0000',
  'darksalmon': '#E9967A',
  'darkseagreen': '#8FBC8F',
  'darkslateblue': '#483D8B',
  'darkslategray': '#2F4F4F',
  'darkslategrey': '#2F4F4F',
  'darkturquoise': '#00CED1',
  'darkviolet': '#9400D3',
  'deeppink': '#FF1493',
  'deepskyblue': '#00BFFF',
  'dimgray': '#696969',
  'dimgrey': '#696969',
  'dodgerblue': '#1E90FF',
  'firebrick': '#B22222',
  'floralwhite': '#FFFAF0',
  'forestgreen': '#228B22',
  'fuchsia': '#FF00FF',
  'gainsboro': '#DCDCDC',
  'ghostwhite': '#F8F8FF',
  'gold': '#FFD700',
  'goldenrod': '#DAA520',
  'gray': '#808080',
  'green': '#008000',
  'greenyellow': '#ADFF2F',
  'grey': '#808080',
  'honeydew': '#F0FFF0',
  'hotpink': '#FF69B4',
  'indianred': '#CD5C5C',
  'indigo': '#4B0082',
  'ivory': '#FFFFF0',
  'khaki': '#F0E68C',
  'lavender': '#E6E6FA',
  'lavenderblush': '#FFF0F5',
  'lawngreen': '#7CFC00',
  'lemonchiffon': '#FFFACD',
  'lightblue': '#ADD8E6',
  'lightcoral': '#F08080',
  'lightcyan': '#E0FFFF',
  'lightgoldenrodyellow': '#FAFAD2',
  'lightgray': '#D3D3D3',
  'lightgreen': '#90EE90',
  'lightgrey': '#D3D3D3',
  'lightpink': '#FFB6C1',
  'lightsalmon': '#FFA07A',
  'lightseagreen': '#20B2AA',
  'lightskyblue': '#87CEFA',
  'lightslategray': '#778899',
  'lightslategrey': '#778899',
  'lightsteelblue': '#B0C4DE',
  'lightyellow': '#FFFFE0',
  'lime': '#00FF00',
  'limegreen': '#32CD32',
  'linen': '#FAF0E6',
  'magenta': '#FF00FF',
  'maroon': '#800000',
  'mediumaquamarine': '#66CDAA',
  'mediumblue': '#0000CD',
  'mediumorchid': '#BA55D3',
  'mediumpurple': '#9370DB',
  'mediumseagreen': '#3CB371',
  'mediumslateblue': '#7B68EE',
  'mediumspringgreen': '#00FA9A',
  'mediumturquoise': '#48D1CC',
  'mediumvioletred': '#C71585',
  'midnightblue': '#191970',
  'mintcream': '#F5FFFA',
  'mistyrose': '#FFE4E1',
  'moccasin': '#FFE4B5',
  'navajowhite': '#FFDEAD',
  'navy': '#000080',
  'oldlace': '#FDF5E6',
  'olive': '#808000',
  'olivedrab': '#6B8E23',
  'orange': '#FFA500',
  'orangered': '#FF4500',
  'orchid': '#DA70D6',
  'palegoldenrod': '#EEE8AA',
  'palegreen': '#98FB98',
  'paleturquoise': '#AFEEEE',
  'palevioletred': '#DB7093',
  'papayawhip': '#FFEFD5',
  'peachpuff': '#FFDAB9',
  'peru': '#CD853F',
  'pink': '#FFC0CB',
  'plum': '#DDA0DD',
  'powderblue': '#B0E0E6',
  'purple': '#800080',
  'red': '#FF0000',
  'rosybrown': '#BC8F8F',
  'royalblue': '#4169E1',
  'saddlebrown': '#8B4513',
  'salmon': '#FA8072',
  'sandybrown': '#F4A460',
  'seagreen': '#2E8B57',
  'seashell': '#FFF5EE',
  'sienna': '#A0522D',
  'silver': '#C0C0C0',
  'skyblue': '#87CEEB',
  'slateblue': '#6A5ACD',
  'slategray': '#708090',
  'slategrey': '#708090',
  'snow': '#FFFAFA',
  'springgreen': '#00FF7F',
  'steelblue': '#4682B4',
  'tan': '#D2B48C',
  'teal': '#008080',
  'thistle': '#D8BFD8',
  'tomato': '#FF6347',
  'turquoise': '#40E0D0',
  'violet': '#EE82EE',
  'wheat': '#F5DEB3',
  'white': '#FFFFFF',
  'whitesmoke': '#F5F5F5',
  'yellow': '#FFFF00',
  'yellowgreen': '#9ACD32',
}

_align_table = {
  'xMinYMin': (0.0, 0.0),
  'xMidYMin': (0.5, 0.0),
  'xMaxYMin': (1.0, 0.0),
  'xMinYMid': (0.0, 0.5),
  'xMidYMid': (0.5, 0.5),
  'xMaxYMid': (1.0, 0.5),
  'xMinYMax': (0.0, 1.0),
  'xMidYMax': (0.5, 1.0),
  'xMaxYMax': (1.0, 1.0),
}

class _Vector:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __add__(self, v):
    return _Vector(self.x + v.x, self.y + v.y)

  def __sub__(self, v):
    return _Vector(self.x - v.x, self.y - v.y)

  def __mul__(self, n):
    return _Vector(self.x * n, self.y * n)

class _Matrix:
  def __init__(self, m00=1, m01=0, m02=0, m10=0, m11=1, m12=0):
    self.m00 = m00
    self.m01 = m01
    self.m02 = m02
    self.m10 = m10
    self.m11 = m11
    self.m12 = m12

  def multiply(self, other):
    return _Matrix(
      self.m00 * other.m00 + self.m01 * other.m10,
      self.m00 * other.m01 + self.m01 * other.m11,
      self.m00 * other.m02 + self.m01 * other.m12 + self.m02,
      self.m10 * other.m00 + self.m11 * other.m10,
      self.m10 * other.m01 + self.m11 * other.m11,
      self.m10 * other.m02 + self.m11 * other.m12 + self.m12)

  def transform(self, v):
    return _Vector(
      self.m00 * v.x + self.m01 * v.y + self.m02,
      self.m10 * v.x + self.m11 * v.y + self.m12)

class _Parser:
  def __init__(self, handler):
    self.matrix = _Matrix()
    self.handler = handler
    self.cursor = _Vector(0, 0)
    self.strokeScale = 1
    self.opacity = 1

  def moveTo(self, p):
    self.cursor = p
    p = self.matrix.transform(p)
    self.handler.moveTo(p.x, p.y)

  def lineTo(self, p):
    self.cursor = p
    p = self.matrix.transform(p)
    self.handler.lineTo(p.x, p.y)

  def quadraticCurveTo(self, p1, p2):
    c1 = self.cursor + (p1 - self.cursor) * (2.0 / 3.0)
    c2 = p2 + (p1 - p2) * (2.0 / 3.0)
    self.cursor = p2
    self.cubicCurveTo(c1, c2, p2)

  def cubicCurveTo(self, p1, p2, p3):
    self.cursor = p3
    p1 = self.matrix.transform(p1)
    p2 = self.matrix.transform(p2)
    p3 = self.matrix.transform(p3)
    self.handler.curveTo(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y)

  def outlineEllipse(self, cx, cy, rx, ry):
    crx = rx * _CIRCLE_APPROXIMATION_CONSTANT
    cry = ry * _CIRCLE_APPROXIMATION_CONSTANT
    self.handler.beginPath()
    self.moveTo(_Vector(cx - rx, cy))
    self.cubicCurveTo(_Vector(cx - rx, cy - cry), _Vector(cx - crx, cy - ry), _Vector(cx, cy - ry))
    self.cubicCurveTo(_Vector(cx + crx, cy - ry), _Vector(cx + rx, cy - cry), _Vector(cx + rx, cy))
    self.cubicCurveTo(_Vector(cx + rx, cy + cry), _Vector(cx + crx, cy + ry), _Vector(cx, cy + ry))
    self.cubicCurveTo(_Vector(cx - crx, cy + ry), _Vector(cx - rx, cy + cry), _Vector(cx - rx, cy))
    self.handler.closePath()

  def outlineRect(self, x, y, w, h):
    self.handler.beginPath()
    self.moveTo(_Vector(x, y))
    self.lineTo(_Vector(x + w, y))
    self.lineTo(_Vector(x + w, y + h))
    self.lineTo(_Vector(x, y + h))
    self.handler.closePath()

  def outlineRoundedRect(self, x, y, w, h, rx, ry):
    rx = min(rx, w * 0.5)
    ry = min(ry, h * 0.5)
    crx = rx * (1 - _CIRCLE_APPROXIMATION_CONSTANT)
    cry = ry * (1 - _CIRCLE_APPROXIMATION_CONSTANT)
    self.handler.beginPath()
    self.moveTo(_Vector(x + rx, y))
    self.lineTo(_Vector(x + w - rx, y))
    self.cubicCurveTo(_Vector(x + w - crx, y), _Vector(x + w, y + cry), _Vector(x + w, y + ry))
    self.lineTo(_Vector(x + w, y + h - ry))
    self.cubicCurveTo(_Vector(x + w, y + h - cry), _Vector(x + w - crx, y + h), _Vector(x + w - rx, y + h))
    self.lineTo(_Vector(x + rx, y + h))
    self.cubicCurveTo(_Vector(x + crx, y + h), _Vector(x, y + h - cry), _Vector(x, y + h - ry))
    self.lineTo(_Vector(x, y + ry))
    self.cubicCurveTo(_Vector(x, y + cry), _Vector(x + crx, y), _Vector(x + rx, y))
    self.handler.closePath()

  def visitPath(self, node, style):
    self.handler.beginPath()
    self._path(_attr(node, 'd'))
    self.fillAndStroke(node, style)

  def visitRect(self, node, style):
    x = _units(_attr(node, 'x'))
    y = _units(_attr(node, 'y'))
    w = _units(_attr(node, 'width'))
    h = _units(_attr(node, 'height'))
    rx = _units(_attr(node, 'rx'))
    ry = _units(_attr(node, 'ry'))
    if rx or ry: self.outlineRoundedRect(x, y, w, h, rx, ry)
    else: self.outlineRect(x, y, w, h)
    self.fillAndStroke(node, style)

  def visitLine(self, node, style):
    x1 = _units(_attr(node, 'x1'))
    y1 = _units(_attr(node, 'y1'))
    x2 = _units(_attr(node, 'x2'))
    y2 = _units(_attr(node, 'y2'))
    self.handler.beginPath()
    self.moveTo(_Vector(x1, y1))
    self.lineTo(_Vector(x2, y2))
    self.fillAndStroke(node, style)

  def visitCircle(self, node, style):
    x = _units(_attr(node, 'cx'))
    y = _units(_attr(node, 'cy'))
    r = _units(_attr(node, 'r'))
    self.outlineEllipse(x, y, r, r)
    self.fillAndStroke(node, style)

  def visitEllipse(self, node, style):
    x = _units(_attr(node, 'cx'))
    y = _units(_attr(node, 'cy'))
    rx = _units(_attr(node, 'rx'))
    ry = _units(_attr(node, 'ry'))
    self.outlineEllipse(x, y, rx, ry)
    self.fillAndStroke(node, style)

  def visitPolyline(self, node, style):
    self.handler.beginPath()
    for i, point in enumerate(_points(_attr(node, 'points'))):
      if i: self.lineTo(point)
      else: self.moveTo(point)
    self.fillAndStroke(node, style)

  def visitPolygon(self, node, style):
    self.handler.beginPath()
    for i, point in enumerate(_points(_attr(node, 'points'))):
      if i: self.lineTo(point)
      else: self.moveTo(point)
    self.handler.closePath()
    self.fillAndStroke(node, style)

  def fillAndStroke(self, node, style):
    fill = _attr(node, 'fill') or style.get('fill', 'black')
    stroke = _attr(node, 'stroke') or style.get('stroke', 'none')
    strokeWidth = _attr(node, 'stroke-width') or style.get('stroke-width', '1')

    if fill != 'none':
      c = _color(fill)
      self.handler.fill(c[0], c[1], c[2], c[3] * self.opacity)

    if stroke != 'none':
      c = _color(stroke)
      self.handler.stroke(c[0], c[1], c[2], c[3] * self.opacity, self.strokeScale * _units(strokeWidth))

  def visitViewbox(self, node, data):
    match = re.match(r'^[\s,]*([^\s,]+)[\s,]+([^\s,]+)[\s,]+([^\s,]+)[\s,]+([^\s,]+)[\s,]*$', _attr(node, 'viewBox'))
    if match:
      aspect = _attr(node, 'preserveAspectRatio') or 'xMidYMid'
      x, y, w, h = map(_units, match.groups())
      data.setdefault('width', w)
      data.setdefault('height', h)
      sx = data['width'] / w
      sy = data['height'] / h
      if aspect in _align_table:
        sx = sy = min(sx, sy)
        ax, ay = _align_table[aspect]
        x += (w - data['width'] / sx) * ax
        y += (h - data['height'] / sy) * ay
      self.matrix = _Matrix(sx, 0, -x * sx, 0, sy, -y * sy)
      self.strokeScale = math.sqrt(sx * sy)

  def visitSVG(self, node):
    data = {}
    if _attr(node, 'width'): data['width'] = _units(_attr(node, 'width'))
    if _attr(node, 'height'): data['height'] = _units(_attr(node, 'height'))
    if _attr(node, 'viewBox'): self.visitViewbox(node, data)
    if data: self.handler.metadata(data)

  def visit(self, node):
    old_matrix = self.matrix
    old_opacity = self.opacity

    style = _attr(node, 'style') or ''
    style = dict(tuple(y.strip() for y in x.split(':')) for x in style.split(';') if x)
    self.opacity *= float(_attr(node, 'opacity') or style.get('opacity', '1'))

    if _attr(node, 'transform'):
      self.matrix = self.matrix.multiply(_matrix(_attr(node, 'transform')))

    if node.nodeType == node.ELEMENT_NODE:
      if node.tagName == 'path': self.visitPath(node, style)
      elif node.tagName == 'rect': self.visitRect(node, style)
      elif node.tagName == 'line': self.visitLine(node, style)
      elif node.tagName == 'circle': self.visitCircle(node, style)
      elif node.tagName == 'ellipse': self.visitEllipse(node, style)
      elif node.tagName == 'polyline': self.visitPolyline(node, style)
      elif node.tagName == 'polygon': self.visitPolygon(node, style)
      elif node.tagName == 'svg': self.visitSVG(node)

    for child in node.childNodes:
      self.visit(child)

    self.matrix = old_matrix
    self.opacity = old_opacity

  def _path(self, data):
    def next():
      token = tokens[i[0]]
      i[0] += 1
      return token

    def nextX():
      return float(next()) + (cursor.x if isRelative else 0)

    def nextY():
      return float(next()) + (cursor.y if isRelative else 0)

    def nextXY():
      return _Vector(nextX(), nextY())

    def nextIsNumber():
      return i[0] < len(tokens) and re.match(r'.*\d.*', tokens[i[0]])

    tokens = _tokenize(data)
    cursor = _Vector(0, 0)
    delta = None
    i = [0] # Python 2.7 doesn't have the nonlocal keyword

    while i[0] < len(tokens):
      command = next()
      isRelative = command == command.lower()
      do_while = True

      if command in 'Mm':
        cursor = nextXY()
        self.moveTo(cursor)
        while nextIsNumber():
          cursor = nextXY()
          self.lineTo(cursor)
        delta = None

      elif command in 'Ll':
        while do_while:
          cursor = nextXY()
          self.lineTo(cursor)
          do_while = nextIsNumber()
        delta = None

      elif command in 'Hh':
        while do_while:
          cursor = _Vector(nextX(), cursor.y)
          self.lineTo(cursor)
          do_while = nextIsNumber()
        delta = None

      elif command in 'Vv':
        while do_while:
          cursor = _Vector(cursor.x, nextY())
          self.lineTo(cursor)
          do_while = nextIsNumber()
        delta = None

      elif command in 'Qq':
        while do_while:
          cp1 = nextXY()
          cursor = nextXY()
          delta = cursor - cp1
          self.quadraticCurveTo(cp1, cursor)
          do_while = nextIsNumber()

      elif command in 'Tt':
        while do_while:
          cp2 = cursor + delta if delta else cursor
          cursor = nextXY()
          delta = cursor - cp2
          self.quadraticCurveTo(cp2, cursor)
          do_while = nextIsNumber()

      elif command in 'Cc':
        while do_while:
          cp3 = nextXY()
          cp4 = nextXY()
          cursor = nextXY()
          delta = cursor - cp4
          self.cubicCurveTo(cp3, cp4, cursor)
          do_while = nextIsNumber()

      elif command in 'Ss':
        while do_while:
          cp5 = cursor + delta if delta else cursor
          cp6 = nextXY()
          cursor = nextXY()
          delta = cursor - cp6
          self.cubicCurveTo(cp5, cp6, cursor)
          do_while = nextIsNumber()

      elif command in 'Zz':
        self.handler.closePath()
        cursor = _Vector(0, 0)
        delta = None

      else:
        raise Exception('Unsupported command syntax: %s' % repr(command))

def _color(text):
  text = text.strip()
  text = _color_table.get(text, text)

  if re.match(r'^#[A-Fa-f0-9]{6}$', text):
    value = int(text[1:], 16)
    return (value >> 16 & 255, value >> 8 & 255, value & 255, 1.0)

  if re.match(r'^#[A-Fa-f0-9]{3}$', text):
    value = int(text[1:], 16)
    return ((value >> 8 & 15) * 0x11, (value >> 4 & 15) * 0x11, (value & 15) * 0x11, 1.0)

  match = re.match(r'^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$', text)
  if match:
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)), 1.0)

  match = re.match(r'^rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+(?:\.\d+)?|\.\d+)\s*\)$', text)
  if match:
    return (int(match.group(1)), int(match.group(2)), int(match.group(3)), float(match.group(4)))

  raise Exception('Unsupported color syntax: %s' % repr(text))

def _units(text):
  return float(text.replace('px', '')) if text else 0.0 # Only handle pixels for now

def _attr(node, name):
  return node.attributes.get(name).value if node.attributes and node.attributes.get(name) else None

def _tokenize(text):
  tokens = [x.strip() for x in re.split(r'([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?|[+-]?\.\d+(?:[eE][+-]?\d+)?|\b\s+\b|\w(?=\w))', text)]
  tokens = [x for x in tokens if x not in ['', ',']]
  return tokens

def _points(text):
  tokens = _tokenize(text)
  return [_Vector(float(p[0]), float(p[1])) for p in zip(tokens[::2], tokens[1::2])]

def _matrix(text):
  match = re.match(r'matrix\s*\(\s*([^,\s]*)[,\s]+([^,\s]*)[,\s]+([^,\s]*)[,\s]+([^,\s]*)[,\s]+([^,\s]*)[,\s]+([^,\s]*)\s*\)', text)
  if match:
    numbers = map(float, list(match.groups()))
    return _Matrix(numbers[0], numbers[2], numbers[4], numbers[1], numbers[3], numbers[5])

  match = re.match(r'translate\s*\(\s*([^,\s]*)[,\s]+([^,\s]*)\s*\)', text)
  if match:
    numbers = map(float, list(match.groups()))
    return _Matrix(1, 0, numbers[0], 0, 1, numbers[1])

  raise Exception('Unsupported transform syntax: %s' % repr(text))
