class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        #i can iterate through all rows first, map the exisitng numbers in a hashmap, then do the same for columns.
        #while i do that I save the pointers of all numbers so I don't have to iterate through the whole matrix, and only on coordinates with numbers.
        #then we check the 3x3 grids scanning the entire table

        col = [set() for _ in range(9)] 
        row = [set() for _ in range(9)] 
        box = [set() for _ in range(9)] 
        print(col)
        for r in range(9):
            for c in range(9):
                value = board[r][c]
                if value == ".":
                    continue
                box_i = (r//3) * 3 + (c//3)
                if (value in row[r] or value in col[c] or value in box[box_i]):
                    return False
                row[r].add(value)
                col[c].add(value)
                box[box_i].add(value)
        return True