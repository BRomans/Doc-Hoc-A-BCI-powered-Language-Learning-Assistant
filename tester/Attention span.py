import pygame
import time
import random
import datetime
import csv

time_arr=[]
pygame.init()
SCREEN_WIDTH=800
SCREEN_HEIGHT=800
screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
def random_data(A):
    return random.randint(50,A-50)
def random_time(z):
    return random.uniform(1,z)
start = time.time()
start1 = time.time()

clock = pygame.time.Clock()
x=100
y=100
img=pygame.image.load('tester/red.jpeg')
img=pygame.transform.scale(img, (100, 100))
img_b=pygame.image.load('tester/green.png')
img_b=pygame.transform.scale(img, (100, 100))
running=True
started=False
found=True
found1=True
pressed=False
control=False
reaction_times=[]
timestamps=[]
pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)
text_surface = my_font.render('Press SPACE to start', False, (255,255, 255))
text_rect = text_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
reaction_time=0
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
       if event.type == pygame.KEYDOWN:
           if event.key == pygame.K_SPACE:
               started=True
           if event.key == pygame.K_z:

               running = False
           if event.key ==pygame.K_r:
                found=True
                start = time.time()
                timestamps.append(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time())))
                reaction_time=start-appeared
                reaction_times.append(reaction_time)
                arg=time.time()
                l=arg-starteda
                time_arr.append(l)
                print(starteda)




    if started==False:
        screen.blit(text_surface, text_rect)

    if started:
        re = my_font.render(str(round(reaction_time*1000)), False, (255, 255, 255))
        screen.blit(re, (300,50))
        if found==True :
            time_start=random_time(3)
            rect_w_h=(random_data(SCREEN_WIDTH),random_data(SCREEN_HEIGHT))
            found=False
        if time.time()-start<time_start:
            appeared=time.time()
        if time.time()-start>time_start:
            screen.blit(img,rect_w_h)
        if control==False:
            starteda=time.time()
            control=True
    pygame.display.update()

stuff=[[]]
x=0
while x<=len(timestamps)-1:
    stuff.append([timestamps[x],time_arr[x],reaction_times[x]])
    x=x+1

with open('data.csv', 'w', newline='') as file:

    writer = csv.writer(file)
    writer.writerow(['timestamps','time_from_start','reaction_times'])
    writer.writerows(stuff)
print(reaction_times)
print(timestamps)
print(time_arr)
