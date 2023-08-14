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

    # form date iterables in order
    years = sorted(list(contributions_history.keys()))
    # get time boundaries of data
    first_month_first_year = min(list(contributions_history[years[0]].keys()))
    last_month_last_year = max(list(contributions_history[years[-1]].keys()))


    # set up plot
    year_month_list = []
    contributions_list = []
    for contribution_year in years:
        year_string = str(contribution_year)[-2:]
        for contribution_month in range(1,13):
            if contribution_year == years[0]:
                if contribution_month < first_month_first_year:
                    continue

            elif contribution_year == years[-1]:
                if contribution_month > last_month_last_year:
                    break

            month_string = str(contribution_month)
            year_month_list.append(year_string + '-' + month_string)
            try:
                contributions_list.append(contributions_history[contribution_year][contribution_month])
            except KeyError:
                contributions_list.append(0)


            

    print(contributions_history)
    plt.bar(year_month_list, contributions_list)
    plt.ylabel('Amount invested [EUR]')
    plt.show()

    
