import pandas as pd
import numpy as np
from scipy.optimize import linprog

hotel_schema = {
    'hotel_name': str,
    'rate': float,
    'king_count': int,
    'double_count': int,
    'triple_count': int,
    'five_six_count': int
}
hotels = pd.read_csv('hotels_robert.txt', delimiter=',', dtype=hotel_schema)
hotels.columns = hotel_schema.keys()

congregation_schema = {
    'congregation_name': str,
    'region': str,
    'total_participants': int,
    'kings_needed': int,
    'doubles_needed': int,
    'triples_needed': int,
    'five_sixes_needed': int,
    'unknown_column': int
}
congregations = pd.read_csv('congregations_robert.txt', delimiter=',', dtype=congregation_schema, encoding='latin-1')
congregations.columns = congregation_schema.keys()
congregation_df = congregations.dropna(how='any')

def main(): 
    # Objective function coefficients (room counts)
    c = np.array(congregation_df[['kings_needed', 'doubles_needed', 'triples_needed', 'five_sixes_needed']]).flatten()

    # Constraint matrix (hotel availability)
    A = np.eye(len(congregation_df) * len(hotels))

    # Constraint vector (tourist group requirements)
    b = np.array(hotels[['king_count', 'double_count', 'triple_count', 'five_six_count']]).flatten()

    # Solve the linear programming problem
    res = linprog(c, A_ub=A, b_ub=b, method='highs')

    # Retrieve the initial optimal solution
    solution = res.x.reshape((-1, len(hotels)))


if __name__ == '__main__': 
    main()