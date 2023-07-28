import sys
sys.path.append('.')
import model.portfolio as pftools

if __name__ == '__main__':
    # enter current pf

    print("Purchase estimator...")
    print("Enter the amount of shares for each stock")

    pe500_qty = input('PE500: ')
    pceu_qty = input('PCEU: ')
    paaem_qty = input('PAEEM: ')

    pf_contents = {
                    pftools.PE500: int(pe500_qty),
                    pftools.PCEU: int(pceu_qty),
                    pftools.PAEEM: int(paaem_qty)
                  }

    pf = pftools.Portfolio.from_tracker_and_quantity(pf_contents)

    print("Enter the amount of shares TO BUY for each stock")

    pe500_qty_to_buy = input('PE500: ')
    pceu_qty_to_buy = input('PCEU: ')
    paaem_qty_to_buy = input('PAEEM: ')

    purchases = {
                    pftools.PE500: int(pe500_qty_to_buy),
                    pftools.PCEU: int(pe500_qty_to_buy),
                    pftools.PAEEM: int(pe500_qty_to_buy)
                  }

    simulated_pf = pftools.BuyEstimatorHelper.simulate_buy(pf, purchases, verbose=True)

    simulated_pf.get_portfolio_summary(verbose=True)