import sys
import matplotlib.pyplot as plt
sys.path.append('.')
import model.portfolio as pftools
import numpy as np

if __name__ == '__main__':
    fortuneo_csv_file = 'data/HistoriqueOperationsBourse_015207052916_du_12_08_2021_au_12_08_2023.csv'

    operations = pftools.FortuneoInterface.extract_operations_from_csv(fortuneo_csv_file)

    """format of contributions history will be [year][month]"""
    contributions_history = {}
    for op in operations:
        year = op.date.year
        month = op.date.month
        try:
            contributions_history[year][month] += op.net_amount
        except KeyError:
            if year not in contributions_history.keys():
                contributions_history[year] = {}

            contributions_history[year][month] = op.net_amount

    # set up plot

    year_month_list = []
    contributions_list = []
    for contribution_year in contributions_history.keys():
        year_string = str(contribution_year)[-2:]
        for contribution_month in contributions_history[contribution_year].keys():
            month_string = str(contribution_month)
            year_month_list.append(year_string + '-' + month_string)
            contributions_list.append(contributions_history[contribution_year][contribution_month])
            

    
    plt.bar(year_month_list, contributions_list)
    plt.ylabel('Amount invested [EUR]')
    plt.show()

    
