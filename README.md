# Simple SVG Parser

A small library to get geometry out of an SVG file. Deals with understanding path command streams and all of the different SVG shape types. Meant for use with things like icons, and not meant to support all of SVG. Automatically flattens all geometry into absolutely-positioned line segments and cubic bezier splines.

Usage:

    class Handler:
      def metadata(self, data):
        print 'width(%d)' % data.get('width', 0)
        print 'height(%d)' % data.get('height', 0)

      def beginPath(self):
        print 'beginPath()'

      def moveTo(self, x, y):
        print 'moveTo(%f, %f)' % (x, y)

      def lineTo(self, x, y):
        print 'lineTo(%f, %f)' % (x, y)

      def curveTo(self, x1, y1, x2, y2, x3, y3):
        print 'curveTo(%f, %f, %f, %f, %f, %f)' % (x1, y1, x2, y2, x3, y3)

      def closePath(self):
        print 'closePath()'

      def fill(self, r, g, b, a):
        print 'fill(%d, %d, %d, %f)' % (r, g, b, a)

      def stroke(self, r, g, b, a, width):
        print 'stroke(%d, %d, %d, %f, %f)' % (r, g, b, a, width)

    import sys
    import simple_svg_parser

    for path in sys.argv[1:]:
      simple_svg_parser.parse(open(path).read(), Handler())
