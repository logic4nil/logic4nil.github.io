
# 最长不重复字串
def f2(arr):
    flag = [1 for i in range(0, len(arr))]
    
    d = {}
    d[arr[0]] = 0
    for i in range(1, len(arr)):
        if arr[i] not in d or (i - 1 - flag[i-1]) >= d[arr[i]]:
            flag[i] = flag[i-1] + 1
        else:
            flag[i] = i - 1 - d[arr[i]]
        d[arr[i]] = i
    
    return max(flag)

print f2("abcabcbb")
print f2("bbbb")
print f2("fasdfff")
print f2("abaacxf123a")