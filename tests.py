import unittest
# import find_stations
from scrape_gas_single import scrape_gas
import warnings

warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

class TestScrape(unittest.TestCase):
    def test_find_stations(self):
        urls = find_stations.urls
        for url in urls:
            self.assertIn("https://www.costco.com/warehouse-locations/", url)

    def test_scrape_two_gas_types(self):
        data = scrape_gas("test_soups/test_data_two_types.txt")
        print('Data: ', data)
        correct = {'Name': 'Haha', 'Address': '123 Avalon St', 'City': 'Tustin', 'State': 'CA', 'Regular_Gas': '$4.99', 'Premium_Gas': '$5.29'}
        self.assertEqual(data, correct)

    def test_scrape_one_gas_type_regular(self):
        data = scrape_gas("test_soups/test_data_one_type_regular.txt")
        correct = {'Name': 'Haha', 'Address': '123 Avalon St', 'City': 'Tustin', 'State': 'CA', 'Regular_Gas': '$4.99', 'Premium_Gas': '?'}
        self.assertEqual(data, correct)
    
    def test_scrape_one_gas_type_premium(self):
        data = scrape_gas("test_soups/test_data_one_type_premium.txt")
        correct = {'Name': 'Haha', 'Address': '123 Avalon St', 'City': 'Tustin', 'State': 'CA', 'Regular_Gas': '?', 'Premium_Gas': '$5.29'}
        self.assertEqual(data, correct)
    


if __name__ == '__main__':
    unittest.main()