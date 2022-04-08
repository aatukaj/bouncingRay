
import pygame
from pygame.math import Vector2
import pygame_gui
import sys, time
from random import randint

class Ray:
    def __init__(self, pos, dir):
        self.pos = Vector2(pos)
        self.dir = Vector2(dir)

    def look_at(self, x, y):
        self.dir.x = x-self.pos.x     
        self.dir.y = y-self.pos.y
        self.dir.normalize_ip()


    
    def cast(self, walls):
        """Returns the closest point of intersection and the intersected wall in a tuple."""
        record=float('inf')
        closest=None
        for wall in walls:
            x1, y1 = wall[0]
            x2, y2 = wall[1]

            x3, y3 = self.pos
            x4, y4 = self.pos+self.dir

            den = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
            if den == 0:
                continue

            t = ((x1-x3)*(y3-y4)-(y1-y3)*(x3-x4)) / den
            u = -((x1-x2)*(y1-y3)-(y1-y2)*(x1-x3)) / den
            if t >= 0 and t <= 1 and u>=0:
                pt = Vector2()
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
                normal = Vector2(-(y1-y2), x1-x2).normalize()
                rays.append(Ray(result[0], rays[-1].dir.reflect(normal)))
        return rays


def random_wall(w, h):
    return ((randint(0, w),randint(0, h)), (randint(0, w),randint(0, h)))
    
def generate_walls(max_walls, w, h):
    return [random_wall(w, h) for _ in range(max_walls)]



def main():
    pygame.init()

    WIN_WIDTH = 900
    WIN_HEIGHT = 900
    MAX_BOUNCES = 10
    


    win=pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    win_walls=[
        ((WIN_WIDTH, WIN_HEIGHT), (WIN_HEIGHT, 0)),
        ((WIN_WIDTH, WIN_HEIGHT), (0, WIN_HEIGHT)), 
        ((0, 0), (0, WIN_HEIGHT)), 
        ((0, 0), (WIN_WIDTH, 0))
        ]
    manager = pygame_gui.UIManager((WIN_WIDTH, WIN_HEIGHT))

    genwalls_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIN_WIDTH-200, WIN_HEIGHT-25), (200, 25)),
                                             text='Regenerate walls',
                                             manager=manager)

    bounces_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((0, WIN_HEIGHT-25), (300, 25)), 
        start_value=10,
        value_range=(0, 40),     
        manager=manager)

    maxwalls_slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((300, WIN_HEIGHT-25), (300, 25)), 
        start_value=10,
        value_range=(0, 20),     
        manager=manager)
    

    MAX_WALLS = maxwalls_slider.get_current_value()

    ray = BouncingRay((WIN_WIDTH//2,WIN_HEIGHT//2), (1, 0), MAX_BOUNCES)  

    walls=generate_walls(MAX_WALLS, WIN_WIDTH, WIN_HEIGHT)

    clock = pygame.time.Clock()
    last_time = time.time()

    pygame.font.init()
    font = pygame.font.SysFont("Comic Sans MS", 20)

    while True:
        win.fill((0, 0, 0))
        clock.tick()
        dt = time.time() - last_time
        last_time = time.time()

        mpos=pygame.mouse.get_pos()
        if mpos[1]<WIN_HEIGHT-35:
            ray.look_at(*pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == genwalls_button:
                    walls=generate_walls(MAX_WALLS, WIN_WIDTH, WIN_HEIGHT)

            if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == bounces_slider:
                    ray.max_bounces=round(bounces_slider.get_current_value())
                if event.ui_element == maxwalls_slider:
                    val=round(maxwalls_slider.get_current_value())
                    if val > MAX_WALLS:
                        walls.append(random_wall(WIN_WIDTH, WIN_HEIGHT))
                    elif val < MAX_WALLS:
                        walls.pop(0)
                    MAX_WALLS=val
                    
             
            manager.process_events(event)

        manager.update(dt)

        
        keys = pygame.key.get_pressed()

		# movement input
        if keys[pygame.K_UP] or keys[pygame.K_w]: 
            ray.pos.y += -300*dt
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]: 
            ray.pos.y += 300*dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            ray.pos.x += 300*dt
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]: 
            ray.pos.x += -300*dt
        
        

        for wall in walls:
            pygame.draw.aaline(win, (255, 255, 0), *wall)
        rays=ray.cast(walls+win_walls)
        if (len(rays)>1): 
            pygame.draw.aalines(win, (255, 255, 255), False, [ray.pos for ray in rays]+[rays[-1].pos+rays[-1].dir*1])



        pygame.draw.circle(win, (255, 255, 255), ray.pos, 5)
        win.blit(font.render(f"FPS : {round(clock.get_fps())}", False, (255, 255, 255)), (0,0))
        manager.draw_ui(win)
        pygame.display.update()

if __name__ == "__main__":
    main()

