from collections import defaultdict
from fractions import Fraction
from itertools import chain
from sys import stderr

import numpy as np
from numpy.core.multiarray import zeros


def parse_atoms(molec: str):
    atoms = defaultdict(int)
    label = molec[0]
    quantity = 1
    for c in molec[1:]:
        if c.islower():
            label += c
        elif c.isnumeric():
            if quantity == 1:
                quantity = c
            else:
                quantity += c
        elif c.isupper():
            if label:
                atoms[label] += int(quantity)
            quantity = 1
            label = c

    if label:
        atoms[label] += int(quantity)

    return dict(atoms)


def parse_side(elements: str):
    molecules = [parse_atoms(mol) for mol in elements.split(" + ")]
    return molecules


def solve_with_free_variable(A, b):
    # Perform Singular Value Decomposition (SVD) to identify rank and free variables
    U, S, Vh = np.linalg.svd(A)

    tol = 1e-10
    rank = np.sum(S > tol)
    pivot_vars = np.arange(rank)
    free_vars = np.arange(rank, A.shape[1])

    solution = np.zeros(A.shape[1])
    if free_vars.size > 0:
        solution[free_vars[0]] = 1
        solution[:rank] = np.linalg.lstsq(
            A[:, :rank],
            b - np.dot(A[:, free_vars[0]], solution[free_vars[0]]),
            rcond=None,
        )[0]

    return solution, free_vars, pivot_vars


def normalize_to_integers(solution):
    fractions = [Fraction(str(x)).limit_denominator() for x in solution]

    denominators = [f.denominator for f in fractions]
    common_denominator = np.lcm.reduce(denominators)
    integer_solution = [int(f * common_denominator) for f in fractions]

    return integer_solution


def balance(left, right):
    atoms = list(sorted(set(key for mol in left for key in mol)))
    coefficients = len(left) + len(right)

    Q = np.zeros(shape=(len(atoms), coefficients))
    for row, atom in enumerate(atoms):
        eq = list()
        for mol in left:
            eq.append(mol.get(atom, 0))
        for mol in right:
            eq.append(-mol.get(atom, 0))
        Q[row] = eq
        print(row, atom, eq, file=stderr)

    Z = zeros(len(atoms))
    solution, free_vars, pivot_vars = solve_with_free_variable(Q, Z)

    print(f"Solution: {solution}", file=stderr)
    print(f"Free variables: {free_vars}", file=stderr)
    print(f"Dependent variable: {pivot_vars}", file=stderr)

    integer_solution = normalize_to_integers(solution)
    print(f"Normalized Integer Solution: {integer_solution}", file=stderr)
    for qi, mol in zip(integer_solution, chain(left, right)):
        mol["_coeff_"] = qi


def pretty(molecules):
    molecs = list()
    for mol in molecules:
        ix = mol.pop("_coeff_")
        part = str(ix) if ix > 1 else ""
        for atom, q in mol.items():
            if q == 1:
                part += atom
            else:
                part += atom + str(q)
        molecs.append(part)
    return " + ".join(molecs)


left_side, right_side = input().split(" -> ")

left = parse_side(left_side)
right = parse_side(right_side)

balance(left, right)
print(pretty(left), "->", pretty(right))
