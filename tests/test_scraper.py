"""Offline tests: do not require requests to the practice website."""

import unittest

import pandas as pd

from bookstore_scraper import optimize_ceo_purchase, parse_page


class ScraperTests(unittest.TestCase):
    def test_parse_card(self):
        html = """
        <article class="product_pod">
          <h3><a href="test-book_1/index.html" title="Test Book">Short title</a></h3>
          <p class="price_color">&pound;12.50</p>
          <p class="star-rating Five"><i></i></p>
          <p class="instock availability"> In stock </p>
        </article>
        """
        books = parse_page(html, "https://books.toscrape.com/catalogue/page-1.html")
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]["Title"], "Test Book")
        self.assertEqual(books[0]["Price"], 12.50)
        self.assertEqual(books[0]["Rating"], 5)
        self.assertEqual(books[0]["Availability"], "In stock")
        self.assertEqual(books[0]["URL"], "https://books.toscrape.com/catalogue/test-book_1/index.html")

    def test_ceo_optimizer_maximizes_rating(self):
        df = pd.DataFrame([
            {"Title": "A", "Price": 39.00, "Rating": 5, "Availability": "In stock", "URL": "a"},
            {"Title": "B", "Price": 20.00, "Rating": 4, "Availability": "In stock", "URL": "b"},
            {"Title": "C", "Price": 50.00, "Rating": 5, "Availability": "In stock", "URL": "c"},
            {"Title": "D", "Price": 1.00, "Rating": 5, "Availability": "Out of stock", "URL": "d"},
        ])
        chosen = optimize_ceo_purchase(df, budget_cents=6000)
        self.assertEqual(set(chosen["Title"]), {"A", "B"})
        self.assertEqual(int(chosen["Rating"].sum()), 9)
        self.assertEqual(round(chosen["Price"].sum(), 2), 59.00)

    def test_ceo_optimizer_cheapest_tie(self):
        df = pd.DataFrame([
            {"Title": "Costly", "Price": 11.00, "Rating": 5, "Availability": "In stock", "URL": "a"},
            {"Title": "Cheap", "Price": 10.00, "Rating": 5, "Availability": "In stock", "URL": "b"},
        ])
        chosen = optimize_ceo_purchase(df, budget_cents=1200)
        self.assertEqual(list(chosen["Title"]), ["Cheap"])


if __name__ == "__main__":
    unittest.main()
