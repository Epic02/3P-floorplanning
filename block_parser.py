import re
from blocks import Block
NUM_SOFT_STR="NumSoftRectangularBlocks : "
NUM_HARD_STR="NumHardRectilinearBlocks : "
class Parser:
    "Class to parse block files and extract information"
    def __init__(self,path):
        self.path=path
        self.blocks=[]
        self.num_hrdblks=0
        self.num_sftblks=0
        self.softy=self.parse()

    def parse(self):
        """Parses the .blocks file"""
        num=0
        with self.path.open(mode="r",encoding="utf-8") as blks:
            blk=blks.read()
            for line in blk.splitlines():
                if re.search("^sb",line):
                    parameters=re.split("(?<!,)\s+",line)
                    is_soft=True if re.search("^soft",parameters[1].strip()) else False
                    block_name=str(num)
                    if is_soft:
                        #print(parameters)
                        min_ar=float(parameters[3])
                        max_ar=float(parameters[4])
                        self.blocks.append(Block(is_soft=is_soft,
                                        block_name=block_name,
                                        area=float(parameters[2]),
                                        min_ar=min_ar,
                                        max_ar=max_ar))
                        
                    else:
                        width,height=self.get_hght_wdth(parameters[5])
                        self.blocks.append(Block(is_soft=is_soft,
                                                block_name=block_name,
                                                length=height,
                                                width=width))
                    num=num+1
                elif re.search("^"+NUM_HARD_STR,line):
                    self.num_hrdblks=int(line[len(NUM_HARD_STR):].strip())
                elif re.search("^"+NUM_SOFT_STR,line):
                    self.num_sftblks=int(line[len(NUM_SOFT_STR):].strip())
        return is_soft
                           

    def get_hght_wdth(self,coo):
        """Extracts the width and height of the blocks from the x and y coordinates"""

        x_y=coo[coo.find("(")+1:coo.find(")")]
        w_h=x_y.split(",")
        return int(w_h[0].strip()),int(w_h[1].strip())