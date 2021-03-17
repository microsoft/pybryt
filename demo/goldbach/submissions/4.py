def check_goldbach_for_num(n, primes_set):
    for x in primes_set:
        for y in primes_set:
            if x + y == n :
                return True
    return False

