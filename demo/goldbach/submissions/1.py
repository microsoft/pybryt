def check_goldbach_for_num(n, primes_set):
    primes_set = sorted(primes_set)
    left = 0
    right = len(primes_set) - 1
    index_s = None
    index_b = None
    while left <= right:
        mid = (left + right) // 2
        if n == primes_set[mid]:
            return "number is prime"
        elif right == left:
            if n > mid:
                index_s = mid
                break
            else:
                index_b = mid
        elif n < primes_set[mid]:
            if n > primes_set[mid - 1]:
                index_b = mid
                index_s = mid - 1
                break
            right = mid - 1
        else:
            if n < primes_set[mid + 1]:
                index_b = mid + 1
                index_s = mid
                break
            left = mid + 1
    for i in range(0, len(primes_set) - 1):
        if n-primes_set[i] in primes_set:
            return True
    return False

