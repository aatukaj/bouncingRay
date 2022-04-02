
import pygame

class Ray:
    def __init__(self, pos, dir):
        self.pos = pygame.Vector2(pos)
        self.dir = pygame.Vector2(dir)

    def look_at(self, x, y):
        self.dir.x = x-self.pos.x     
        self.dir.y = y-self.pos.y
        self.dir.normalize_ip()


    #Returns the point of intersection and the intersected wall and  in a tuple
    def cast(self, walls):
        record=float('inf')
        closest=None
        for wall in walls:
            x1, y1 = wall[0]
            x2, y2 = wall[1]

            x3, y3 = self.pos
            x4, y4 = self.pos+self.dir

            den = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
            if den == 0:
                return

            t = ((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4)) / den
            u = -((x1-x2)*(y1-y3)-(y1-y2)*(x1-x3)) / den
            if t >= 0 and t <= 1 and u>=0:
                pt = pygame.Vector2()
                pt.x = x1+t*(x2-x1)
                pt.y = y1+t*(y2-y1)
                d=pt.distance_to(self.pos)
                if d<record:
                    record=d
                    closest=pt, wall
                    
        return closest
    def __repr__(self):
        return f"{self.pos}, {self.dir}"

class BouncingRay(Ray):
    def __init__(self, pos, dir, max_bounces):
        super().__init__(pos, dir)
        self.max_bounces=max_bounces

    def cast(self, walls):
        rays=[Ray(self.pos, self.dir)]
        lastwall=None
        for _ in range(self.max_bounces):
            temp=walls[:]
            if lastwall:
                temp.remove(lastwall)
            result = rays[-1].cast(temp) 
       
            if result:
                lastwall = result[1]
                x1, y1= result[1][0]
                x2, y2= result[1][1]
                normal = pygame.Vector2(-(y1-y2), x1-x2).normalize()
                rays.append(Ray(result[0], rays[-1].dir.reflect(normal)))
        return rays


def main():
    import sys
    from random import randint

    WIN_WIDTH = 900
    WIN_HEIGHT = 900
    MAX_BOUNCES = 10
    WALLS = 5


    win=pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    ray = BouncingRay((WIN_WIDTH//2,WIN_HEIGHT//2), (1, 0), MAX_BOUNCES)  
    walls=[((randint(0, WIN_WIDTH),randint(0, WIN_HEIGHT)), (randint(0, WIN_WIDTH),randint(0, WIN_HEIGHT))) for _ in range(WALLS)]
    
    #Add window borders as walls
    walls+=[
        ((WIN_WIDTH, WIN_HEIGHT), (WIN_WIDTH, 0)),
        ((WIN_WIDTH, WIN_HEIGHT), (0, WIN_HEIGHT)), 
        ((-1, 0), (-1, WIN_HEIGHT)), 
        ((0, 0), (WIN_WIDTH, 0))
        ]

    clock = pygame.time.Clock()

    pygame.font.init()
    font = pygame.font.SysFont("Comic Sans MS", 20)

    while True:
        clock.tick()
        
        ray.look_at(*pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()

		# movement input
        if keys[pygame.K_UP]: 
            ray.pos.y += -1
        elif keys[pygame.K_DOWN]: 
            ray.pos.y += 1
        if keys[pygame.K_RIGHT]: 
            ray.pos.x += 1
        elif keys[pygame.K_LEFT]: 
            ray.pos.x += -1
        
        win.fill((0, 0, 0))

        for wall in walls:
            pygame.draw.aaline(win, (255, 255, 0), *wall)
        rays=ray.cast(walls)
        if (len(rays)>1): 
            pygame.draw.aalines(win, (255, 255, 255), False, [ray.pos for ray in rays]+[rays[-1].pos+rays[-1].dir*1000])


        pygame.draw.circle(win, (255, 255, 255), ray.pos, 5)
        win.blit(font.render(f"FPS : {round(clock.get_fps())}", False, (255, 255, 255)), (0,0))
        
        pygame.display.update()

if __name__ == "__main__":
    main()