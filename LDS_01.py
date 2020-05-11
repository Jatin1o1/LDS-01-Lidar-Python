import serial
import threading
import matplotlib.pyplot as plt
import math    



ser = serial.Serial ("/dev/ttyUSB0", baudrate=230400)


def draw():
    global is_plot
    while is_plot:
        plt.figure(1)
        plt.cla()
        plt.ylim(-5000,5000)
        plt.xlim(-5000,5000)
        plt.scatter(x,y,c='r',s=8)
        plt.pause(0.001)
    plt.close("all")
    
                
is_plot = True
x=[]
y=[]
for _ in range(360):
    x.append(0)
    y.append(0)


def grab_data():
    try:
        unique_values = 0;
        distance_list = [None] * 360
        while unique_values < 360:
            result = ser.read(42)
            if (result[-1] == result[-2]):
                rpm = result[3]*256 + result[2]
                base_angle = (result[1] - 160)*6
                for m in range(6):
                    angle = base_angle + m
                    distance = result[((6*(m+1))+1)]*256 + result[((6*(m+1)))]
                    
                    if distance_list[angle] == None:
                        unique_values += 1
                        
                        if distance > 0:
                            distance_list[angle] = distance

                            if(type(x) is list):
                                x[angle]= distance * math.cos(math.radians(angle))
                                print("x = "+ str( x[angle]))
                            
                            if(type(y) is list):
                                y[angle] = distance * math.sin(math.radians(angle))
                                print("y = "+ str(y[angle]))
                            print("  ")
                            
                        else:
                           distance_list[angle] = 4200
        
    except IndexError:
        ser.write(b'e')
        print('Stopped! Out of sync.')
threading.Thread(target=draw).start()    
while 1:
    grab_data()
