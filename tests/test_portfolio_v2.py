import sys
import unittest
sys.path.append(".")
import model.portfoliov2 as pf

class PF2TestCase(unittest.TestCase):
    
    def test_generate_pf_from_eml(self):
        """
        test data purchases
        Votre ordre d'achat sur AMUNDI ETF PEA S&P 500 UCITS ETF - EUR (FR0013412285) a été exécuté à 30,322 EUR pour une quantité de 16.0 le 15/03/22 à 13:08. (réf 20220315-2E652)
        Votre ordre d'achat sur Amundi PEA MSCI Emerging Markets ESG Leaders UCITS ETF - EUR (C/D) (FR0013412020) a été exécuté à 21,729 EUR pour une quantité de 1.0 le 11/09/24 à 11:17. (réf 20240911-40035)
        Votre ordre d'achat sur AMUNDI ETF PEA S&P 500 UCITS ETF - EUR (FR0013412285) a été exécuté à 29,239 EUR pour une quantité de 18.0 le 16/07/21 à 12:15. (réf 20210716-14843)
        Votre ordre d'achat sur AMUNDI ETF PEA MSCI EUROPE UCITS ETF - EUR (FR0013412038) a été exécuté à 27,215 EUR pour une quantité de 2.0 le 16/01/24 à 15:30. (réf 20240116-50EED) 
        Votre ordre d'achat sur AMUNDI ETF PEA MSCI EUROPE UCITS ETF - EUR (FR0013412038) a été exécuté à 25,375 EUR pour une quantité de 15.0 le 17/02/22 à 13:57. (réf 20220217-96DFD)

        """
        my_pf = pf.generate_portfolio_db_from_eml('data/order-emails/test_data')
        print(my_pf.get_portfolio_tickers())


if __name__ == '__main__':
    unittest.main()
