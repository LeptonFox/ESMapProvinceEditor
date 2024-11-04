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

        // Initialize cells for each site
        this.sites.forEach(site => this.cells.push({ site, halfedges: [] }));
        
        this._generateVoronoi();
        return { cells: this.cells, edges: this.edges };
    }

    _generateVoronoi() {
        // Sort sites by position for beachline sweep
        this.sites.sort((a, b) => a.y - b.y || a.x - b.x);
        const beachline = new Beachline(this);

        // Insert each site into the beachline
        this.sites.forEach(site => beachline.insert(site));
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

        // Handle initial arc case
        if (this.arcs.length === 0) {
            this.arcs.push(new Arc(site, cell));
            return;
        }

        // Process through arcs and insert appropriately
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
        // Clip each edge to the bounding box
        this.edges.forEach(edge => {
            if (!edge.end) edge.end = this._clipEdge(edge);
        });
    }

    _breaksArc(site, arc) {
        // Modified arc breaking condition based on site closeness and y-coordinates
        return Math.abs(site.x - arc.site.x) < 1 && site.y < arc.site.y;
    }

    _createEdge(start, end) {
        // Add start point, end is set later or clipped
        return { start, end: null };
    }

    _clipEdge(edge) {
        const { xl, xr, yt, yb } = this.voronoi.bbox;

        // Calculate where edge intersects bbox
        const xClipped = Math.max(xl, Math.min(edge.start.x, xr));
        const yClipped = Math.max(yt, Math.min(edge.start.y, yb));
        return { x: xClipped, y: yClipped };
    }
}

class Arc {
    constructor(site, cell) {
        this.site = site;
        this.cell = cell;
    }
}
