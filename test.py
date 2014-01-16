import simple_svg_parser

class Handler:
  def __init__(self):
    self.lines = []

  def metadata(self, data):
    self.lines += [
      'var canvas = document.getElementById("canvas");',
      'var context = canvas.getContext("2d");',
      'var width = {0};'.format(data.get('width', 0)),
      'var height = {0};'.format(data.get('height', 0)),
      'var dpr = window.devicePixelRatio || 1;',
      'canvas.width = dpr * width;',
      'canvas.height = dpr * height;',
      'canvas.style.width = width + "px";',
      'canvas.style.height = height + "px";',
      'context.scale(dpr, dpr);',
    ]

  def beginPath(self):
    self.lines += ['context.beginPath();']

  def moveTo(self, x, y):
    self.lines += ['context.moveTo({0}, {1});'.format(x, y)]

  def lineTo(self, x, y):
    self.lines += ['context.lineTo({0}, {1});'.format(x, y)]

  def curveTo(self, x1, y1, x2, y2, x3, y3):
    self.lines += ['context.bezierCurveTo({0}, {1}, {2}, {3}, {4}, {5});'.format(x1, y1, x2, y2, x3, y3)]

  def closePath(self):
    self.lines += ['context.closePath();']

  def fill(self, r, g, b, a):
    self.lines += [
      'context.fillStyle = "rgba({0}, {1}, {2}, {3})";'.format(r, g, b, a),
      'context.fill();',
    ]

  def stroke(self, r, g, b, a, width):
    self.lines += [
      'context.lineWidth = {0};'.format(width),
      'context.strokeStyle = "rgba({0}, {1}, {2}, {3})";'.format(r, g, b, a),
      'context.stroke();',
    ]

svg = '''
<svg xmlns="http://www.w3.org/2000/svg" width="500px" height="500px">
  <rect x="0" y="0" width="500" height="500" fill="#EEEEEE"/>

  <rect x="10" y="10" width="50" height="50" rx="10" ry="200" fill="red" stroke="black" stroke-width="4"/>
  <circle cx="95" cy="35" r="25" fill="red" stroke="black" stroke-width="4"/>
  <ellipse cx="95" cy="95" rx="25" ry="15" fill="red" stroke="black" stroke-width="4"/>
  <polygon points="130 70 180 70 155 120" fill="red" stroke="black" stroke-width="4"/>
  <polyline points="130 10 180 10 155 60" fill="red" stroke="black" stroke-width="4"/>
  <path d="M 190 10 C 215 10 240 10 240 35 Q 215 35 215 60" fill="red" stroke="black" stroke-width="4"/>

  <rect transform="matrix(0 1 -1 0 400 0)" x="10" y="10" width="50" height="50" rx="10" ry="200" fill="green" stroke="black" stroke-width="4"/>
  <circle transform="matrix(0 1 -1 0 400 0)" cx="95" cy="35" r="25" fill="green" stroke="black" stroke-width="4"/>
  <ellipse transform="matrix(0 1 -1 0 400 0)" cx="95" cy="95" rx="25" ry="15" fill="green" stroke="black" stroke-width="4"/>
  <polygon transform="matrix(0 1 -1 0 400 0)" points="130 70 180 70 155 120" fill="green" stroke="black" stroke-width="4"/>
  <polyline transform="matrix(0 1 -1 0 400 0)" points="130 10 180 10 155 60" fill="green" stroke="black" stroke-width="4"/>
  <path transform="matrix(0 1 -1 0 400 0)" d="M 190 10 C 215 10 240 10 240 35 Q 215 35 215 60" fill="green" stroke="black" stroke-width="4"/>

  <g transform="matrix(0 -1 1 0 0 400)">
    <rect x="10" y="10" width="50" height="50" rx="10" ry="200" fill="blue" stroke="black" stroke-width="4"/>
    <circle cx="95" cy="35" r="25" fill="blue" stroke="black" stroke-width="4"/>
    <ellipse cx="95" cy="95" rx="25" ry="15" fill="blue" stroke="black" stroke-width="4"/>
    <polygon points="130 70 180 70 155 120" fill="blue" stroke="black" stroke-width="4"/>
    <polyline points="130 10 180 10 155 60" fill="blue" stroke="black" stroke-width="4"/>
    <path d="M 190 10 C 215 10 240 10 240 35 Q 215 35 215 60" fill="blue" stroke="black" stroke-width="4"/>
  </g>
</svg>
'''

html = '''
%s
<canvas id="canvas"></canvas>
<script>
%s
</script>
'''

handler = Handler()
simple_svg_parser.parse(svg, handler)
open('test.html', 'w').write(html % (svg, '\n'.join(handler.lines)))
