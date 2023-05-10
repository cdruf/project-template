from dataclasses import dataclass
from datetime import datetime

import pulp as pl

from src.optimization_data import Solution
from util.pulp_helper import get_positive_expr_values_int, get_positive_expr_values


@dataclass()
class OptimizationModel:

    def __init__(self):
        print('...')
        self._mdl = None

    def _solve_gurobi(self, timeout_sec=60 * 5, mip_gap=0.001):
        """Solve with Gurobi's Python API."""
        solver = pl.GUROBI(timeLimit=timeout_sec, mipgap=mip_gap)
        solver.buildSolverModel(self._mdl)

        # MIP start (seems to be not working)
        if pl.LpStatus[self._mdl.status] == 'Optimal':
            self._mdl.solverModel.NumStart = 1
            for _, x in self.x_etp.items():
                var = self._mdl.solverModel.getVarByName(x.name)
                var.Start = pl.value(x)

        self._mdl.solverModel.update()
        self._mdl.solve(solver)
        if self._mdl.solverModel.status == 3:
            print("\n\n\nModel is infeasible\n\n\n")
            self._mdl.solverModel.computeIIS()
            self._mdl.solverModel.write("iis.ilp")
            print("\n\n\nIIS written to iis.ilp\n\n\n")

    def _solve_cbc(self, timeout_sec=60 * 5, mip_gap=0.001):
        """Solve the model with the CBC solver shipped with PuLP."""
        solver = pl.PULP_CBC_CMD(timeLimit=timeout_sec, gapRel=mip_gap,
                                 warmStart=True, presolve=True, cuts=True,
                                 keepFiles=False, msg=True)
        print('Solving ...')
        self._mdl.solve(solver=solver)

    def _build_solution(self) -> Solution:
        """Extract variable and expression values and pass them to the solution-object."""

        # Variables
        xx = get_positive_expr_values_int(self.x_et)

        # Expressions

        yyy = get_positive_expr_values(self.s_fte_minus_e)

        return Solution()

    def _solve_with_solver(self, solver, timeout_sec, mip_gap):
        """Call the right method for the given solver."""
        if solver.lower() == "cbc":
            self._solve_cbc(timeout_sec, mip_gap)
        elif solver.lower() == "grb":
            self._solve_gurobi(timeout_sec, mip_gap)
        else:
            raise ValueError("Wrong solver!")

    def solve(self, timeout_sec=60 * 5, solver="CBC") -> Solution:
        """Solve the hierarchical objectives in phases"""

        print('Solve model')
        print(f"\tTimeout set to {timeout_sec} sec")
        start = datetime.now()
        self._mdl.writeLP(str((self.data_folder_path / "model_files/schedule.lp").resolve()))

        print("\n")
        self._solve_with_solver(solver, timeout_sec, 0.001)

        self.solve_secs = round((datetime.now() - start).seconds, 2)
        print(f"Model solved in {self.solve_secs:.0f} secs")
        print(f"Objective value = {pl.value(self._mdl.objective):.0f}")

        return self._build_solution()
