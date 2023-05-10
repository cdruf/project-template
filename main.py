from pathlib import Path

if __name__ == '__main__':
    print("Welcome to electric vehicle arc routing")
    data_folder_path = Path(__file__).parent / "data"
    instance = Instance.read_from_excel(data_folder_path, "Data_template - v09.xlsx")

    # Create start solution with optimization model
    model = SchedulingModel(instance, data_folder_path)
    solution = model.solve(solver="GRB", timeout_sec=60 * 10)
    solution.to_csv(data_folder_path / 'out_model')

    # Warm-start local search and improve solution
    ls = LocalSearch(instance, start_solution=solution)
    solution = ls.solve_v2(timeout_sec=60 * 45)
    solution.to_csv(data_folder_path / 'out_local_search')
    print("Buy!")