def check_goldbach_for_num(n, primes_set):
    for i in primes_set:
        if (n-i)in primes_set:
            return (True)

