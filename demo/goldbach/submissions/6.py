def check_goldbach_for_num(n,primes_set) :
    '''gets an even integer- n, and a set of primes- primes_set. Returns whether there're two primes which their sum is n'''
    
    for prime in primes_set :
        if ((p < n) and ((n - prime) in primes_set)):
            return True
    return False

