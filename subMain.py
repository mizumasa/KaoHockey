#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
import sys
import time
import cv2
import json
import glob
import random
import dlib
import PySimpleGUI as sg
from PIL import ImageGrab
from mss import mss

__author__ = "masaru mizuochi"
__version__ = "1.00"
__date__ = "12 April 2020"

from common import *
from multiprocessing import Process
from multiprocessing import Pipe
from multiprocessing import Array

from subGame import Game, BALL_S
from subImage import getImage

SHOW_W_MAIN = 600
SHOW_W_FULL = 1920
SHOW_H_FULL = 1080

SHOW_W_SUB = 40
FPS = 24

MODE_INIT = 0
MODE_PLAY = 1

DETECT_WITH_OPENCV = 0
DETECT_WITH_DLIB = 1
DETECT_WITH = DETECT_WITH_DLIB

GOAL_WIDTH = 7

RESIZE_SCALE_DEFAULT = 2.0

def valueToNdarray(v):
    return np.ctypeslib.as_array(v.get_obj())


def Process1(ptomain,maintop,frame_conn,frame_conn2):
    elapsed_times = []
    count = 0
    print("Process 1 start")
    crop_grab = None
    sct = mss()
    try:
        while True:
            while maintop.poll():
                recv = maintop.recv()
                if "exit" in recv.keys():
                    print("p1 got exit")
                    return
                if "crop_grab" in recv.keys():
                    crop_grab = recv["crop_grab"]
            start = time.time()
            if crop_grab is None:
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img_rgb = np.frombuffer(sct_img.rgb,dtype=np.uint8).reshape((sct_img.height,sct_img.width,3))
            else:
                monitor = {"top":  crop_grab[0], "left": crop_grab[2], "width":  crop_grab[3]-crop_grab[2], "height": crop_grab[1]-crop_grab[0]}
                sct_img = sct.grab(monitor)
                img_rgb = np.frombuffer(sct_img.rgb,dtype=np.uint8).reshape((sct_img.height,sct_img.width,3))
            img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)
            if crop_grab is None:
                valueToNdarray(frame_conn)[:] = img_rgb.flatten()
            else:
                valueToNdarray(frame_conn)[:(crop_grab[3]-crop_grab[2])*(crop_grab[1]-crop_grab[0])*3] = img_rgb.flatten()

            playground_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            playground_gray_flat = playground_gray.flatten()
            valueToNdarray(frame_conn2)[:playground_gray_flat.shape[0]] = playground_gray_flat

            elapsed_times.append(time.time() - start)
            if count%FPS == 0:
                print ("elapsed_time 1(FBS):{0:.0f}".format(sum(elapsed_times)*1000./FPS) + "[msec] {0:.0f}[fps]".format(FPS * 1.0/ sum(elapsed_times)))
                elapsed_times = []
            count += 1
    except KeyboardInterrupt:
        print("Process 1 Error")
        pass


def getPointFromEyes(eyes,img):
    output_eyes = [[],[]]
    X = 0
    Y = 1
    for (ex,ey,ew,eh) in eyes:
        cv2.rectangle(img,(ex,ey),(ex+ew,ey+eh),(0,225,255),2)
        output_eyes[X].append(ex+ew/2)
        output_eyes[Y].append(ey+eh/2)
    if(len(output_eyes[X])>1):
        x_sortargs = np.argsort(output_eyes[X])
        left_eye_x = output_eyes[X][x_sortargs[0]]
        left_eye_y = output_eyes[Y][x_sortargs[0]]
        right_eye_x = output_eyes[X][x_sortargs[-1]]
        right_eye_y = output_eyes[Y][x_sortargs[-1]]
        return [left_eye_x,left_eye_y,right_eye_x,right_eye_y]
    return None

def addOffset(pointEye,x,y):
    return [pointEye[0]+x,pointEye[1]+y,pointEye[2]+x,pointEye[3]+y]

def get_detected_eyes_scale(detected_eyes,show_w,ori_w):
    out = []
    for i in detected_eyes:
        buf = []
        for j in i:
            buf.append(j*show_w/ori_w)
        out.append(buf)
    return out

def find_nearest_face(faces,bx,by):
    dist = []
    for (x,y,w,h) in faces:
        dist.append(abs(bx-(x+w/2))+abs(by-(y+h/2)))
    return faces[np.argmin(dist)]

def Process2(ptomain,maintop,frame_conn,frame_conn_face):
    elapsed_times = []
    count = 0
    print("Process 2 start")
    p2_w = 0
    p2_h = 0

    ball_x = 0
    ball_y = 0
    frame_conn_face_ary = None

    if DETECT_WITH == DETECT_WITH_DLIB:
        dlib_detector = dlib.get_frontal_face_detector()
    if DETECT_WITH == DETECT_WITH_OPENCV:
        print(os.path.join(SCRIPT_DIR,"../data/haarcascade_eye.xml"))
        eye_cascade = cv2.CascadeClassifier(os.path.join(SCRIPT_DIR,"../data/haarcascade_eye.xml"))
        face_cascade = cv2.CascadeClassifier(os.path.join(SCRIPT_DIR,"../data/haarcascade_frontalface_default.xml"))
    detect_mode = 0
    resize_scale = 2
    result_pre = []
    if 1:
        while True:
            try:
                ball_change = False
                while maintop.poll():
                    recv = maintop.recv()
                    if "ball_x" in recv.keys():
                        ball_x = int(recv["ball_x"])
                    if "ball_y" in recv.keys():
                        ball_y = int(recv["ball_y"])                
                    if "ball_change" in recv.keys():
                        ball_change = True
                    if "w" in recv.keys():
                        p2_w = int(recv["w"])
                    if "h" in recv.keys():
                        p2_h = int(recv["h"])
                    if "exit" in recv.keys():
                        print("p2 got exit")
                        return
                    if "detect_mode" in recv.keys():
                        detect_mode = int(recv["detect_mode"])
                    if "detect_level" in recv.keys():
                        resize_scale = float(recv["detect_level"])
                start = time.time()
                img_ary = valueToNdarray(frame_conn).astype("uint8")
                if p2_w*p2_h == 0:
                    continue
                else:
                    img_ary = img_ary[:p2_w*p2_h].reshape((p2_h,p2_w))
                
                p2_h_ = int(p2_h / resize_scale)
                p2_w_ = int(p2_w / resize_scale)
                img_ary_ = cv2.resize(img_ary,(p2_w_,p2_h_))
                faces = []
                if DETECT_WITH == DETECT_WITH_DLIB:
                    dets, scores, idx = dlib_detector.run(img_ary_, 0)
                    for det in dets:
                        faces.append([int(det.left()*resize_scale),int(det.top()*resize_scale),int(det.width()*resize_scale),int(det.height()*resize_scale)])
                if DETECT_WITH == DETECT_WITH_OPENCV:
                    faces = face_cascade.detectMultiScale(img_ary_, 1.3, 5)
                output = []
                if detect_mode == 0:
                    for (x,y,w,h) in faces:
                        output.append([x,y,w,h])
                else:
                    for (x,y,w,h) in faces:
                        cv2.rectangle(img_ary,(x,y),(x+w,y+h),(255,255,0),2)
                        gray_face = img_ary[y:y+h, x:x+w] # cut the gray face frame out
                        eyes = eye_cascade.detectMultiScale(gray_face)
                        ret = getPointFromEyes(eyes,gray_face)
                        if ret is not None:
                            output.append(addOffset(ret,x,y))
                        #cv2.imshow('my image',gray_face)
                for (x_p,y_p,w_p,h_p) in result_pre:
                    use_past = True
                    x_c = x_p+w_p/2
                    y_c = y_p+h_p/2
                    for (x,y,w,h) in faces:
                        if x < x_c and x_c < x+w and y < y_c and y_c < y+h:
                            use_past = False
                    if use_past:
                        output.append([x_p,y_p,w_p,h_p])
                result_pre = faces

                if len(faces) > 0:
                    x,y,w,h = find_nearest_face(faces,ball_x,ball_y)
                    gray_face = img_ary[y:y+h, x:x+w]
                    if gray_face.shape[0]>50 and gray_face.shape[1]>50:
                        frame_conn_face_ary = gray_face.copy()
                if ball_change and frame_conn_face_ary is not None:
                    print(frame_conn_face_ary.shape)
                    if len(frame_conn_face_ary.shape) == 3:
                        frame_conn_face_ary = frame_conn_face_ary[:,:,0] 
                    frame_conn_face_ary = cv2.cvtColor(frame_conn_face_ary, cv2.COLOR_GRAY2RGB)
                    valueToNdarray(frame_conn_face)[:] = cv2.resize(frame_conn_face_ary,(BALL_S,BALL_S)).flatten()

                if 0:
                    cv2.imshow("dlib",img_ary)
                    key = cv2.waitKey(1)
                ptomain.send({"eyes":output})

                elapsed_times.append(time.time() - start)
                if count%FPS == 0:
                    print ("elapsed_time 2(FBS):{0:.0f}".format(sum(elapsed_times)*1000./FPS) + "[msec] {0:.0f}[fps]".format(FPS * 1.0/ sum(elapsed_times)))
                    elapsed_times = []
                count += 1
            except KeyboardInterrupt:
                print("Process 2 loop Error")
            #time.sleep(0.1)
    #except KeyboardInterrupt:
    #    print("Process 2 Error")
    #    pass


def subMain():
    cv2.imshow('KaoHockey',getImage())
    cv2.waitKey(1)
    
    sg.change_look_and_feel('DarkBlue')

    # define the window layout
    layout = [
        [sg.Image(filename='', key='screen', enable_events=True),sg.Image(filename='', key='playground')],

        [sg.Checkbox('Team Mode', default = False, size=(10, 1), key='switch_team'),
        sg.Checkbox('VS Mode', default = True, size=(10, 1), key='vs_mode'),
        sg.Checkbox('Face Ball', default = False, size=(10, 1), key='switch_ball'),
        sg.Checkbox('Flip Screen', default = True, size=(10, 1), key='flip_screen'),
        sg.Checkbox('Flip Text', default = True, size=(10, 1), key='flip_text'),
        sg.Checkbox('Full Screen', default = False, size=(10, 1), key='full_screen')],
        [sg.Text('---',key='score1',font='Courier 20', text_color='blue'),sg.Text(':'),sg.Text('---',key='score2',font='Courier 20', text_color='red')],
        [sg.Text('Crop Left',key='crop_left_label'),sg.Slider((0, 100), 10, 0.1, orientation='h', size=(48, 15), key='crop_left')],
        [sg.Text('Crop Right',key='crop_right_label'),sg.Slider((0, 100), 90, 0.1, orientation='h', size=(48, 15), key='crop_right')],
        [sg.Text('Crop Top',key='crop_top_label'),sg.Slider((0, 100), 10, 0.1, orientation='h', size=(48, 15), key='crop_top')],
        [sg.Text('Crop Bottom',key='crop_bottom_label'),sg.Slider((0, 100), 90, 0.1, orientation='h', size=(48, 15), key='crop_bottom')],
        [sg.Text('Mode',key='ttt',visible=False),sg.Slider((0, 4), 0, 1, orientation='h', size=(20, 15), key='detect_mode',visible=False)],
        [sg.Text('Ball',visible=False),sg.Slider((1, 30), 0, 1, orientation='h', size=(20, 15), key='ball_num',visible=False)],
        [sg.Text('Speed'),sg.Slider((1, 10), 2, 0.1, orientation='h', size=(20, 15), key='game_speed')],
        [sg.Text('Detect Level'),sg.Slider((1, 10), 2, 0.1, orientation='h', size=(20, 15), key='detect_level')],
        [sg.Text('Bar Assist'),sg.Slider((0, 40), 0, 0.1, orientation='h', size=(20, 15), key='bar_assist')],
        [sg.Button('Start', size=(10, 1),key='button_start'),
        sg.Button('Stop', size=(10, 1),key='button_stop',disabled=True),
        sg.Button('Save', size=(10, 1)),
        sg.Button('Reset', size=(10, 1)),
        sg.Button('Exit', size=(10, 1))]
    ]

    # create the window and show it without the plot
    window = sg.Window('KaoHockey',layout,location=(100, 100),no_titlebar=False, alpha_channel=.9, grab_anywhere=False)
    elapsed_times = []
    count = 0

    img = ImageGrab.grab()
    w,h = img.size

    parent_maintop1, child_maintop1 = Pipe()
    parent_ptomain1, child_ptomain1 = Pipe()
    frame_conn1 = Array('i',np.zeros((w*h*3),dtype="uint8"))

    parent_maintop2, child_maintop2 = Pipe()
    parent_ptomain2, child_ptomain2 = Pipe()
    frame_conn2 = Array('i',np.zeros((w*h),dtype="uint8"))
 
    frame_conn3 = Array('i',np.zeros((BALL_S*BALL_S*3),dtype="uint8"))

    p1 = Process(target = Process1, args=(child_ptomain1, parent_maintop1, frame_conn1, frame_conn2))
    p1.start()

    p2 = Process(target = Process2, args=(child_ptomain2, parent_maintop2, frame_conn2, frame_conn3))
    p2.start()

    status = MODE_INIT
    status_pre = status

    detected_eyes = []

    game = None

    crop_grab = None
    crop_grab_size = 0

    crop_left = 0
    crop_right = 0
    crop_top = 0
    crop_bottom = 0
    score = [0,0]
    playscreen = window.FindElement("playground")
    vs_mode_pre = True
    while True:
        try:
            start = time.time()
            event, values = window.read(timeout=0, timeout_key='timeout')
            values['count'] = count
            if event == 'screen':
                print(values)
            if event == 'Reset':
                if game is not None:
                    game.reset_score()
            if event == 'Save':
                f = open('param.json', 'w')
                json.dump(values, f)
                f.close()
            if event == 'button_start':
                if status == MODE_INIT:
                    status = MODE_PLAY
                    window.Element('button_start').Update(disabled=True)
                    window.Element('button_stop').Update(disabled=False)
                    window.refresh()
            if event == 'button_stop':
                if status == MODE_PLAY:
                    status = MODE_INIT
                    window.Element('button_start').Update(disabled=False)
                    window.Element('button_stop').Update(disabled=True)
                    window.refresh()

                    
            if event == 'Exit' or event is None:
                break

            img_ary = valueToNdarray(frame_conn1).astype("uint8")
            if crop_grab is None:
                screen = img_ary.reshape((h,w,3))
                crop_left = int(values['crop_left']/100.0 * w)
                crop_right = int(values['crop_right']/100.0 * w)
                crop_top = int(values['crop_top']/100.0 * h)
                crop_bottom = int(values['crop_bottom']/100.0 * h)
                playground = screen[crop_top:crop_bottom,crop_left:crop_right,:].copy()
                cv2.rectangle(screen,(crop_left,crop_top),(crop_right,crop_bottom),(200,200,200),4)
                draw_goal(screen,crop_left,crop_top,crop_right,crop_bottom,values)
                if min(playground.shape)==0:
                    playground = screen.copy()
            else:
                playground = img_ary[:crop_grab_size].reshape(((crop_grab[1]-crop_grab[0]),(crop_grab[3]-crop_grab[2]),3))
            playground_gray_h = playground.shape[0]
            playground_gray_w = playground.shape[1]
                            
            #playground = (playground*0.8).astype("uint8")
            while parent_ptomain2.poll():
                recv = parent_ptomain2.recv()
                if "eyes" in recv.keys():
                    detected_eyes = recv["eyes"]
                    detected_eyes = extend_eyes(detected_eyes,values)
                    detected_eyes = make_bar(detected_eyes,values)
            for eyes in detected_eyes:
                cv2.line(playground,(int(eyes[0]),int(eyes[1])),(int(eyes[2]),int(eyes[3])),(255,255,0),20)

            if status != MODE_PLAY:
                child_maintop2.send({"w":playground_gray_w})
                child_maintop2.send({"h":playground_gray_h})

            playground_h = playground.shape[0]
            playground_w = playground.shape[1]

            #status = values['switch_screen']
            

            if status == MODE_PLAY:
                detected_eyes_scale = get_detected_eyes_scale(detected_eyes,SHOW_W_MAIN,playground_w)
                screen_w = SHOW_W_SUB
                screen_h = int(screen_w * h / w)
                resize_ratio = 1.0 * SHOW_W_MAIN / playground_w
                playground_h = int(SHOW_W_MAIN * playground_h / playground_w)
                playground_w = SHOW_W_MAIN

                playground = cv2.resize(playground,(playground_w,playground_h))
                if game is not None:

                    game.set_goal(get_goal(values))
                    game.set_player_direction_h(values["switch_team"])
                    game.set_cooperate_mode(not values["vs_mode"])

                    game.set_speed(values['game_speed'])
                    game.update(detected_eyes=detected_eyes_scale)
                    goal_pos = game.get_goal_pos()
                    ball_pos = game.get_ball_pos()
                    child_maintop2_msg = {}
                    child_maintop2_msg["detect_level"]=values['detect_level']
                    if goal_pos != []:
                        child_maintop2_msg["ball_x"]=goal_pos[0][0] / resize_ratio
                        child_maintop2_msg["ball_y"]=goal_pos[0][1] / resize_ratio                        
                        child_maintop2_msg["ball_change"]=None
                    elif ball_pos != []:
                        child_maintop2_msg["ball_x"]=ball_pos[0][0] / resize_ratio
                        child_maintop2_msg["ball_y"]=ball_pos[0][1] / resize_ratio                        
                    child_maintop2_msg["w"]=playground_gray_w
                    child_maintop2_msg["h"]=playground_gray_h
                    child_maintop2.send(child_maintop2_msg)


                    if values["switch_ball"]:
                        game.set_ball_image(valueToNdarray(frame_conn3).astype("uint8").reshape((BALL_S,BALL_S,3)))
                    else:
                        game.set_ball_image()
                    game.draw(playground)

                    if values["vs_mode"] != vs_mode_pre:
                        game.reset_score()
                        if values["vs_mode"]:
                            pass                           
                        else:
                            window.FindElement('score1').Update('---')
                            window.FindElement('score2').Update('---')

                    if values['flip_text']:
                        playground = playground[:,::-1,:].copy()
                    if values["vs_mode"]:
                        score = game.get_score()
                        window.FindElement('score1').Update(str(score[1]))
                        window.FindElement('score2').Update(str(score[0]))
                        if values['flip_text']:
                            cv2.putText(playground,str(score[1]),(playground_w-50,50),cv2.FONT_HERSHEY_SIMPLEX,1.0,(255,0,0),thickness=2)
                            cv2.putText(playground,str(score[0]),(30,playground_h-30),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255),thickness=2)
                        else:
                            cv2.putText(playground,str(score[1]),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1.0,(255,0,0),thickness=2)
                            cv2.putText(playground,str(score[0]),(playground_w-50,playground_h-30),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255),thickness=2)    
                            #cv2.putText(playground,str(score[1]),(int(playground_w/2)-10,int(playground_h/2)-30),cv2.FONT_HERSHEY_SIMPLEX,1.0,(255,0,0),thickness=2)
                            #cv2.putText(playground,str(score[0]),(int(playground_w/2)-10,int(playground_h/2)+30),cv2.FONT_HERSHEY_SIMPLEX,1.0,(0,0,255),thickness=2)    
                    else:
                        cooperate_score = game.get_cooperate_score()
                        cv2.putText(playground,str(cooperate_score),(int(playground_w/2)-30,int(playground_h/2)+25),cv2.FONT_HERSHEY_SIMPLEX,3.0,(255,0,0),thickness=10)
                        
                if 1:
                    if (values['flip_screen'] and (not values['flip_text'])) or ((not values['flip_screen']) and values['flip_text']):
                        playground = playground[:,::-1,:]
                    if values['full_screen']:
                        if playground_h * 16 / 9 > playground_w:
                            cv2.imshow("KaoHockey",cv2.resize(playground,(int(SHOW_H_FULL*playground_w/playground_h),SHOW_H_FULL)))
                        else:
                            cv2.imshow("KaoHockey",cv2.resize(playground,(SHOW_W_FULL,int(SHOW_W_FULL*playground_h/playground_w))))
                    else:
                        cv2.imshow("KaoHockey",playground)
                    key = cv2.waitKey(30)
                else:
                    playscreen.update(data=cv2.imencode('.png', playground)[1].tobytes())

            else:
                screen_w = SHOW_W_MAIN
                screen_h = int(screen_w * h / w)
                playground_h = int(SHOW_W_SUB * playground_h / playground_w)
                playground_w = SHOW_W_SUB
                        
                screen =  cv2.resize(screen,(screen_w,screen_h))
                imgbytes = cv2.imencode('.png', screen)[1].tobytes()
                window['screen'].update(data=imgbytes)

            if status != status_pre:
                window['screen'].update(data="")
                #window.Element('switch_team').Update(disabled = status)
                #window.Element('vs_mode').Update(disabled = status)
                #window.Element('crop_left_label').Update(visible=not status)
                window.Element('crop_left').Update(visible=not status)
                #window.Element('crop_right_label').Update(visible=not status)
                window.Element('crop_right').Update(visible=not status)
                #window.Element('crop_top_label').Update(visible=not status)
                window.Element('crop_top').Update(visible=not status)
                #window.Element('crop_bottom_label').Update(visible=not status)
                window.Element('crop_bottom').Update(visible=not status)
                if status == MODE_PLAY:
                    crop_grab = [crop_top,crop_bottom,crop_left,crop_right]
                    crop_grab_size = (crop_right-crop_left)*(crop_bottom-crop_top)*3
                    child_maintop2.send({"detect_mode":values['detect_mode']})
                    game = Game(playground_w,playground_h)
                    game.set_ball_num(values["ball_num"])
                    game.set_ball_image()
                    game.setup()
                    playSound("decision26.wav")
                    window['playground'].update(data="")
                else:
                    crop_grab = None
                    game = None
                    score = [0,0]
                    window['playground'].update(data="")
                child_maintop1.send({"crop_grab":crop_grab})

            elapsed_times.append(time.time() - start)
            if count%FPS == 0:
                print("elapsed_time main(FBS):{0:.0f}".format(sum(elapsed_times)*1000./FPS) + "[msec] {0:.0f}[fps]".format(FPS * 1.0/ sum(elapsed_times)))
                print(score)
                elapsed_times = []
            count += 1
            status_pre = status
            vs_mode_pre = values["vs_mode"]
        except:
            break

    child_maintop1.send({"exit":None})
    child_maintop2.send({"exit":None})

    p1.join()
    p2.join()
    window.close()
    cv2.destroyAllWindows()
    print("Finished")
    return 0

def make_bar(detected_eyes,values):
    #bar H to V
    out = []
    for i in detected_eyes:
        if values["switch_team"]:
            out.append([i[0]+i[2]/2,i[1],i[0]+i[2]/2,i[1]+i[3]])
        else:
            out.append([i[0],i[1]+i[3]/4,i[0]+i[2],i[1]+i[3]/4])
    return out



def extend_eyes(detected_eyes,values):
    out = []
    a = values["bar_assist"]
    for i in detected_eyes:
        out.append([i[0]-a,i[1]-a//2,i[2]+2*a,i[3]+2*a])
    return out

def draw_goal(screen,l,t,r,b,values):
    if values["switch_team"]:
        cv2.line(screen,(l,t),(l,b),(200,0,0),GOAL_WIDTH)
        cv2.line(screen,(r,t),(r,b),(0,0,200),GOAL_WIDTH)
    else:
        cv2.line(screen,(l,t),(r,t),(200,0,0),GOAL_WIDTH)
        cv2.line(screen,(l,b),(r,b),(0,0,200),GOAL_WIDTH)
    return
"""
    if values["bound1"] == "Team1":
        cv2.line(screen,(l,t),(l,b),(200,0,0),GOAL_WIDTH)
    if values["bound1"] == "Team2":
        cv2.line(screen,(l,t),(l,b),(0,0,200),GOAL_WIDTH)
    if values["bound2"] == "Team1":
        cv2.line(screen,(l,t),(r,t),(200,0,0),GOAL_WIDTH)
    if values["bound2"] == "Team2":
        cv2.line(screen,(l,t),(r,t),(0,0,200),GOAL_WIDTH)
    if values["bound3"] == "Team1":
        cv2.line(screen,(r,t),(r,b),(200,0,0),GOAL_WIDTH)
    if values["bound3"] == "Team2":
        cv2.line(screen,(r,t),(r,b),(0,0,200),GOAL_WIDTH)
    if values["bound4"] == "Team1":
        cv2.line(screen,(l,b),(r,b),(200,0,0),GOAL_WIDTH)
    if values["bound4"] == "Team2":
        cv2.line(screen,(l,b),(r,b),(0,0,200),GOAL_WIDTH)
"""

def get_goal(values):
    buf = [None,None,None,None]
    if values["switch_team"]:
        if values['vs_mode']:
            buf[0] = 0
            buf[2] = 1
        else:
            buf[0] = 0
            buf[2] = 0
    else:
        if values['vs_mode']:
            buf[1] = 0
            buf[3] = 1 
        else:
            buf[1] = 0
            buf[3] = 0
    return buf
"""
    if values["bound1"] == "Team1":
        buf[0] = 0
    if values["bound1"] == "Team2":
        buf[0] = 1
    if values["bound2"] == "Team1":
        buf[1] = 0
    if values["bound2"] == "Team2":
        buf[1] = 1
    if values["bound3"] == "Team1":
        buf[2] = 0
    if values["bound3"] == "Team2":
        buf[2] = 1
    if values["bound4"] == "Team1":
        buf[3] = 0
    if values["bound4"] == "Team2":
        buf[3] = 1 
"""

if __name__ == '__main__':
    argvs=sys.argv
    print(argvs)
    main()


