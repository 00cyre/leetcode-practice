class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
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