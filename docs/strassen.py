"""Pythonic matrix multiplcation using Strassen's algorithm"""

# This implementation is adapted from https://martin-thoma.com/strassen-algorithm-in-python-java-cpp/

from math import ceil, log


LEAF_SIZE = 8


def naive_matmul(A, B):
    n = len(A)
    C = [[0 for i in range(n)] for j in range(n)]
    for i in range(n):
        for k in range(n):
            for j in range(n):
                C[i][j] += A[i][k] * B[k][j]
    return C


def add(A, B):
    n = len(A)
    C = [[0 for j in range(0, n)] for i in range(0, n)]
    for i in range(0, n):
        for j in range(0, n):
            C[i][j] = A[i][j] + B[i][j]
    return C


def subtract(A, B):
    n = len(A)
    C = [[0 for j in range(0, n)] for i in range(0, n)]
    for i in range(0, n):
        for j in range(0, n):
            C[i][j] = A[i][j] - B[i][j]
    return C


def strassen(A, B):
    n = len(A)

    if n <= LEAF_SIZE:
        return naive_matmul(A, B)

    else:
        # initializing the new sub-matrices
        new_size = n // 2
        a11 = [[0 for j in range(0, new_size)] for i in range(0, new_size)]
        a12 = [[0 for j in range(0, new_size)] for i in range(0, new_size)]
        a21 = [[0 for j in range(0, new_size)] for i in range(0, new_size)]
        a22 = [[0 for j in range(0, new_size)] for i in range(0, new_size)]

        b11 = [[0 for j in range(0, new_size)] for i in range(0, new_size)]
        b12 = [[0 for j in range(0, new_size)] for i in range(0, new_size)]
        b21 = [[0 for j in range(0, new_size)] for i in range(0, new_size)]
        b22 = [[0 for j in range(0, new_size)] for i in range(0, new_size)]

        A_result = [[0 for j in range(0, new_size)] for i in range(0, new_size)]
        B_result = [[0 for j in range(0, new_size)] for i in range(0, new_size)]

        # dividing the matrices in 4 sub-matrices:
        for i in range(0, new_size):
            for j in range(0, new_size):
                a11[i][j] = A[i][j]  # top left
                a12[i][j] = A[i][j + new_size]  # top right
                a21[i][j] = A[i + new_size][j]  # bottom left
                a22[i][j] = A[i + new_size][j + new_size]  # bottom right

                b11[i][j] = B[i][j]  # top left
                b12[i][j] = B[i][j + new_size]  # top right
                b21[i][j] = B[i + new_size][j]  # bottom left
                b22[i][j] = B[i + new_size][j + new_size]  # bottom right

        # Calculating p1 to p7:
        A_result = add(a11, a22)
        B_result = add(b11, b22)
        p1 = strassen(A_result, B_result)  # p1 = (a11+a22) * (b11+b22)

        A_result = add(a21, a22)  # a21 + a22
        p2 = strassen(A_result, b11)  # p2 = (a21+a22) * (b11)

        B_result = subtract(b12, b22)  # b12 - b22
        p3 = strassen(a11, B_result)  # p3 = (a11) * (b12 - b22)

        B_result = subtract(b21, b11)  # b21 - b11
        p4 = strassen(a22, B_result)  # p4 = (a22) * (b21 - b11)

        A_result = add(a11, a12)  # a11 + a12
        p5 = strassen(A_result, b22)  # p5 = (a11+a12) * (b22)

        A_result = subtract(a21, a11)  # a21 - a11
        B_result = add(b11, b12)  # b11 + b12
        p6 = strassen(A_result, B_result)  # p6 = (a21-a11) * (b11+b12)

        A_result = subtract(a12, a22)  # a12 - a22
        B_result = add(b21, b22)  # b21 + b22
        p7 = strassen(A_result, B_result)  # p7 = (a12-a22) * (b21+b22)

        # calculating c21, c21, c11 e c22:
        c12 = add(p3, p5)  # c12 = p3 + p5
        c21 = add(p2, p4)  # c21 = p2 + p4

        A_result = add(p1, p4)  # p1 + p4
        B_result = add(A_result, p7)  # p1 + p4 + p7
        c11 = subtract(B_result, p5)  # c11 = p1 + p4 - p5 + p7

        A_result = add(p1, p3)  # p1 + p3
        B_result = add(A_result, p6)  # p1 + p3 + p6
        c22 = subtract(B_result, p2)  # c22 = p1 + p3 - p2 + p6

        # Grouping the results obtained in a single matrix:
        C = [[0 for j in range(0, n)] for i in range(0, n)]
        for i in range(0, new_size):
            for j in range(0, new_size):
                C[i][j] = c11[i][j]
                C[i][j + new_size] = c12[i][j]
                C[i + new_size][j] = c21[i][j]
                C[i + new_size][j + new_size] = c22[i][j]

        return C


def matmul(A, B):
    assert type(A) == list and type(B) == list
    assert len(A) == len(A[0]) == len(B) == len(B[0])

    # Make the matrices bigger so that you can apply the strassen
    # algorithm recursively without having to deal with odd
    # matrix sizes
    next_power_of_two = lambda n: 2 ** int(ceil(log(n, 2)))
    n = len(A)
    m = next_power_of_two(n)
    A_prep = [[0 for i in range(m)] for j in range(m)]
    B_prep = [[0 for i in range(m)] for j in range(m)]
    for i in range(n):
        for j in range(n):
            A_prep[i][j] = A[i][j]
            B_prep[i][j] = B[i][j]

    C_prep = strassen(A_prep, B_prep)
    C = [[0 for i in range(n)] for j in range(n)]
    for i in range(n):
        for j in range(n):
            C[i][j] = C_prep[i][j]

    return C
