import re
from cv2 import cv2
from screeninfo import get_monitors
import numpy as np
from pathlib import Path

class ViewPlacement:
    def __init__(self,skip,render_speed=10):
        self.skip=skip
        self.render_speed=render_speed
        self.show_trck_bar=True
        self.pause=False
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_size=1
        for m in get_monitors():
            if(m.is_primary):
                self.screen_w=int(m.width*0.75)
                self.screen_h=int(self.screen_w*(9/16))
        self.img = np.zeros((int(self.screen_h),int(self.screen_w),3),np.uint8)
        #print(self.img[:int(self.screen_w*0.25)][int(self.screen_w*0.75):])
        self.gr_x=int(self.screen_w*0.75)
        self.gr_y=int(self.screen_w*0.25)
        self.gr_w=int(self.screen_w*0.25)
        self.gr_h=int(self.screen_w*0.25)
        self.img[:int(self.screen_w*0.25),int(self.screen_w*0.75):]=[[(255,255,255)]*self.gr_w]*self.gr_h
        cv2.line(self.img,(self.gr_x+int(self.gr_w*0.1),self.gr_y-int(self.gr_h*0.1)),(self.gr_x+int(self.gr_w*0.9),self.gr_y-int(self.gr_h*0.1)),color=(0,0,0),thickness=4)
        cv2.line(self.img,(self.gr_x+int(self.gr_w*0.1),self.gr_y-int(self.gr_h*0.1)),(self.gr_x+int(self.gr_w*0.1),self.gr_y-int(self.gr_h*0.9)),color=(0,0,0),thickness=4)
        #cv2.createTrackbar("Render speed: ",name,0,100,self.callbck)
        
              


    def view_result(self,x,y,blocks,width,height,name,count=0):
        stop=False
        scale_x=width/(self.screen_w*0.75)
        scale_y=height/self.screen_h
        self.img[:,:int(self.screen_w*0.75)]=[[(0,0,0)]*int(self.screen_w*0.75)]*self.screen_h
        #self.img = np.zeros((int(self.screen_h),int(self.screen_w),3),np.uint8)
        #self.img[:int(self.screen_w*0.25),int(self.screen_w*0.75):]=[[(255,255,255)]*self.gr_w]*self.gr_h
        cv2.line(self.img,(self.gr_x+int(self.gr_w*0.1),self.gr_y-int(self.gr_h*0.1)),(self.gr_x+int(self.gr_w*0.9),self.gr_y-int(self.gr_h*0.1)),color=(0,0,0),thickness=2)
        cv2.line(self.img,(self.gr_x+int(self.gr_w*0.1),self.gr_y-int(self.gr_h*0.1)),(self.gr_x+int(self.gr_w*0.1),self.gr_y-int(self.gr_h*0.9)),color=(0,0,0),thickness=2)
        self.live_plot(x=x,y=y,name=name,count=count)
        
        for k,v in blocks.items():
            low_x=int(v.x_coordinate*scale_x)
            low_y=int(v.y_coordinate*scale_y)
            up_x=int((v.x_coordinate+v.width)*scale_x)
            up_y=int((v.y_coordinate+v.length)*scale_y)
            cv2.rectangle(self.img, (low_x, up_y), (up_x, low_y), color=(255,255,255), thickness=-1)
            cv2.rectangle(self.img, (low_x, up_y), (up_x, low_y), color=(0,255,0), thickness=10)
            
            cv2.imshow(name,self.img)
            if self.show_trck_bar:
                self.show_trck_bar=False
                cv2.createTrackbar("Render speed: ",name,1,1000,self.callbck)
                cv2.setTrackbarMin("Render speed: ",name,1)
                cv2.setTrackbarPos("Render speed: ",name,10)
                cv2.createTrackbar("Skip: ",name,1,100,self.skip_callbck)
                cv2.setTrackbarMin("Render speed: ",name,1)
                cv2.setTrackbarPos("Render speed: ",name,self.skip)
            if cv2.waitKey(self.render_speed) == ord(" "):
                if self.pause:
                    self.render_speed=10
                    self.pause=False
                else:
                    self.render_speed=0
                    self.pause=True
            if cv2.getWindowProperty(name,cv2.WND_PROP_VISIBLE)<1:
                stop=True
                break
        return stop
        
        """for line in coors.splitlines():
            if re.search("^sb",line):
                coordinates=line.split(" ")
                coord=coordinates[1]
                low_xy=coord[coord.find("(")+1:coord.find(")")]
                coord=coordinates[2]
                up_xy=coord[coord.find("(")+1:coord.find(")")]
                low_x=int(float(low_xy[:low_xy.find(",")])*scale_x)
                low_y=int(float(low_xy[low_xy.find(",")+1:])*scale_y)
                up_x=int(float(up_xy[:up_xy.find(",")])*scale_x)
                up_y=int(float(up_xy[up_xy.find(",")+1:])*scale_y)
                cv2.rectangle(self.img, (low_x, up_y), (up_x, low_y), color=(255,255,255), thickness=-1)
                cv2.rectangle(self.img, (low_x, up_y), (up_x, low_y), color=(0,255,0), thickness=10)"""
        #cv2.imshow("lalala", self.img)
        #k=cv2.waitKey(0)



    def live_plot(self,x,y,name,show=False,count=0):
        #y=[i for i in range(1,len(x)+1)]
        stop=False
        if len(x)==len(y):
            x_max=max(x)
            y_max=max(y)
            scale_x=(self.screen_w*0.25*0.8)/x_max
            scale_y=(self.screen_h*0.25*0.8)/y_max
            #print(scale_y)
            offset_x=int(self.gr_w*0.1)+int(self.gr_x)
            offset_y=self.gr_y-int(self.gr_h*0.1)
            start_x=offset_x
            start_y=offset_y
            #print(offset_x)
            self.img[int(self.screen_w*0.25):,int(self.screen_w*0.75):]=[[(0,0,0)]*int(self.screen_w*0.25)]*(self.screen_h-int(self.screen_w*0.25))
            cv2.putText(self.img,"Iteration "+str(count),(self.gr_x,100+self.gr_y), self.font, self.font_size,(255,255,255),2,cv2.LINE_AA)
            self.img[:int(self.screen_w*0.25),int(self.screen_w*0.75):]=[[(255,255,255)]*self.gr_w]*self.gr_h
            cv2.line(self.img,(self.gr_x+int(self.gr_w*0.1),self.gr_y-int(self.gr_h*0.1)),(self.gr_x+int(self.gr_w*0.9),self.gr_y-int(self.gr_h*0.1)),color=(0,0,0),thickness=2)
            cv2.line(self.img,(self.gr_x+int(self.gr_w*0.1),self.gr_y-int(self.gr_h*0.1)),(self.gr_x+int(self.gr_w*0.1),self.gr_y-int(self.gr_h*0.9)),color=(0,0,0),thickness=2)
            for plot_x,plot_y in zip(x,y):
                end_x=int(int(plot_x*scale_x)+offset_x)
                end_y=int(offset_y-int(plot_y*scale_y))
                #print(end_x)
                #print(int(plot_y*scale_y))
                cv2.line(self.img,(start_x,start_y),(end_x,end_y),color=(0,255,0),thickness=2)
                start_x=end_x
                start_y=end_y
                if show:
                    cv2.imshow(name,self.img)
                    cv2.waitKey(self.render_speed)
                    if cv2.waitKey(self.render_speed) == ord(" "):
                        if self.pause:
                            self.render_speed=10
                            self.pause=False
                        else:
                            self.render_speed=0
                            self.pause=True
                    if cv2.getWindowProperty(name,cv2.WND_PROP_VISIBLE)<1:
                        stop=True
                        break
        return stop
            
    def callbck(self,val):
        self.render_speed=val
    def skip_callbck(self,val):
        self.skip=val
    def get_skip(self):
        return self.skip
