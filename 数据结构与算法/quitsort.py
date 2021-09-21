class Solution(object):
    def sortArray(self, nums):
        """
        :type nums: List[int]
        :rtype: List[int]
        """

        # Quiksort
        def findv(arr, start, end):
            m = (start + end)/2
            arr[start], arr[m] = arr[m], arr[start]

        # Quiksort
        def partition(arr, start, end):
            findv(arr, start, end)
            tmp = arr[start]
            i, j = start, end
            while i < j:
                while arr[j] > tmp and i < j:
                    j -= 1
                if i < j:
                    arr[i] = arr[j]
                    i += 1
                while arr[i] < tmp and i < j:
                    i += 1
                if i < j:
                    arr[j] = arr[i]
                    j -= 1
            
            arr[i] = tmp
            return i
            
        
        def quitsort(arr, start, end):
            m = partition(arr, start, end)
            if m-1 > start:
                quitsort(arr, start, m-1)
            if m + 1 < end:
                quitsort(arr, m+1, end)
        
        quitsort(nums, 0, len(nums) - 1)

        return nums

print Solution().sortArray([5,2,3,1])