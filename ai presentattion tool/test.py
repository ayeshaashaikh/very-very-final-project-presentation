import random


def partition(arr,low,high):
    pivot = arr[high]
    i = low-1
    for j in range(low,high):
        if arr[j]<= pivot:
            i+=1
            arr[i],arr[j] = arr[j], arr[i]
    arr[i+1],arr[high] = arr[high], arr[i+1]
    return i+1

def deter(arr,low,high):
    if low<high:
        pi = partition(arr,low,high)
        deter(arr,low,pi-1)
        deter(arr,pi+1,high)
        
def randomized(arr,low,high):
    rand_index = random.randint(low,high)
    arr[rand_index], arr[high] = arr[high],arr[rand_index]
    return partition(arr,low,high)

def quick_sort_randomized(arr, low, high):
    if low<high:
        pi = partition(arr,low,high)
        quick_sort_randomized(arr,low,pi-1)
        quick_sort_randomized(arr,pi+1,high)
        
if __name__ == "__main__":
    arr = list(map(int, input("enter values seperating by space:").split()))
    n = len(arr)
    deter(arr,0,n-1)
    print(arr)
    quick_sort_randomized(arr,0,n-1)
    print(arr)
    