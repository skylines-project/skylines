/*!
 * g.Raphael 0.5 - Charting library, based on Raphaël
 *
 * Copyright (c) 2009 Dmitry Baranovskiy (http://g.raphaeljs.com)
 * Licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) license.
 */
(function () {

    function shrink(values, dim) {
        var k = values.length / dim,
            j = 0,
            l = k,
            sum = 0,
            res = [];

        if (k > 1) {
            while (j < values.length) {
                l--;

                if (l < 0) {
                    sum += values[j] * (1 + l);
                    res.push(sum / k);
                    sum = values[j++] * -l;
                    l += k;
                } else {
                    sum += values[j++];
                }
            }
        } else {
            res = values;
        }

        return res;
    }

    function getAnchors(p1x, p1y, p2x, p2y, p3x, p3y) {
        var l1 = (p2x - p1x) / 2,
            l2 = (p3x - p2x) / 2,
            a = Math.atan((p2x - p1x) / Math.abs(p2y - p1y)),
            b = Math.atan((p3x - p2x) / Math.abs(p2y - p3y));

        a = p1y < p2y ? Math.PI - a : a;
        b = p3y < p2y ? Math.PI - b : b;

        var alpha = Math.PI / 2 - ((a + b) % (Math.PI * 2)) / 2,
            dx1 = l1 * Math.sin(alpha + a),
            dy1 = l1 * Math.cos(alpha + a),
            dx2 = l2 * Math.sin(alpha + b),
            dy2 = l2 * Math.cos(alpha + b);

        return {
            x1: p2x - dx1,
            y1: p2y + dy1,
            x2: p2x + dx2,
            y2: p2y + dy2
        };
    }

    function Linechart(paper, x, y, width, height, valuesx, valuesy, opts) {
        
        var chartinst = this;
        
        opts = opts || {};

        if (!paper.raphael.is(valuesx[0], "array")) {
            valuesx = [valuesx];
        }

        if (!paper.raphael.is(valuesy[0], "array")) {
            valuesy = [valuesy];
        }

        var gutter = opts.gutter || 10,
            len = Math.max(valuesx[0].length, valuesy[0].length),
            symbol = opts.symbol || "",
            colors = opts.colors || chartinst.colors,
            columns = null,
            dots = null,
            chart = paper.set(),
            path = [],
            primary = opts.primary || 0,
            stripesy = (opts.stripes && opts.stripes.y) || [],
            inactive_opacity = opts.inactive_opacity || 0.3,
            stripes_visibility = opts.stripes.visible;

        for (var i = 0, ii = valuesy.length; i < ii; i++) {
            len = Math.max(len, valuesy[i].length);
        }

        var valuesx_shrinked = [];
        var valuesy_shrinked = [];
        var stripesy_shrinked = [];

        for (i = 0, ii = valuesy.length; i < ii; i++) {
            valuesy_shrinked[i] = shrink(valuesy[i], width - 2 * gutter);
            len = valuesy_shrinked.lenght;

            if (valuesx[i]) {
                valuesx_shrinked[i] = shrink(valuesx[i], width - 2 * gutter);
            }

            if (opts.stripes) {
                stripesy_shrinked[i] = shrink(stripesy[i], width - 2 * gutter);
            }
        }

        var stripes_miny = Math.min.apply(Math, stripesy[primary]),
            stripes_maxy = Math.max.apply(Math, stripesy[primary]);

        var allx = Array.prototype.concat.apply([], valuesx_shrinked),
            ally = Array.prototype.concat.apply([], valuesy_shrinked),
            xdim = chartinst.snapEnds(Math.min.apply(Math, allx), Math.max.apply(Math, allx), valuesx_shrinked[0].length - 1),
            minx = xdim.from,
            maxx = xdim.to,
            ydim = chartinst.snapEnds(Math.min.apply(Math, ally), Math.max.apply(Math, ally), valuesy_shrinked[0].length - 1),
            miny = ydim.from,
            maxy = ydim.to,
            kx = (width - gutter * 2) / ((maxx - minx) || 1),
            ky = (height - gutter * 2) / ((maxy - miny) || 1);

        var stripes = createStripes();
        var shades = createShades();
        var axis = createAxis();

        var res = createLines();
        var lines = res.lines,
            symbols = res.symbols;

        function createShades() {
            var shades = paper.set();

            for (i = 0, ii = valuesy_shrinked.length; i < ii; i++) {
                if (opts.shade) {
                    shades.push(paper.path().attr({ stroke: "none", fill: colors[i%colors.length], opacity: opts.nostroke ? 1 : .3 }));
                }
            }
            return shades;
        }

        function initStripes() {
            var stripes = paper.set(),
                Y = y + gutter,
                h = opts.stripes.height;

            for (var dx = 0; dx < (width - 2 * gutter); dx++) {
                var X = x + gutter + dx;

                stripes.push(paper.path(["M", X, Y, "v", 0, h])
                    .attr({ stroke: "#ffffff" }));
            }

            return stripes;
        }

        function createStripes() {
            if (!opts.stripes || !stripes_visibility) return;

            var stripes = chart.stripes || initStripes();
            var u = 0,
                v = width - 2 * gutter;

            var u_min = v,
                v_max = u;
            var base_color = opts.stripes.color || { h: 0.42, s: 1, l: 0.5 };
            var stripes_range = opts.stripes.range || Math.max(1, stripes_maxy - stripes_miny);

            for (var j = 0, jj = stripesy_shrinked[primary].length - 1; j < jj; j++) {
                u = Math.max(0, Math.round( (valuesx_shrinked[primary][j] - minx) * kx )),
                v = Math.min(width - 2 * gutter, Math.round( (valuesx_shrinked[primary][j+1] - minx) * kx ));
                var value = (stripesy_shrinked[primary][j] - stripes_miny) / stripes_range;

                u_min = Math.min(u, u_min);
                v_max = Math.max(v, v_max);

                for (u; u < v; u++) {
                    // value is the saturation of the color from 0 to 1, where 0 is white and
                    // 1 is full saturated.
                    var color = paper.raphael.hsl(
                        base_color.h * 100,
                        base_color.s * 100,
                        base_color.l * 100 + (100 - base_color.l * 100) * (1 - value)
                    );
                    stripes[u].attr({ stroke: color });
                }
            }

            // reset stripes which are not set yet...
            for (var i = u_min - 1; i >= 0; i--) {
                stripes[i].attr({ stroke: "#ffffff" });
            }

            for (var i = Math.max(v_max, u_min); i < (width - 2 * gutter); i++) {
                stripes[i].attr({ stroke: "#ffffff" });
            }

            return stripes;
        }

        function createAxis() {
            var axis = paper.set();

            if (opts.axis) {
                var ax = (opts.axis + "").split(/[,\s]+/);
                +ax[0] && axis.push(chartinst.axis(x + gutter, y + gutter, width - 2 * gutter, minx, maxx, opts.axisxstep || Math.floor((width - 2 * gutter) / 20), 2, opts.axisxfunc, paper));
                +ax[1] && axis.push(chartinst.axis(x + width - gutter, y + height - gutter, height - 2 * gutter, miny, maxy, opts.axisystep || Math.floor((height - 2 * gutter) / 20), 3, opts.axisyfunc, paper));
                +ax[2] && axis.push(chartinst.axis(x + gutter, y + height - gutter, width - 2 * gutter, minx, maxx, opts.axisxstep || Math.floor((width - 2 * gutter) / 20), 0, opts.axisxfunc, paper));
                +ax[3] && axis.push(chartinst.axis(x + gutter, y + height - gutter, height - 2 * gutter, miny, maxy, opts.axisystep || Math.floor((height - 2 * gutter) / 20), 1, opts.axisyfunc, paper));
            }
            return axis;
        }

        function createLines() {
            var lines = paper.set(),
                symbols = paper.set(),
                line;

            for (i = 0, ii = valuesy_shrinked.length; i < ii; i++) {
                if (!opts.nostroke) {
                    lines.push(line = paper.path().attr({
                        stroke: colors[i%colors.length],
                        "stroke-width": opts.width || 2,
                        "stroke-linejoin": "round",
                        "stroke-linecap": "round",
                        "stroke-dasharray": opts.dash || "",
                        opacity: (i == primary) ? 1 : inactive_opacity
                    }));
                }

                var sym = Raphael.is(symbol, "array") ? symbol[i] : symbol,
                    symset = paper.set();

                path = [];

                for (var j = 0, jj = valuesy_shrinked[i].length; j < jj; j++) {
                    var X = x + gutter + ((valuesx_shrinked[i] || valuesx_shrinked[0])[j] - minx) * kx,
                        Y = y + height - gutter - (valuesy_shrinked[i][j] - miny) * ky;

                    (Raphael.is(sym, "array") ? sym[j] : sym) && symset.push(paper[Raphael.is(sym, "array") ? sym[j] : sym](X, Y, (opts.width || 2) * 3).attr({ fill: colors[i%colors.length], stroke: "none" }));
                    if (opts.smooth) {
                        if (j && j != jj - 1) {
                            var X0 = x + gutter + ((valuesx_shrinked[i] || valuesx_shrinked[0])[j - 1] - minx) * kx,
                                Y0 = y + height - gutter - (valuesy_shrinked[i][j - 1] - miny) * ky,
                                X2 = x + gutter + ((valuesx_shrinked[i] || valuesx_shrinked[0])[j + 1] - minx) * kx,
                                Y2 = y + height - gutter - (valuesy_shrinked[i][j + 1] - miny) * ky,
                                a = getAnchors(X0, Y0, X, Y, X2, Y2);

                            path = path.concat([a.x1, a.y1, X, Y, a.x2, a.y2]);
                        }

                        if (!j) {
                            path = ["M", X, Y, "C", X, Y];
                        }
                    } else {
                        path = path.concat([j ? "L" : "M", X, Y]);
                    }
                }

                if (opts.smooth) {
                    path = path.concat([X, Y, X, Y]);
                 }

                symbols.push(symset);

                if (opts.shade) {
                    shades[i].attr({ path: path.concat(["L", X, y + height - gutter, "L",  x + gutter + ((valuesx_shrinked[i] || valuesx_shrinked[0])[0] - minx) * kx, y + height - gutter, "z"]).join(",") });
                }

                !opts.nostroke && line.attr({ path: path.join(",") });
            }

            return { lines: lines, symbols: symbols };
        }

        function createColumns(f) {
            // unite Xs together
            var Xs = [];

            for (var i = 0, ii = valuesx_shrinked.length; i < ii; i++) {
                Xs = Xs.concat(valuesx_shrinked[i]);
            }

            Xs.sort();
            // remove duplicates

            var Xs2 = [],
                xs = [];

            for (i = 0, ii = Xs.length; i < ii; i++) {
                Xs[i] != Xs[i - 1] && Xs2.push(Xs[i]) && xs.push(x + gutter + (Xs[i] - minx) * kx);
            }

            Xs = Xs2;
            ii = Xs.length;

            var cvrs = f || paper.set();

            for (i = 0; i < ii; i++) {
                var X = xs[i] - (xs[i] - (xs[i - 1] || x)) / 2,
                    w = ((xs[i + 1] || x + width) - xs[i]) / 2 + (xs[i] - (xs[i - 1] || x)) / 2,
                    C;

                f ? (C = {}) : cvrs.push(C = paper.rect(X - 1, y, Math.max(w + 1, 1), height).attr({ stroke: "none", fill: "#000", opacity: 0 }));
                C.values = [];
                C.symbols = paper.set();
                C.y = [];
                C.x = xs[i];
                C.axis = Xs[i];

                for (var j = 0, jj = valuesy_shrinked.length; j < jj; j++) {
                    Xs2 = valuesx_shrinked[j] || valuesx_shrinked[0];

                    for (var k = 0, kk = Xs2.length; k < kk; k++) {
                        if (Xs2[k] == Xs[i]) {
                            C.values.push(valuesy_shrinked[j][k]);
                            C.y.push(y + height - gutter - (valuesy_shrinked[j][k] - miny) * ky);
                            C.symbols.push(chart.symbols[j][k]);
                        }
                    }
                }

                f && f.call(C);
            }

            !f && (columns = cvrs);
        }

        function createDots(f) {
            var cvrs = f || paper.set(),
                C;

            for (var i = 0, ii = valuesy_shrinked.length; i < ii; i++) {
                for (var j = 0, jj = valuesy_shrinked[i].length; j < jj; j++) {
                    var X = x + gutter + ((valuesx_shrinked[i] || valuesx_shrinked[0])[j] - minx) * kx,
                        nearX = x + gutter + ((valuesx_shrinked[i] || valuesx_shrinked[0])[j ? j - 1 : 1] - minx) * kx,
                        Y = y + height - gutter - (valuesy_shrinked[i][j] - miny) * ky;

                    f ? (C = {}) : cvrs.push(C = paper.circle(X, Y, Math.abs(nearX - X) / 2).attr({ stroke: "none", fill: "#000", opacity: 0 }));
                    C.x = X;
                    C.y = Y;
                    C.value = valuesy_shrinked[i][j];
                    C.line = chart.lines[i];
                    C.shade = chart.shades[i];
                    C.symbol = chart.symbols[i][j];
                    C.symbols = chart.symbols[i];
                    C.axis = (valuesx_shrinked[i] || valuesx_shrinked[0])[j];
                    f && f.call(C);
                }
            }

            !f && (dots = cvrs);
        }

        chart.push(lines, shades, symbols, axis, columns, dots);
        chart.lines = lines;
        chart.shades = shades;
        chart.symbols = symbols;
        chart.axis = axis;

        if (opts.stripes) {
            chart.push(stripes);
            chart.stripes = stripes;
        }

        chart.hoverColumn = function (fin, fout) {
            !columns && createColumns();
            columns.mouseover(fin).mouseout(fout);
            return this;
        };

        chart.clickColumn = function (f) {
            !columns && createColumns();
            columns.click(f);
            return this;
        };

        chart.hrefColumn = function (cols) {
            var hrefs = paper.raphael.is(arguments[0], "array") ? arguments[0] : arguments;

            if (!(arguments.length - 1) && typeof cols == "object") {
                for (var x in cols) {
                    for (var i = 0, ii = columns.length; i < ii; i++) if (columns[i].axis == x) {
                        columns[i].attr("href", cols[x]);
                    }
                }
            }

            !columns && createColumns();

            for (i = 0, ii = hrefs.length; i < ii; i++) {
                columns[i] && columns[i].attr("href", hrefs[i]);
            }

            return this;
        };

        chart.hover = function (fin, fout) {
            !dots && createDots();
            dots.mouseover(fin).mouseout(fout);
            return this;
        };

        chart.click = function (f) {
            !dots && createDots();
            dots.click(f);
            return this;
        };

        chart.each = function (f) {
            createDots(f);
            return this;
        };

        chart.eachColumn = function (f) {
            createColumns(f);
            return this;
        };

        chart.resetSize = function(_width, _height) {
            width = _width;
            height = _height;

            kx = (width - gutter * 2) / ((maxx - minx) || 1);
            ky = (height - gutter * 2) / ((maxy - miny) || 1);

            var res = createLines();
            lines = res.lines,
            symbols = res.symbols;

            chart.lines.remove();
            chart.lines = lines;

            chart.symbols.remove();
            chart.symbols = symbols;

            chart.axis.remove();
            chart.axis = createAxis();
        };

        chart.zoomReset = function(reset_y_axis) {
            var from = [];
            var to = [];

            for (i = 0, ii = valuesy.length; i < ii; i++) {
                from.push(0);
                to.push(valuesy[i].length-1);
            }
            chart.zoomInto(from, to, reset_y_axis);
        };

        chart.zoomInto = function(from, to, reset_y_axis) {
            var max_len = 0;

            for (i = 0, ii = valuesy.length; i < ii; i++) {
                if (from[i] == -1 || to[i] == -1) {
                  valuesx_shrinked[i] = [];
                  valuesy_shrinked[i] = [];
                  continue;
                }

                valuesy_shrinked[i] = shrink(valuesy[i].slice(from[i], to[i]+1), width - 2 * gutter);
                len = valuesy_shrinked.lenght;

                if (valuesx[i]) {
                    valuesx_shrinked[i] = shrink(valuesx[i].slice(from[i], to[i]+1), width - 2 * gutter);
                    if (max_len < valuesx_shrinked[i].length) max_len = valuesx_shrinked[i].length;
                }

                if (opts.stripes) {
                    stripesy_shrinked[i] = shrink(stripesy[i].slice(from[i], to[i]+1), width - 2 * gutter);
                }
            }

            allx = Array.prototype.concat.apply([], valuesx_shrinked);
            xdim = chartinst.snapEnds(Math.min.apply(Math, allx), Math.max.apply(Math, allx), max_len - 1);
            minx = xdim.from;
            maxx = xdim.to;
            kx = (width - gutter * 2) / ((maxx - minx) || 1);

            if (reset_y_axis) {
              ally = Array.prototype.concat.apply([], valuesy),
              ydim = chartinst.snapEnds(Math.min.apply(Math, ally), Math.max.apply(Math, ally), max_len - 1),
              miny = ydim.from,
              maxy = ydim.to,
              ky = (height - gutter * 2) / ((maxy - miny) || 1),
              stripes_miny = Math.min.apply(Math, stripesy[primary]),
              stripes_maxy = Math.max.apply(Math, stripesy[primary]);
            }

            var res = createLines();
            lines = res.lines,
            symbols = res.symbols;

            chart.lines.remove();
            chart.lines = lines;

            chart.symbols.remove();
            chart.symbols = symbols;

            chart.axis.remove();
            chart.axis = createAxis();

            chart.stripes = createStripes();
        }

        chart.getProperties = function() {
            return { minx: minx,
                     maxx: maxx,
                     miny: miny,
                     maxy: maxy,
                     gutter: gutter,
                     width: width,
                     height: height,
                     x: x,
                     y: y,
                     kx: kx,
                     ky: ky,
                     primary: primary };
        }

        chart.setPrimary = function(new_primary) {
            if (new_primary == primary) return;

            primary = new_primary;

            stripes_miny = Math.min.apply(Math, stripesy[primary]);
            stripes_maxy = Math.max.apply(Math, stripesy[primary]);

            chart.stripes = createStripes();

            for (var i = 0; i < chart.lines.length; i++) {
                chart.lines[i].attr({
                  opacity: (i == primary) ? 1 : inactive_opacity
                });
            }
        }

        chart.toggleStripes = function() {
            if (!opts.stripes) return;

            stripes_visibility = !stripes_visibility;
            if (stripes_visibility) {
                stripes = createStripes();
                chart.push(stripes.toBack());
                chart.stripes = stripes;
            } else {
                chart.stripes.remove();
                delete chart.stripes;
            }
        }

        chart.getStripesState = function() {
            return stripes_visibility && opts.stripes;
        }

        return chart;
    };
    
    //inheritance
    var F = function() {};
    F.prototype = Raphael.g;
    Linechart.prototype = new F;
    
    //public
    Raphael.fn.linechart = function(x, y, width, height, valuesx, valuesy, opts) {
        return new Linechart(this, x, y, width, height, valuesx, valuesy, opts);
    }
    
})();
