class Solution:
    def countStudents(self, students: List[int], sandwiches: List[int]) -> int:
        #pega 11001 00011
        #n pega 10011 00011
        #n pega 00111 00011
        #pega 0111 0011
        #pega 111 011
        #n pega 
        # check for every sandwich if there's studend with 0 or 1 depending on the top stack sandwich
        # if we have it, continue iterating, and reapply logic.
        while True:
            if len(sandwiches) == 0:
                break
            s = sandwiches[0]
            stu = students[0]
            print(s,stu, students, sandwiches)
            if s not in students:
                return len(students)
            if stu != s:
                students.append(stu)
                students.pop(0)
            if stu == s:
                sandwiches.pop(0)
                students.pop(0)
        return 0   