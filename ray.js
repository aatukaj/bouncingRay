//gAMing
class Ray {
    constructor(x, y, dx, dy) {
        this.pos = createVector(x, y);
        this.dir = createVector(dx, dy);
        this.dir.normalize();
    }
    look_at(x, y, ) {
        this.dir.x = x - this.pos.x;
        this.dir.y = y - this.pos.y;
        this.dir.normalize();
    }
    cast(walls) {
        let record = Infinity;
        let result;
        for (let wall of walls) {
            const x1 = wall.a.x;
            const y1 = wall.a.y;
            const x2 = wall.b.x;
            const y2 = wall.b.y;

            const x3 = this.pos.x;
            const y3 = this.pos.y;
            const x4 = this.pos.x + this.dir.x;
            const y4 = this.pos.y + this.dir.y;
            const den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4);
            if (den == 0) {
                continue;
            }

            const t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den;
            const u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den;
            if (t > 0 && t < 1 && u > 0) {
                const pt = createVector(x1 + t * (x2 - x1), y1 + t * (y2 - y1));
                const d = pt.dist(this.pos);
                if (d < record) {
                    record = d;
                    result = {
                        point: pt,
                        wall: wall
                    };
                }
            }
        }
        return result;
    }
    draw() {
        stroke(255);
        push();
        line(
            this.pos.x,
            this.pos.y,
            this.pos.x + this.dir.x * 1000,
            this.pos.y + this.dir.y * 1000
        );
        pop();
    }
}

class BouncingRay extends Ray {
    constructor(x, y, dx, dy, max_bounces) {
        super(x, y, dx, dy);
        this.max_bounces = max_bounces;
    }
    bcast(walls) {
        let rays = [new Ray(this.pos.x, this.pos.y, this.dir.x, this.dir.y)]
        let prev_wall;
        for (let i = 0; i < this.max_bounces; i++) {
            let temp = [...walls]
            if (prev_wall) {
                const index = temp.indexOf(prev_wall);
                if (index > -1) {
                    temp.splice(index, 1);
                }
            }
            let ray = rays[rays.length - 1]
            let result = ray.cast(temp);
            console.log(i);
            if (result) {

                prev_wall = result.wall;
                normal = createVector(-(result.wall.a.y - result.wall.b.y), result.wall.a.x - result.wall.b.x);
                normal.normalize();
                let dir = ray.dir.copy()
                dir.reflect(normal);
                rays.push(new Ray(...result.point.array(), ...dir.array()))
            }

        }
        return rays;
    }
}


class Wall {
    constructor(ax, ay, bx, by) {
        this.a = createVector(ax, ay);
        this.b = createVector(bx, by);
    }
    draw() {
        stroke(255);
        push();
        line(this.a.x, this.a.y, this.b.x, this.b.y);
        pop();
    }
}
let walls = [];

function arrayRemove(arr, value) {

    return arr.filter(function (ele) {
        return ele != value;
    });
}

function setup() {
    createCanvas(800, 800);
    bray = new BouncingRay(400, 400, 1, 0, 5);

    for (let i = 0; i < 5; i++) {
        walls[i] = new Wall(random(width), random(height), random(width), random(height));
    }
}

function draw() {
    background(0);
    let rays = bray.bcast(walls);
    if (rays) {
        for (ray of rays){
            ray.draw()
        }
        

        bray.look_at(mouseX, mouseY);


    }
    for (wall of walls) {
        wall.draw();
    }

}