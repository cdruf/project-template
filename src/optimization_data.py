from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Instance:
    n_days: int

    @classmethod
    def read_from_excel(cls, data_folder_path: Path, file_name: str):
        return None


@dataclass
class Solution:
    assignments: pd.DataFrame

    def to_csv(self, data_folder_path: str):
        print('Write solution to CSV')
