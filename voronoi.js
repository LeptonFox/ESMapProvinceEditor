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
        
        this.sites.forEach((site, index) => {
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
        
        if (!this.arcs.length) {
            this.arcs.push(new Arc(site, cell));
            return;
        }

        for (let i = 0; i < this.arcs.length; i++) {
            const arc = this.arcs[i];
            if (this._breaksArc(site, arc)) {
                const newArc = new Arc(site, cell);
                this.edges.push(this._createEdge(arc.site, newArc.site));
                this.arcs.splice(i, 1, arc, newArc);
                return;
            }
        }
    }

    finish() {
        // Connect all edges to the bounding box for completeness
        this.edges.forEach(edge => {
            if (!edge.end) edge.end = this._clipEdge(edge);
        });
    }

    _breaksArc(site, arc) {
        return Math.abs(site.x - arc.site.x) < 1 && site.y < arc.site.y;
    }

    _createEdge(start, end) {
        const edge = { start, end: null };
        this.edges.push(edge);
        return edge;
    }

    _clipEdge(edge) {
        const { xl, xr, yt, yb } = this.voronoi.bbox;
        return { x: Math.max(xl, Math.min(edge.start.x, xr)), y: Math.max(yt, Math.min(edge.start.y, yb)) };
    }
}

class Arc {
    constructor(site, cell) {
        this.site = site;
        this.cell = cell;
    }
}
