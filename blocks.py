class Block: 
    def __init__(self, block_name, is_soft, length=None, width=None, area=None, min_ar=None, max_ar=None): 
        # Details of the block 
        self.block_name = block_name 
        self.is_soft = is_soft  # True for a soft-macro, None (or False) for a hard-macro 
        self.length = length 
        self.width = width 
        self.area = area if is_soft else length * width 
 
        # To keep track of slicing tree for incremental cost update 
        self.parent_block = None 
        self.left_child = None 
        self.right_child = None 
 
        # For soft-macros only, otherwise None 
        self.min_ar = min_ar if is_soft else None 
        self.max_ar = max_ar if is_soft else None
        self.ar_1 = 1 if is_soft and max_ar>1 and min_ar<1 else None
        self.optimal_aspect_ratio = None  # the optimal aspect ratio  
        # To print the coordinates of each block. 
        self.x_coordinate = 0.0  # lower left 
        self.y_coordinate = 0.0  # lower left 