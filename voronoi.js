class Voronoi {
    constructor() {
        this.sites = [];
        this.edges = [];
        this.cells = [];
    }

    compute(sites, bbox) {
        this.sites = sites;
        this.edges = [];
        this.cells = [];
        this.bbox = bbox;

        this.sites.forEach(site => {
            const cell = { site, halfedges: [] };
            this.cells.push(cell);
        });

        this._generateVoronoi();
        return { cells: this.cells, edges: this.edges };
    }

    _generateVoronoi() {
        this.sites.sort((a, b) => a.y - b.y || a.x - b.x);
        const beachline = new Beachline(this);

        this.sites.forEach(site => {
            beachline.insert(site);
        });

        beachline.finish();
    }
}

class Beachline {
    constructor(voronoi) {
        this.voronoi = voronoi;
        this.edges = voronoi.edges;
        this.cells = voronoi.cells;
        this.arcs = [];
    }

    insert(site) {
        const cell = this.cells.find(c => c.site === site);

        if (this.arcs.length === 0) {
            this.arcs.push(new Arc(site, cell));
            return;
        }

        for (let i = 0; i < this.arcs.length; i++) {
            const arc = this.arcs[i];
            if (this._breaksArc(site, arc)) {
                const newArc = new Arc(site, cell);
                const edge = this._createEdge(arc.site, newArc.site);

                arc.cell.halfedges.push(edge);
                newArc.cell.halfedges.push(edge);

                this.edges.push(edge);
                this.arcs.splice(i, 1, arc, newArc);
                return;
            }
        }
    }

    finish() {
        this.edges.forEach(edge => {
            if (!edge.end) edge.end = this._clipEdge(edge);
        });
    }

    _breaksArc(site, arc) {
        return Math.abs(site.x - arc.site.x) < 1 && site.y < arc.site.y;
    }

    _createEdge(start, end) {
        const edge = { start, end: null };

        // Assign halfedges to cells by direction
        this.cells.forEach(cell => {
            if (cell.site === start) {
                cell.halfedges.push({ edge, site: end });
            }
            if (cell.site === end) {
                cell.halfedges.push({ edge, site: start });
            }
        });

        this.edges.push(edge);
        return edge;
    }

    _clipEdge(edge) {
        const { xl, xr, yt, yb } = this.voronoi.bbox;
        return {
            x: Math.max(xl, Math.min(edge.start.x, xr)),
            y: Math.max(yt, Math.min(edge.start.y, yb))
        };
    }
}

class Arc {
    constructor(site, cell) {
        this.site = site;
        this.cell = cell;
    }
}
