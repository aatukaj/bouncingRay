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
    cast(obstacles) {
        let record = Infinity;
        let result;
        for (let wall of obstacles) {
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
    cast(obstacles) {
        let rays = [new Ray(this.pos.x, this.pos.y, this.dir.x, this.dir.y)]
        let prev_wall;
        for (let i = 0; i < this.max_bounces; i++) {
            let temp = [...obstacles]
            if (prev_wall) {
                temp = arrayRemove(obstacles, prev_wall);
            }
            let ray = rays[rays.length - 1];
            let result = ray.cast(temp);
            if (result) {
                prev_wall = result.wall;
                let n = createVector(-(result.wall.a.y - result.wall.b.y), result.wall.a.x - result.wall.b.x);
                n.normalize();
                let dir = ray.dir.copy();
                dir.reflect(n);
                rays.push(new Ray(result.point.x, result.point.y, dir.x, dir.y));
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


function arrayRemove(arr, value) {

    return arr.filter(function (ele) {
        return ele != value;
    });
}

function inBounds(x, y) {
    return (x >= 0 && y >= 0 && x <= width && y <= height);
}

function randomWall(w, h) {
    return new Wall(random(w), random(h), random(w), random(h));
}

function generateWalls(max_walls) {
    let walls = [];
    for (let i = 0; i < max_walls; i++) {
        walls[i] = randomWall(width, height);
    }
    return walls
}


let walls = [];
let win_walls = [];
let obstacles = [];
let bouncingRay;

window.onload = () => {
    let max_bounces_slider = document.getElementById("max_bounces");
    let max_bounces_output = document.getElementById("max_bounces_value");
    max_bounces_output.innerHTML = max_bounces_slider.value;
    
    max_bounces_slider.oninput = function () {
        max_bounces_output.innerHTML = this.value;
        bouncingRay.max_bounces = this.value;
    }

    let walls_slider = document.getElementById("walls");
    let walls_output = document.getElementById("walls_value");
    walls_output.innerHTML = walls_slider.value;

    walls_slider.oninput = function() {
        const dif = Math.abs(this.value-walls.length);
        if (this.value > walls.length) {
            walls.push(...generateWalls(dif));
        } else if (this.value < walls.length) {
            walls.splice(0, dif);
        }
        walls_output.innerHTML = this.value;
    }

    let gen_walls_button = document.getElementById("gen_walls");

    gen_walls_button.onclick = function () {
        walls = generateWalls(walls_slider.value);
    }

};



function setup() {
    createCanvas(800, 800);
    bouncingRay = new BouncingRay(400, 400, 1, 0, 5);
    win_walls = [
        new Wall(width, height, width, 0),
        new Wall(width, height, 0, height),
        new Wall(0, 0, 0, height),
        new Wall(0, 0, width, 0)
    ];
    walls = generateWalls(5);
}

function mouseClicked() {
    if (inBounds(mouseX, mouseY)) {
        bouncingRay.pos = createVector(mouseX, mouseY);
    }

}

function draw() {
    background(0);
    let rays = bouncingRay.cast(walls.concat(win_walls));
    if (rays) {
        stroke(46, 132, 255);
        for (let i = 0; i < rays.length - 1; i++) {
            line(rays[i].pos.x, rays[i].pos.y, rays[i + 1].pos.x, rays[i + 1].pos.y);
        }
        for (let ray of rays) {
            ellipse(ray.pos.x, ray.pos.y, 5, 5);
        }
    }
    if (inBounds(mouseX, mouseY)) {
        bouncingRay.look_at(mouseX, mouseY);
    }
    for (wall of walls) {
        wall.draw();
    }
}
