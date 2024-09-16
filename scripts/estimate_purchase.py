import sys
sys.path.append('.')
import model.portfolio as pftools

if __name__ == '__main__':

    print("Purchase estimator...")
    # configure current porfolio
    pe500_qty = 412
    pceu_qty = 325
    paaem_qty = 160

    pf_contents = {
                    pftools.PE500: pe500_qty,
                    pftools.PCEU: pceu_qty,
                    pftools.PAEEM: paaem_qty
                  }
  
    pf = pftools.Portfolio.from_tracker_and_quantity(pf_contents, fetch_stock_prices=True)
    print('Current porfolio summary:')
    pf.get_portfolio_summary(verbose=True)
    print('\n')

    previous_pe500_qty_to_buy = 0
    previous_pceu_qty_to_buy = 0
    previous_paaem_qty_to_buy = 0
    while True:
      print("Enter the amount of shares TO BUY for each stock")

      pe500_qty_to_buy = int(input('PE500: ') or previous_pe500_qty_to_buy)
      pceu_qty_to_buy = int(input('PCEU: ') or previous_pceu_qty_to_buy)
      paaem_qty_to_buy = int(input('PAEEM: ') or previous_paaem_qty_to_buy)


      purchases = {
                      pftools.PE500: pe500_qty_to_buy,
                      pftools.PCEU: pceu_qty_to_buy,
                      pftools.PAEEM: paaem_qty_to_buy
                    }

      simulated_pf = pftools.BuyEstimatorHelper.simulate_buy(pf, purchases, verbose=True)

      simulated_pf.get_portfolio_summary(verbose=True)

      previous_pe500_qty_to_buy = pe500_qty_to_buy
      previous_pceu_qty_to_buy = pceu_qty_to_buy
      previous_paaem_qty_to_buy = paaem_qty_to_buy
    
      print('\n')