from abc import ABC, abstractmethod


class LPSolverInterface(ABC):
    @abstractmethod
    def create_tableau(self, objective_coeffs, constraint_coeffs, rhs_values, rel_coeffs, restricted):
        pass

    @abstractmethod
    def solve(self, maximize, tableau_df):
        pass
