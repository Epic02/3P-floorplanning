import random
import copy
import re
import math
import matplotlib.pyplot as mp
from viewplacement import ViewPlacement
import time
import threading


BOLTZ_CON=(1.38*(10**(-23)))
class Placer:
    def __init__(self,blocks,softy):
        self.NUM_OF_MOVES=300
        self.blocks=blocks
        self.block_dict={}
        self.polsh_expr=self.rows_1_1()
        self.softy=softy
        self.cool_slow=0
        self.T0=0
        self.decay_rate=0.9
        self.s1=0
        self.s2=self.NUM_OF_MOVES-1
        self.cost_decrease=0
        #Variables For analysis
        self.start=0
        self.end=0
        self.trac_d_cost=[]
        self.boltz_trac=[]
        self.area_trac=[]
        self.T_trac=[]
        self.trac_r=[]
        self.block_ratios=[]
        self.cost_accptd=[]
        self.temp_accptd=[]
        self.accptd_move_pc=[]
        self.once=True
        self.iter=[]
        self.thread_queue=[]
        self.sa_engine_on=False
        self.mov0=0
        self.mov1=0
        self.mov2=0
    def get_polsh_expr(self):
        return self.polsh_expr
    def rows_1_1(self):
        row_size=int(math.sqrt(len(self.blocks)))
        #print(row_size)
        row_size_flt=math.sqrt(len(self.blocks))
        start=0
        end=row_size
        rows=[]
        pol_expr=""
        for i in range(row_size):
            row=""
            for n,bl in enumerate(self.blocks[start:end]):
                self.block_dict[bl.block_name]=bl
                if n==1:
                    row=row+self.blocks[start].block_name+" "+bl.block_name+" | "
                elif n>1:
                    row=row+bl.block_name+" | "
            rows.append(row)
            start=start+row_size
            #print(start)
            end=end+row_size
        #print(start)
        #print(self.blocks[start:])
        if row_size_flt>row_size:
            row=""
            if len(self.blocks[start:])==1:
                self.block_dict[self.blocks[start].block_name]=self.blocks[start]
                row=row+self.blocks[start].block_name+" "
            else:
                for n,bl in enumerate(self.blocks[start:]):
                    self.block_dict[bl.block_name]=bl
                    if n==1:
                        row=row+self.blocks[start].block_name+" "+bl.block_name+" | "
                    elif n>1:
                        row=row+bl.block_name+" | "
            rows.append(row)
        #print(rows)
        for i,row_i in enumerate(rows):
            if i==1:
                pol_expr=pol_expr+rows[0]+row_i+"- "
            elif i>1:
                pol_expr=pol_expr+row_i+"- "
        #print("1x1:"+pol_expr)
        return pol_expr.strip()

        
    def compute_coord(self,pol_expr):
        blocks=copy.deepcopy(self.block_dict)
        stack=[]
        split_pol=pol_expr.strip().split(" ")
        for blk in self.block_ratios:
            blocks[blk[0]].length=blk[1][1]
            blocks[blk[0]].width=blk[1][0]
        for op in split_pol:
            if op in ("|","-"):
                sv1=stack.pop()
                sv2=stack.pop()
                w_h=True if op=="|" else False
                if isinstance(sv1,dict) and isinstance(sv2,dict):
                    if op=="|":
                        if split_pol[0] in sv1["blocks"]:
                            for block in sv2["blocks"]:
                                blocks[block].x_coordinate=blocks[block].x_coordinate+sv1["width"]
                        elif split_pol[0] in sv2["blocks"]:
                            for block in sv1["blocks"]:
                                blocks[block].x_coordinate=blocks[block].x_coordinate+sv2["width"]
                        sv1["width"]=sv1["width"]+sv2["width"]
                        sv1["height"]=max(sv1["height"],sv2["height"])
                        sv1["blocks"]=sv1["blocks"]+sv2["blocks"]
                        stack.append(sv1)
                    else:
                        if split_pol[0] in sv1["blocks"]:
                            for block in sv2["blocks"]:
                                blocks[block].y_coordinate=blocks[block].y_coordinate+sv1["height"]
                        elif split_pol[0] in sv2["blocks"]:
                            for block in sv1["blocks"]:
                                blocks[block].y_coordinate=blocks[block].y_coordinate+sv2["height"]
                        sv1["height"]=sv1["height"]+sv2["height"]
                        sv1["width"]=max(sv1["width"],sv2["width"])
                        sv1["blocks"]=sv1["blocks"]+sv2["blocks"]
                        stack.append(sv1)
                elif isinstance(sv1,dict) and not isinstance(sv2,dict):
                    print("Happens "+sv2)
                    print("Blocks: "+str(sv1["blocks"]))
                elif not isinstance(sv1,dict) and isinstance(sv2,dict):  
                    if op=="|":
                        blocks[sv1].x_coordinate=blocks[sv1].x_coordinate+sv2["width"]
                        sv2["width"]=sv2["width"]+blocks[sv1].width
                        sv2["height"]=max(sv2["height"],blocks[sv1].length)
                        sv2["blocks"].append(sv1)
                    else:
                        blocks[sv1].y_coordinate=blocks[sv1].y_coordinate+sv2["height"]
                        sv2["height"]=sv2["height"]+blocks[sv1].length
                        sv2["width"]=max(sv2["width"],blocks[sv1].width)
                        sv2["blocks"].append(sv1)
                    stack.append(sv2)
                else:
                    temp={}
                    temp["width"]=sum([blocks[sv1].width,blocks[sv2].width]) if w_h else max(blocks[sv1].width,blocks[sv2].width)
                    temp["height"]=max([blocks[sv1].length,blocks[sv2].length]) if w_h else sum([blocks[sv1].length,blocks[sv2].length])
                    temp["blocks"]=[sv1,sv2]
                    
                    if op=="|":
                        blocks[sv1].x_coordinate=blocks[sv1].x_coordinate+blocks[sv2].width
                    else:
                        blocks[sv1].y_coordinate=blocks[sv1].y_coordinate+blocks[sv2].length
                    stack.append(temp)
            else:
                stack.append(op)
        final_area=stack[0]["width"]*stack[0]["height"]
        black_area=final_area-self.fill_area()
        #print("Time taken: "+str(round((self.end-self.start)*(10**(-9)),3))+" s")
        #print("MAX: "+str(max(self.trac_d_cost)))
        #print("Percentage of black area: "+str(round(black_area/final_area,2)*100)+" %")
        #print("MIN: "+str(max(self.trac_d_cost)))
        return final_area,black_area,stack[0]["width"],stack[0]["height"],blocks
    def get_area_hard_rot(self,pol_expr,debug=False):
        stack=[]
        for blk in pol_expr.strip().split(" "):
            if blk in ("-","|"):
                sv1=stack.pop()
                sv2=stack.pop()
                candidates=[]
                for sv in [sv2,sv1]:
                    if not isinstance(sv,dict):
                        temp=[]
                        temp.append(sv)
                        temp.append((float(self.block_dict[sv].width),float(self.block_dict[sv].length)))
                        temp.append((float(self.block_dict[sv].length),float(self.block_dict[sv].width)))
                        candidates.append(temp)
                    else:
                        candidates.append(sv) 
                stack.append(self.optimal_ratios(candidates,blk)) 
            else:
                stack.append(blk)
        min_area_key=self.get_min_area(stack[0])
        self.block_ratios=stack[0][min_area_key[1]]
        return min_area_key[0]
    def get_area_hard(self,pol_expr,debug=False):
        """Computes the area of the polish expression"""
        stack=[]
        #print(pol_expr)
        for op in pol_expr.strip().split(" "):
            if debug:
                print("Stack: "+str(stack))
            if op in ("|","-"):
                sv1=stack.pop()
                sv2=stack.pop()
                sum_this="width" if op=="|" else "height"
                max_this="height" if op=="|" else "width"
                w_h=True if op=="|" else False
                if isinstance(sv1,dict) and isinstance(sv2,dict):
                    sv1[sum_this]=sv1[sum_this]+sv2[sum_this]
                    if sv2[max_this]>sv1[max_this]:
                        sv1[max_this]=sv2[max_this]
                    stack.append(sv1)
                elif isinstance(sv1,dict) and not isinstance(sv2,dict):
                    sv1[sum_this]=sv1[sum_this]+(self.block_dict[sv2].width if w_h else self.block_dict[sv2].length)
                    val1=(self.block_dict[sv2].length if w_h else self.block_dict[sv2].width)
                    if val1>sv1[max_this]:
                        sv1[max_this]=val1
                    stack.append(sv1)
                elif not isinstance(sv1,dict) and isinstance(sv2,dict):
                    sv2[sum_this]=sv2[sum_this]+(self.block_dict[sv1].width if w_h else self.block_dict[sv1].length)
                    val1=(self.block_dict[sv1].length if w_h else self.block_dict[sv1].width)
                    if val1>sv2[max_this]:
                        sv2[max_this]=val1
                    stack.append(sv2)
                else:
                    temp={}
                    temp[sum_this]=(self.block_dict[sv1].width if w_h else self.block_dict[sv1].length)+(self.block_dict[sv2].width if w_h else self.block_dict[sv2].length)
                    val1=(self.block_dict[sv1].length if w_h else self.block_dict[sv1].width)
                    val2=(self.block_dict[sv2].length if w_h else self.block_dict[sv2].width)
                    temp[max_this]=max(val1,val2)
                    stack.append(temp)
            else:
                stack.append(op)
        return stack[0]["width"]*stack[0]["height"]
    
    def get_area_soft(self,pol_expr):
        """Solves floorplan sizing problem for soft macros"""
        stack=[]
        for blk in pol_expr.strip().split(" "):
            if blk in ("-","|"):
                sv1=stack.pop()
                sv2=stack.pop()
                candidates=[]
                for sv in [sv2,sv1]:
                    if not isinstance(sv,dict):
                        temp=[]
                        temp.append(sv)
                        if not self.block_dict[sv].ar_1 is None:
                            temp.append(self.get_w_h(area=self.block_dict[sv].area,
                                                        ar=1))
                        if self.block_dict[sv].max_ar==self.block_dict[sv].min_ar:
                            temp.append(self.get_w_h(area=self.block_dict[sv].area,
                                                        ar=self.block_dict[sv].max_ar))
                        else:
                            temp.append(self.get_w_h(area=self.block_dict[sv].area,
                                                        ar=self.block_dict[sv].max_ar))
                            temp.append(self.get_w_h(area=self.block_dict[sv].area,
                                                        ar=self.block_dict[sv].min_ar))
                        candidates.append(temp)
                    else:
                        candidates.append(sv) 
                stack.append(self.optimal_ratios(candidates,blk)) 
            else:
                stack.append(blk)
        min_area_key=self.get_min_area(stack[0])
        #print(stack[0][min_area_key[1]])
        self.block_ratios=stack[0][min_area_key[1]]
        return min_area_key[0]
    
    def get_area(self,pol_expr,debug=False):
        """Calculates area based on type of blocks"""
        if self.softy:
            return self.get_area_soft(pol_expr)
        else:
            return self.get_area_hard_rot(pol_expr,debug=debug)
    
    def optimal_ratios(self,candidates,operation):
        temp={}
        i=0
        j=0
        k=0
        l=0
        if isinstance(candidates[0],list) and isinstance(candidates[1],list):
            a=candidates[0][1:]
            b=candidates[1][1:]
            self.sort(a,operation)
            self.sort(b,operation)
            
            #print(a)
            #print(b)
            if self.once:
                print(a)
                self.once=False
            while k<len(a) and l<len(b):
                i=k
                j=l
                if operation == "|":
                    dimension=(a[i][0]+b[j][0],max(a[i][1],b[j][1]))
                    as_r=str(dimension[0])+"_"+str(dimension[1])
                    temp[as_r]=[(candidates[0][0],a[i]),(candidates[1][0],b[j])]
                    #print("i: "+str(a[i][1])+" j: "+str(j))
                    if max(a[i][1],b[j][1])==b[j][1]:
                        l=l+1
                    if max(a[i][1],b[j][1])==a[i][1]:
                        k=k+1
                elif operation=="-":
                    dimension=(max(a[i][0],b[j][0]),a[i][1]+b[j][1])
                    as_r=str(dimension[0])+"_"+str(dimension[1])
                    temp[as_r]=[(candidates[0][0],a[i]),(candidates[1][0],b[j])]
                    if max(a[i][0],b[j][0])==b[j][0]:
                        l=l+1
                    if max(a[i][0],b[j][0])==a[i][0]:
                        k=k+1
            return temp
        elif isinstance(candidates[0],list) and isinstance(candidates[1],dict):
            a=self.sort(candidates[0][1:],operation)
            b=[]
            for d in candidates[1].keys():
                w_h=d.split("_")
                b.append((float(w_h[0]),float(w_h[1])))
            b=self.sort(b,operation)
            while k<len(a) and l<len(b):
                i=k
                j=l
                if operation == "|":
                    dimension=(a[i][0]+b[j][0],max(a[i][1],b[j][1]))
                    as_r=str(dimension[0])+"_"+str(dimension[1])
                    backtrace=candidates[1][str(b[j][0])+"_"+str(b[j][1])]
                    temp[as_r]=[(candidates[0][0],a[i])]+backtrace
                    if max(a[i][1],b[j][1])==b[j][1]:
                        l=l+1
                    if max(a[i][1],b[j][1])==a[i][1]:
                        k=k+1
                elif operation=="-":
                    dimension=(max(a[i][0],b[j][0]),a[i][1]+b[j][1])
                    as_r=str(dimension[0])+"_"+str(dimension[1])
                    backtrace=candidates[1][str(b[j][0])+"_"+str(b[j][1])]
                    temp[as_r]=[(candidates[0][0],a[i])]+backtrace
                    if max(a[i][0],b[j][0])==b[j][0]:
                        l=l+1
                    if max(a[i][0],b[j][0])==a[i][0]:
                        k=k+1
        elif isinstance(candidates[0],dict) and isinstance(candidates[1],list):
            b=self.sort(candidates[1][1:],operation)
            a=[]
            for d in candidates[0].keys():
                w_h=d.split("_")
                a.append((float(w_h[0]),float(w_h[1])))
            a=self.sort(a,operation)
            while k<len(a) and l<len(b):
                i=k
                j=l
                if operation == "|":
                    #print(a)
                    #print("i: "+str(i)+" j: "+str(j))
                    dimension=(a[i][0]+b[j][0],max(a[i][1],b[j][1]))
                    as_r=str(dimension[0])+"_"+str(dimension[1])
                    #print(candidates[0])
                    backtrace=candidates[0][str(a[i][0])+"_"+str(a[i][1])]
                    temp[as_r]=[(candidates[1][0],b[j])]+backtrace
                    if max(a[i][1],b[j][1])==b[j][1]:
                        l=l+1
                    if max(a[i][1],b[j][1])==a[i][1]:
                        k=k+1
                elif operation=="-":
                    dimension=(max(a[i][0],b[j][0]),a[i][1]+b[j][1])
                    as_r=str(dimension[0])+"_"+str(dimension[1])
                    backtrace=candidates[0][str(a[i][0])+"_"+str(a[i][1])]
                    temp[as_r]=[(candidates[1][0],b[j])]+backtrace
                    if max(a[i][0],b[j][0])==b[j][0]:
                        l=l+1
                    if max(a[i][0],b[j][0])==a[i][0]:
                        k=k+1
        elif isinstance(candidates[0],dict) and isinstance(candidates[1],dict):
            b=[]
            for d in candidates[1].keys():
                w_h=d.split("_")
                b.append((float(w_h[0]),float(w_h[1])))
            b=self.sort(b,operation)
            a=[]
            for d in candidates[0].keys():
                w_h=d.split("_")
                a.append((float(w_h[0]),float(w_h[1])))
            a=self.sort(a,operation)
            while k<len(a) and l<len(b):
                i=k
                j=l
                if operation == "|":
                    dimension=(a[i][0]+b[j][0],max(a[i][1],b[j][1]))
                    as_r=str(dimension[0])+"_"+str(dimension[1])
                    backtrace1=candidates[0][str(a[i][0])+"_"+str(a[i][1])]
                    backtrace2=candidates[1][str(b[j][0])+"_"+str(b[j][1])]
                    temp[as_r]=backtrace1+backtrace2
                    if max(a[i][1],b[j][1])==b[j][1]:
                        l=l+1
                    if max(a[i][1],b[j][1])==a[i][1]:
                        k=k+1
                elif operation=="-":
                    dimension=(max(a[i][0],b[j][0]),a[i][1]+b[j][1])
                    as_r=str(dimension[0])+"_"+str(dimension[1])
                    backtrace1=candidates[0][str(a[i][0])+"_"+str(a[i][1])]
                    backtrace2=candidates[1][str(b[j][0])+"_"+str(b[j][1])]
                    temp[as_r]=backtrace1+backtrace2
                    if max(a[i][0],b[j][0])==b[j][0]:
                        l=l+1
                    if max(a[i][0],b[j][0])==a[i][0]:
                        k=k+1
        return temp

    def get_min_area(self,cand_ratios):
        cr=list(cand_ratios.keys())
        min_i=0
        w_h=cr[min_i].split("_")
        min_area=float(w_h[0])*float(w_h[1])
        for d in range(1,len(cr)):
            w_h=cr[d].split("_")
            area=float(w_h[0])*float(w_h[1])
            if min_area>area:
                min_area=area
                min_i=d
        return (min_area,cr[min_i])




    def get_w_h(self,area,ar):
        height=math.sqrt(area/ar)
        return (ar*height,height)
    
    def sort(self,arr,opr):
        w_h= 0 if opr=="|" else 1
        n = len(arr)
        
        # Traverse through all array elements
        for i in range(n):
            swapped = False

            # Last i elements are already in place
            for j in range(0, n-i-1):

                # Traverse the array from 0 to n-i-1
                # Swap if the element found is greater
                # than the next element
                if arr[j][w_h] > arr[j+1][w_h]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
                    swapped = True
            if (swapped == False):
                break
        return arr
    def sa_engine(self):
        """The simulated annealing engine"""
        currSol=self.polsh_expr

        #print("Area Before Annling: "+str(self.get_area(self.polsh_expr)))
        #print("Currsol: "+currSol)
        self.sa_engine_on=True
        avg_change=self.avg_change()
        print("Avg Change: "+str(avg_change))
        T=self.get_T0(avg_change)
        self.T0=T
        print("T0: "+str(T))
        T_frz=self.get_Tfrz(avg_change)
        print("T_frz: "+str(T_frz)) 
        count=0
        self.start=time.time_ns()
        iter=0
        #t1=threading.Thread(target=self.render)
        #t1.daemon=True
        #t1.start()
        while T>T_frz:
            for i in range(self.NUM_OF_MOVES):
                next_sol=self.perturb(pol_expr=currSol)
                cost=self.get_area(next_sol)
                delta_cost=self.get_area(next_sol)-self.get_area(currSol)
                self.trac_d_cost.append(delta_cost)
                
                if self.acceptMov(d_cost=delta_cost,T=T):
                    count=count+1
                    currSol=next_sol
                    self.iter.append(count)
                    self.cost_accptd.append(cost)
                    self.temp_accptd.append(T)
                    self.area_trac.append(self.get_area(currSol))
                    final_area, black_area, width, height,blocks=self.compute_coord(currSol)
                    self.thread_queue.append((blocks,width,height))
            self.accptd_move_pc.append((count/self.NUM_OF_MOVES)*100)
            self.T_trac.append(T)
            T=self.coolDown(T=T)
        #t1.join()
        self.end=time.time_ns()
        return currSol
    def acceptMov(self,d_cost,T):
        """Decides move acceptance"""
        if d_cost<0:
            return True
        else:
            boltz=math.exp(-(d_cost/(BOLTZ_CON*T)))
            self.boltz_trac.append(boltz)
            r=random.uniform(0,1)
            self.trac_r.append(r)
            if r<boltz:
                #self.trac_r.append(r)
                return True
            else:
                return False
    
    def coolDown(self,T):
        """Decreases temperature based on cooldown schedule"""
        #self.cool_slow=self.cool_slow+1
        #if T<self.T0*0.5:
        #    temp=0.9*T
        #    self.NUM_OF_MOVES=300
        #else:
        #self.s2=len(self.area_trac)-1
        #ratio=self.area_trac[self.s2]/self.area_trac[self.s1]
        #self.s1=self.s2
        #if ratio>1:
        #    self.decay_rate=self.decay_rate-0.1
        #else:
        #    if self.decay_rate<0.9:
        #        self.decay_rate=self.decay_rate+0.1
        #if T>(self.T0*0.1):
        #    temp=0.9*T
        #else:
        #    temp=0.9*T
        #if temp==0 or temp<0:
        #    print("True")
        return self.decay_rate*T
        #return (100*T)**(-2)
        #if self.cool_slow>10:
        #    return 0.6*T
        #else:
            #self.NUM_OF_MOVES=300
        #    return 0.5*T
    def perturb(self,pol_expr,inc_2=True):
        """Perform on of the 3 perturbations at random"""
        move=random.randint(0,2)#(2 if inc_2 else 1))
        #print("Move: "+str(move))
        if move==0:
            self.mov0=self.mov0+1
            pol_split=pol_expr.split(" ")
            possible_swap=list(re.finditer("(?=((\s)(\d+)((\s|\||-)+)(\d+)))",pol_expr))
            swap=random.randint(0,len(possible_swap)-1)
            #print(possible_swap[swap].group(1))
            swap_v=possible_swap[swap].group(1).strip().split(" ")
            #print(swap_v)
            for n,i in enumerate(pol_split):
                if i==swap_v[0]:
                    s1=n
                if i==swap_v[len(swap_v)-1]:
                    s2=n
            temp=pol_split[s1]
            pol_split[s1]=pol_split[s2]
            pol_split[s2]=temp
            #pol_expr=" ".join(pol_split)
            return " ".join(pol_split)
        elif move==1:  #Complement operands
            self.mov1=self.mov1+1
            pol_split=pol_expr.split(" ")
            oprnd_interval=random.sample(range(0,len(self.blocks)),2)
            comp=0
            for n,oprnd in enumerate(pol_split):
                if oprnd in (str(oprnd_interval[0]),str(oprnd_interval[1])):
                    comp=comp+1
                if comp==1 and (oprnd=="|" or oprnd=="-"):
                    pol_split[n]="-" if oprnd=="|" else "|"
                elif comp==2:
                    break
            #self.polsh_expr=" ".join(pol_split)
            return " ".join(pol_split)
        elif move==2:
            valid=False
            pol_split=(pol_expr+" ").split(" ")
            possible_swap=re.findall("(\d+) (\||-)",pol_expr)#re.findall("(\||-) (\d+)",pol_expr)
            possible_swap1=re.findall("(\||-) (\d+)",pol_expr)
            #print(re.findall("(\||-) (\d+)",pol_expr).reverse())
            i=0
            cover=False
            while not valid and i<len(possible_swap)+len(possible_swap1):
                #ps=random.randint(0,1)
                #swap_loc=random.randint(0,len(possible_swap)-1 if ps else len(possible_swap)-1)
                #print(possible_swap1[swap_loc])
                if i==len(possible_swap):
                    possible_swap=possible_swap1
                    cover=True
                blk_name=possible_swap[i-len(possible_swap) if cover else i][int(cover)]
                #print("blk: "+str(swap_loc)+" "+str(len(pol_split)))
                for n,oprtor in enumerate(pol_split):
                    #print(n)
                    if oprtor==blk_name:
                        temp=pol_split[n]
                        #print(oprtor+" "+blk_name+" "+pol_split[n])
                        pol_split[n]=pol_split[n-1 if cover else n+1]
                        pol_split[n-1 if cover else n+1]=temp
                        if self.is_valid(pol_split):
                            valid=True
                            break
                        else:
                            temp=pol_split[n-1 if cover else n+1]
                            pol_split[n-1 if cover else n+1]=pol_split[n]
                            pol_split[n]=temp
                if not valid:
                    i=i+1
            #self.polsh_expr=" ".join(pol_split)
            if i==len(possible_swap)+len(possible_swap1):
                self.perturb(pol_expr=pol_expr,inc_2=False)
            else:
                self.mov2=self.mov2+1
                return " ".join(pol_split)
    def is_valid(self,pol_expr):
        """Checks if polish expressin is valid"""
        #pol_expr=expr.split(" ")
        count=0
        for op in pol_expr:
            if op.isnumeric():
                count=count+1
            elif op in ("|","-"):
                count=count-1
            #print("Count: "+str(count))
            if count<=0:
                break
        if count==1:
            return True
        else:
            return False
    def avg_change(self):
        currSol=self.polsh_expr
        sum_d=0
        for i in range(1000):
            next_sol=self.perturb(pol_expr=currSol)
            #cost=self.get_area(next_sol)
            delta_cost=self.get_area(next_sol)-self.get_area(currSol)
            sum_d=sum_d+delta_cost
            currSol=next_sol
        return sum_d/1000


    def get_T0(self,d_cost):
        #print("area T0: "+str(self.get_area(pol_expr=pol_expr)))
        #print("Log :"+str(math.log(0.99)))
        
        return (((-1)*(d_cost))/((1.38*(10**(-23)))*math.log(0.9)))
    def get_Tfrz(self,d_cost):
        #print("Log :"+str(math.log(0.00001)))
        return (((-1)*(d_cost))/((1.38*(10**(-23)))*math.log(0.0000001)))
        #return ((-1)*564061)/((1.38*(10**(-23)))*math.log(0.00001))*0.1
    def fill_area(self):
        area=0.0
        for blk in self.blocks:
            area=area+blk.area
        return area
    def show_plots(self):
        mp.figure(1)
        mp.subplot(2,2,1).set_title("Delta Cost")
        mp.plot(self.trac_d_cost)
        mp.subplot(2,2,2).set_title("Probability")
        mp.plot(self.boltz_trac)
        #mp.plot(self.trac_r)
        mp.subplot(2,2,3).set_title("Area cost")
        mp.plot(self.area_trac)
        #mp.plot(self.T_trac)
        print("Temps drops: "+str(len(self.T_trac)))
        mp.subplot(2,2,4).set_title("Temperature")
        mp.plot(self.T_trac)
        mp.title("Blocks: "+str(len(self.blocks)))
        #mp.show()
        mp.figure(2)
        mp.subplot(2,2,1).set_title("Cost vs Iteration")
        mp.plot(self.cost_accptd)
        mp.subplot(2,2,2).set_title("Temperature vs Iteration")
        mp.plot(self.temp_accptd)
        mp.subplot(2,2,3).set_title("Percent of accepted moves")
        mp.plot(self.accptd_move_pc)
        mp.show()

    
