

list = [3,6,0,7,0,8]
removed = []
print(list)
pop = 0
for i in range(len(list)):
    print(i)
    if list[i-pop] == 0:
        list.pop(i-pop)
        removed.append(i)
        pop+=1
print(list)
for i in range(len(removed)):
    list.insert(removed[i],0)
print(list)

