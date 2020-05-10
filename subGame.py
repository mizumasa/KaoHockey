#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import sys
import cv2
import random
from common import *

__author__ = "masaru mizuochi"
__version__ = "1.00"
__date__ = "12 April 2020"

BALL_S = 50
BALL_MASK = np.zeros((BALL_S,BALL_S,3),dtype=np.uint8)
cv2.circle(BALL_MASK,(25,25), 25, (255,255,255), -1)
BALL_MASKn = cv2.bitwise_not(BALL_MASK)

size = tuple([BALL_S,BALL_S])
center = tuple([int(BALL_S/2), int(BALL_S/2)])
scale = 1.0

TEST_IMAGE = np.zeros((BALL_S,BALL_S,3),dtype=np.uint8)
for i in range(BALL_S):
    for j in range(BALL_S):
        TEST_IMAGE[i,j,0]=(i+j)*5

def check_collision(x,y,vy,eyes):
    """
    eyes = [lx,ly,rx,ry]
    """
    if ( (eyes[0] < x) and (x < eyes[2]) and (abs(y - eyes[1]) < abs(vy)) ):
        return 2.0 * (x - eyes[0]) / (eyes[2] - eyes[0]) - 1
    else:
        return None

class Game:
    def __init__(self,w,h):
        self.window_w = w
        self.window_h = h
        self.ball = []
        self.count = 0
        self.speed = 1.0
        self.goal = [None,None,None,None]
        self.score = [0,0]
        self.ball_num = 1
        self.ball_image = TEST_IMAGE
        self.goal_pos = []
        self.ball_pos = []

    def set_ball_image(self,image=None):
        self.ball_image = image        

    def set_speed(self,speed):
        self.speed = speed

    def set_ball_num(self,num):
        self.ball_num = int(num)

    def setup(self):
        for i in range(self.ball_num):
            self.addBall(random.random()*300,random.random()*300)

    def addBall(self,x,y):
        ball = Ball(x,y)
        self.ball.append(ball)

    def set_goal(self,goal):
        self.goal = goal

    def get_score(self):
        return self.score

    def reset_score(self):
        self.score = [0,0]

    def get_goal_pos(self):
        return self.goal_pos

    def get_ball_pos(self):
        return self.ball_pos

    def update(self,detected_eyes=[]):
        self.count += 1
        edge_margin = 0
        self.goal_pos = []
        self.ball_pos = []
        if self.ball_image is not None:
            edge_margin = 25
        for ball in self.ball:
            x,y = ball.get_next_pos()
            self.ball_pos.append([x,y])
            vy = ball.get_speed()
            for eyes in detected_eyes:
                ret = check_collision(x,y,vy,eyes)
                if ret is not None:
                    ball.force_x(ret)
                    ball.flip_y()
                    soundBar()
            if x < 0 + edge_margin:
                if ball.flip_x():
                    if self.goal[0] is not None:
                        self.score[self.goal[0]]+=1
                        self.goal_pos.append([x,y])
                        soundPoint()
                    else:
                        soundWall()
            if x > (self.window_w - edge_margin):
                if ball.flip_x():
                    if self.goal[2] is not None:
                        self.score[self.goal[2]]+=1
                        self.goal_pos.append([x,y])
                        soundPoint()
                    else:
                        soundWall()
            if y < 0 + edge_margin:
                if ball.flip_y():
                    if self.goal[1] is not None:
                        self.score[self.goal[1]]+=1
                        self.goal_pos.append([x,y])
                        soundPoint()
                    else:
                        soundWall()
            if y > (self.window_h - edge_margin):
                if ball.flip_y():
                    if self.goal[3] is not None:
                        self.score[self.goal[3]]+=1
                        self.goal_pos.append([x,y])
                        soundPoint()
                    else:
                        soundWall()
            ball.update(self.speed)

    def draw(self,frame):
        p = [(0,self.window_h),(0,0),(self.window_w,0),(self.window_w,self.window_h),(0,self.window_h)]
        c = [(200,0,0),(0,0,200)]
        for i in range(4):
            if self.goal[i] != None:
                cv2.line(frame,p[i],p[i+1],c[self.goal[i]],7)
        for ball in self.ball:
            ball.draw(frame,self.ball_image)

class Ball:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.vx = 3
        self.vy = 3
        self.count = 0
        self.angle = 0.0
        self.speed = 1.0
    def get_speed(self):
        return self.speed * self.vy
    def get_next_pos(self):
        return self.x + self.vx, self.y + self.vy 

    def flip_x(self):
        if (self.count > 4) or (self.count == 0):
            self.vx *= -1
            self.count = 0
            return True
        return False

    def flip_y(self):
        if (self.count > 4) or (self.count == 0):
            self.vy *= -1
            self.count = 0
            return True
        return False
    
    def force_x(self,ret):
        v = (self.vx ** 2 + self.vy ** 2) ** 0.5
        self.vx = min(v-0.2,max(-v+0.2, self.vx + ret))
        if self.vy > 0:
            #self.vy =  max(0.1,(v ** 2 - self.vx ** 2) ** 0.5)
            self.vy =  (v ** 2 - self.vx ** 2) ** 0.5
        else:
            #self.vy = - max(0.1,((v ** 2 - self.vx ** 2) ** 0.5))
            self.vy = - ((v ** 2 - self.vx ** 2) ** 0.5)

    def update(self,speed):
        self.speed = speed
        self.count += 1
        self.angle += 5
        self.x += self.vx * self.speed
        self.y += self.vy * self.speed

    def draw(self,frame,image = None):
        if image is None:
            cv2.circle(frame,(int(self.x),int(self.y)), 10, (0,255,255), -1)
        else:
            try:
                rotation_matrix = cv2.getRotationMatrix2D(center, self.angle, scale)
                image_rotate = cv2.warpAffine(image, rotation_matrix, size, flags=cv2.INTER_CUBIC)
                frame_ = frame[int(self.y)-25:int(self.y)+25,int(self.x)-25:int(self.x)+25,:].copy()
                image_ = cv2.bitwise_and(image_rotate, BALL_MASK)
                frame_ = cv2.bitwise_and(frame_, BALL_MASKn)
                frame[int(self.y)-25:int(self.y)+25,int(self.x)-25:int(self.x)+25,:] = cv2.bitwise_or(frame_, image_)
            except:
                print("ball print error")




if __name__ == '__main__':
    argvs=sys.argv
    print(argvs)
    main()


