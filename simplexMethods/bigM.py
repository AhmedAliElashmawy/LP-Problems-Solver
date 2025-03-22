import numpy as np
import pandas as pd
import sympy as sp
from LpInterface import LPSolverInterface


class BigMSolver(LPSolverInterface):
    __M = sp.Symbol("M")

    def __init__(self):
        self.basic_vars = []
        self.var_names = []
        self.steps = []
        self.answer = None

    def create_tableau(self, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):

        num_artificial_vars = sum(1 for x in rel_coeffs if x != "<=")
        num_slack_vars = sum(1 for x in rel_coeffs if x != "=")
        num_unrestricted_variables = sum(1 for val in restricted if not val)



        num_constraints, num_variables = len(constraint_coeffs), len(objective_coeffs)

        total_variables = num_variables + num_unrestricted_variables + num_artificial_vars + num_slack_vars


        tableau = sp.Matrix.zeros(num_constraints + 1, total_variables + 1)

        artifical_var_id = slack_var_id = unrestricted_var_id = restricted_var_id = 1

        header_row = []
        expanded_obj_coeffs = []
        expanded_constraint_coeffs = []

        # Handles restricted and unrestricted vars
        for i in range(num_variables):
            if restricted[i]:
                expanded_constraint_coeffs.append([row[i] for row in constraint_coeffs])
                expanded_obj_coeffs.append(objective_coeffs[i])
                header_row.append(f"x{restricted_var_id}")
                restricted_var_id += 1
            else:
                expanded_constraint_coeffs.append([row[i] for row in constraint_coeffs])
                expanded_constraint_coeffs.append([-row[i] for row in constraint_coeffs])
                expanded_obj_coeffs.append(objective_coeffs[i])
                expanded_obj_coeffs.append(-objective_coeffs[i])
                header_row.extend([f"y{unrestricted_var_id}+" , f"y{unrestricted_var_id}-"])
                unrestricted_var_id += 1

        #Handles slack vars
        for i in range(len(rel_coeffs)):
            if rel_coeffs[i] == "=":
                continue
            expanded_constraint_coeffs.append([0]*(i)+[(-1 if rel_coeffs[i]=='>=' else 1)]+[0]*(num_constraints-1-i))
            header_row.append(f"s{slack_var_id}")

            slack_var_id += 1
            expanded_obj_coeffs.append(0)

        #Handles artificial vars
        for i in range(len(rel_coeffs)):
            if rel_coeffs[i] in ["=", ">="]:
                expanded_constraint_coeffs.append([0]*(i)+[1]+[0]*(num_constraints-1-i))
                header_row.append(f"a{artifical_var_id}")
                artifical_var_id += 1
                expanded_obj_coeffs.append(BigMSolver.__M)

        #Handles Basic vars
        artifical_var_id = slack_var_id = 1
        for rel in rel_coeffs:
            self.basic_vars.append(f"a{artifical_var_id}" if rel in ["=", ">="] else f"s{slack_var_id}")
            if rel in ["=", ">="]:
                artifical_var_id += 1
            else:
                slack_var_id += 1


        # Shapes objective row
        expanded_obj_coeffs = [expanded_obj_coeffs]


        # Sets tableau values
        tableau[:-1, :total_variables] = sp.Matrix(expanded_constraint_coeffs).T
        tableau[:-1, -1] = sp.Matrix(rhs_values)
        tableau[-1, :total_variables] = sp.Matrix(expanded_obj_coeffs)

        # Eliminates M values in the objective row's artificial vars
        if(num_artificial_vars >0):
            for i, var in enumerate(self.basic_vars):
                col_index = header_row.index(var)
                tableau[-1, :] -= BigMSolver.__M * tableau[i, :]

        self.var_names = header_row + ["RHS"]

        return pd.DataFrame(np.array(tableau).astype(object), index=self.basic_vars + ["Z"], columns=self.var_names)

    def solve(self, maximize, tableau_df):
        if tableau_df is None:
            print("Unsolvable with Big-M method")
            return None, self.steps, None

        tableau = sp.Matrix(tableau_df.to_numpy())
        self.var_names = list(tableau_df.columns)
        self.basic_vars = list(tableau_df.index[:-1])
        self.steps.append(tableau_df.copy())

        # Iterate while there is a negative coefficient in the objective row for maximization (or positive for minimization)
        while any(sp.simplify(x).subs('M', 1e9) < 0 if maximize else sp.simplify(x).subs('M', 1e9) > 0 for x in tableau[-1, :-1]):
            # Choose pivot column (most negative for max, most positive for min)
            pivot_col = min(
                range(tableau.shape[1] - 1),
                key=lambda j: tableau[-1, j].subs('M', 1e9).evalf()
            ) if maximize else max(
                range(tableau.shape[1] - 1),
                key=lambda j: tableau[-1, j].subs('M', 1e9).evalf()
            )

            # Compute ratios for minimum positive pivot rule
            ratios = [
                tableau[i, -1] / tableau[i, pivot_col] if tableau[i, pivot_col] > 0 else sp.oo
                for i in range(tableau.shape[0] - 1)
            ]

            # Find pivot row (row with minimum ratio)
            pivot_row = min((i for i in range(len(ratios)) if ratios[i] != sp.oo), key=lambda i: ratios[i], default=None)

            if pivot_row is None:
                print("Unbounded solution detected.")
                return None, self.steps, None

            # Update basic variable
            self.basic_vars[pivot_row] = self.var_names[pivot_col]

            # Normalize pivot row
            tableau[pivot_row, :] /= tableau[pivot_row, pivot_col]

            # Store intermediate step
            self.steps.append(pd.DataFrame(np.array(tableau).astype(object), index=self.basic_vars + ["Z"], columns=self.var_names))

            # Perform row operations to make pivot column zero
            for i in range(tableau.shape[0]):
                if i != pivot_row:
                    tableau[i, :] -= tableau[pivot_row, :] * tableau[i, pivot_col]

            # Store intermediate step
            self.steps.append(pd.DataFrame(np.array(tableau).astype(object), index=self.basic_vars + ["Z"], columns=self.var_names))

        # Extract final solution values
        new_rhs = dict(zip(self.basic_vars, tableau[:-1, -1]))

        # Ensure feasibility (all artificial variables should be zero)
        for var in self.basic_vars:
            if var.startswith("a") and tableau[self.basic_vars.index(var), -1] != 0:
                print("Infeasible solution detected.")
                return None, self.steps, None

        # Handle unrestricted variables properly (y1 = y1+ - y1-)
        y_val = new_rhs.get("y1+", 0) - new_rhs.get("y1-", 0)

        # Extract the solution
        self.answer = (new_rhs.get("x1", 0), y_val)

        return tableau[-1, -1].evalf() * (1 if maximize else -1), self.steps, self.answer



