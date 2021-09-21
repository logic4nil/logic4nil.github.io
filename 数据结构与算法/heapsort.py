
class Solution(object):
    def sortArray(self, nums):
        """
        :type nums: List[int]
        :rtype: List[int]
        """
        def sift(arr, i, n):
            tmp = arr[i]
            j = 2 * i
            while j <= n:
                if j < n and arr[j] < arr[j + 1]:
                    j += 1
                if tmp < arr[j]:
                    arr[i] = arr[j]
                    i = j
                    j = 2 * j
                else:
                    break
            arr[i] = tmp
        
        def heapsort(arr):
            n = len(arr)
            newarr = [0]
            newarr.extend(arr)
            for t in range(n/2, 0 , -1):
                sift(newarr, t, n)
            for t in range(n, 1, -1):
                newarr[t], newarr[1] = newarr[1], newarr[t]
                sift(newarr, 1, t-1)
            
            return newarr[1:]
        return heapsort(nums)          



print Solution().sortArray([-4,0,7,4,9,-5,-1,0,-7,-1])