from argparse import ArgumentParser
from pathlib import Path
import threading
from block_parser import Parser
from placer import Placer

from viewplacement import ViewPlacement

queue=[]

def render(place,skip):
    viewer=ViewPlacement(render_speed=5,skip=skip)
    stop=False
    while len(place.thread_queue)>0 and not stop:
        n=2+viewer.get_skip()
        pop=place.thread_queue.pop(0)
        #stop=viewer.live_plot(place.iter[:n:skip],place.area_trac[:n:skip],count=place.iter[n],name="floorplan")
        stop=viewer.view_result(x=place.iter[:n:skip],y=place.area_trac[:n:skip],blocks=pop[0],width=pop[1],height=pop[2],name="floorplan",count=place.iter[n])
        n=n+(skip+1)


def stats(place):
    total=place.mov0+place.mov1+place.mov2
    print("Total moves made: "+str(total))
    print("Number of accepted op1: "+str(place.mov0)+" "+str(round((place.mov0/total)*100,2))+" %")
    print("Number of accepted op2: "+str(place.mov1)+" "+str(round((place.mov1/total)*100,2))+" %")
    print("Number of accepted op3: "+str(place.mov2)+" "+str(round((place.mov2/total)*100,2))+" %")


parser = ArgumentParser()
parser.add_argument("-s","--show",action="store_true",help="display floorplanning process")
parser.add_argument("-input",help="intput block file")
parser.add_argument("-output",help="output file name")
parser.add_argument("-skip",help="skip steps in floorplanning to display")
args=parser.parse_args()
path=Path(args.input)
outpath=Path(args.output)


if args.input:
    bp=Parser(path=path)
    if args.output:
        op_path=Path(args.output)
    else:
        op_path=Path(path.name.split(".")[0]+".out")
    if args.skip:
        show_skip=int(args.skip)
    else:
        show_skip=0
    place=Placer(blocks=bp.blocks,softy=bp.softy)
    final_area, black_area, width, height, blocks=place.compute_coord(place.sa_engine())
    print("Percent black area: "+str(round(black_area/final_area,2)*100)+" %")
    plot_thread=threading.Thread(target=place.show_plots)
    place.show_plots()
    #plot_thread.start()
    stats(place=place)
    #t1.join()
    #ViewPlacement().view_result(blocks=blocks,width=width,height=height,name="Final")
    with open(outpath,encoding="utf-8",mode="w") as output:
        #output.write("Pol: "+place.polsh_expr)
        output.write("Final area = "+str(final_area)+"\n")
        output.write("Black area = "+str(black_area))
        output.write("\n\n")
        output.write("block_name lower_left(x,y)coordinate upper_right(x,y)coordinate\n")
        for k,v in blocks.items():
            output.write("sb"+k+" "+"("+str((v.x_coordinate))+","+str((v.y_coordinate))+")"+" ("+str((v.x_coordinate+v.width))+","+str((v.y_coordinate+v.length))+")\n")
    if args.show:
        render(place=place,skip=show_skip)
    #plot_thread.join()
    #view_result(outpath,width,height)

else:
    parser.print_help()