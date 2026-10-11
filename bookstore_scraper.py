"""Scrape Books to Scrape and generate the bookstore intelligence deliverables."""

import argparse
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests


BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
COLUMNS = ["Title", "Price", "Rating", "Availability", "URL"]
BUDGET_CENTS = 10000


def parse_page(html, page_url):
    """Extract book-card fields from a single catalogue page."""
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.product_pod")
    if not cards:
        raise ValueError(f"No book cards found at {page_url}")

    books = []
    for card in cards:
        link = card.select_one("h3 a")
        price_tag = card.select_one("p.price_color")
        rating_tag = card.select_one("p.star-rating")
        availability_tag = card.select_one("p.availability")
        if any(tag is None for tag in (link, price_tag, rating_tag, availability_tag)):
            raise ValueError(f"Incomplete book card at {page_url}")

        title = link.get("title") or link.get_text(strip=True)
        price_match = re.search(r"\d+\.\d{2}", price_tag.get_text(strip=True))
        if not price_match:
            raise ValueError(f"Could not parse price for {title}")
        price = float(Decimal(price_match.group()))

        rating = next(
            (RATING_MAP[word] for word in rating_tag.get("class", []) if word in RATING_MAP),
            None,
        )
        if rating is None:
            raise ValueError(f"Could not parse rating for {title}")

        availability_text = availability_tag.get_text(" ", strip=True)
        availability = "In stock" if "In stock" in availability_text else "Out of stock"
        books.append(
            {
                "Title": title,
                "Price": price,
                "Rating": rating,
                "Availability": availability,
                "URL": urljoin(page_url, link["href"]),
            }
        )
    return books


def scrape_books(num_pages):
    """Fetch the requested catalogue pages using one reusable parsing function."""
    session = requests.Session()
    session.headers.update({"User-Agent": "BookstoreIntelligenceStudentProject/1.0"})
    all_books = []

    for page in range(1, num_pages + 1):
        url = BASE_URL.format(page)
        response = session.get(url, timeout=20)
        response.raise_for_status()
        page_books = parse_page(response.text, url)
        all_books.extend(page_books)
        print(f"Page {page}: {len(page_books)} books scraped")

    df = pd.DataFrame(all_books, columns=COLUMNS)
    df = df.drop_duplicates(subset="URL").reset_index(drop=True)
    df["Price"] = pd.to_numeric(df["Price"])
    df["Rating"] = pd.to_numeric(df["Rating"]).astype(int)
    if df.empty:
        raise ValueError("No books were scraped")
    return df


def pence(value):
    return int(Decimal(str(value)).quantize(Decimal("0.01")) * 100)


def optimize_ceo_purchase(df, budget_cents=BUDGET_CENTS):
    """0/1 knapsack: maximize rating points, then minimize total cost."""
    available = df.loc[df["Availability"] == "In stock"].reset_index(drop=True)
    scores = [0] * (budget_cents + 1)
    decisions = []

    for book in available.itertuples(index=False):
        cost = pence(book.Price)
        chosen = bytearray(budget_cents + 1)
        for remaining in range(budget_cents, cost - 1, -1):
            score = scores[remaining - cost] + int(book.Rating)
            if score > scores[remaining]:
                scores[remaining] = score
                chosen[remaining] = 1
        decisions.append(chosen)

    best_score = scores[budget_cents]
    current_budget = scores.index(best_score)
    selected_indices = []
    for i in range(len(available) - 1, -1, -1):
        if decisions[i][current_budget]:
            selected_indices.append(i)
            current_budget -= pence(available.at[i, "Price"])

    result = available.iloc[selected_indices].sort_values(
        by=["Price", "Title"], ascending=[True, True]
    ).reset_index(drop=True)
    assert sum(pence(x) for x in result["Price"]) <= budget_cents
    assert int(result["Rating"].sum()) == best_score
    return result


def make_analysis_report(df, selected, pages):
    expensive = df.loc[df["Price"].idxmax()]
    cheap = df.loc[df["Price"].idxmin()]
    five_star = df.loc[df["Rating"] == 5]
    in_stock = df["Availability"].eq("In stock").mean() * 100
    top_five = df.sort_values(
        ["Rating", "Price", "Title"], ascending=[False, True, True]
    ).head(5)
    cheapest_five = five_star.sort_values(["Price", "Title"]).head(1)
    recommended = df.loc[
        (df["Rating"] == 5) & (df["Availability"] == "In stock")
    ].sort_values(["Price", "Title"]).head(2)

    def book_line(row):
        return f"{row['Title']} (GBP {row['Price']:.2f}; {int(row['Rating'])} stars)"

    report = [
        "# Bookstore Intelligence: Analysis Report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Source: https://books.toscrape.com/ (first {pages} catalogue pages)",
        f"Books analyzed: {len(df)}",
        "",
        "Note: This is a practice website. Its prices and star ratings are randomly assigned,",
        "so these findings are an exercise, not evidence of real consumer preferences.",
        "",
        "## Mission 1: HTML reconnaissance",
        "",
        "| Data | HTML element / class | How it is used |",
        "| --- | --- | --- |",
        "| Title | `article.product_pod h3 a` | Read the `title` attribute |",
        "| Price | `p.price_color` | Extract numeric price |",
        "| Rating | `p.star-rating` | Map word class `One` to `Five` to 1-5 |",
        "| Availability | `p.availability` | Normalize to In stock / Out of stock |",
        "",
        "## Mission 4: Seven business intelligence answers",
        "",
        f"1. **Most expensive:** {book_line(expensive)}.",
        f"2. **Cheapest:** {book_line(cheap)}.",
        f"3. **Average price:** GBP {df['Price'].mean():.2f}.",
        f"4. **Number of 5-star books:** {len(five_star)}.",
        f"5. **Percentage in stock:** {in_stock:.2f}%.",
        "6. **Top five highest-rated books** (ties ordered by lowest price):",
        "",
        "| Title | Price (GBP) | Rating |",
        "| --- | ---: | ---: |",
    ]
    for row in top_five.to_dict("records"):
        report.append(f"| {row['Title'].replace('|', '/')} | {row['Price']:.2f} | {row['Rating']} |")
    report.extend(["", "7. **Cheapest 5-star book:** " + (
        book_line(cheapest_five.iloc[0]) if not cheapest_five.empty else "None in the sample"
    ) + ".", "", "## Business recommendation", ""])

    if not recommended.empty:
        titles = "; ".join(book_line(row) for _, row in recommended.iterrows())
        report.append(
            "Prioritize " + titles + ". They are both rated 5 stars and currently in stock; "
            "they are also among the cheapest in-stock 5-star titles in the scraped sample. "
            "These criteria help test a highly rated, lower-cost assortment, but do not measure actual demand."
        )
    else:
        report.append("No in-stock 5-star titles appeared in this sample; consider in-stock 4-star alternatives.")

    report.extend([
        "", "## CEO challenge: Maximum star points for GBP 100", "",
        "Each title may be purchased at most once. Only in-stock titles qualify.",
        "The 0/1 knapsack algorithm maximizes total star points under the budget,",
        "breaking ties in favor of the lowest total cost.", "",
        "| Selected title | Price (GBP) | Rating |",
        "| --- | ---: | ---: |",
    ])
    for row in selected.to_dict("records"):
        report.append(f"| {row['Title'].replace('|', '/')} | {row['Price']:.2f} | {row['Rating']} |")
    total_pence = sum(pence(x) for x in selected["Price"])
    report.extend([
        "",
        f"**Selected books:** {len(selected)}",
        f"**Total cost:** GBP {total_pence / 100:.2f}",
        f"**Total rating score:** {int(selected['Rating'].sum())}",
        f"**Remaining budget:** GBP {(BUDGET_CENTS - total_pence) / 100:.2f}",
        "",
        "## Bonus: Rating distribution", "",
        "| Stars | Number of books |", "| ---: | ---: |",
    ])
    for stars, count in df["Rating"].value_counts().reindex(range(1, 6), fill_value=0).sort_index().items():
        report.append(f"| {stars} | {count} |")
    report.extend(["", "See `rating_distribution.png` for the chart.", ""])
    return "\n".join(report)


def save_chart(df, path):
    counts = df["Rating"].value_counts().reindex(range(1, 6), fill_value=0)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(counts.index.astype(str), counts.values)
    ax.set_title("Books by Star Rating")
    ax.set_xlabel("Star rating")
    ax.set_ylabel("Number of books")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Books to Scrape market intelligence assignment")
    parser.add_argument("--pages", type=int, default=5, help="Catalogue pages to scrape (1-50; default 5)")
    parser.add_argument("--all", action="store_true", help="Scrape all 50 catalogue pages")
    parser.add_argument("--output-dir", type=Path, default=Path("."), help="Directory for output files")
    args = parser.parse_args()

    pages = 50 if args.all else args.pages
    if not 1 <= pages <= 50:
        parser.error("--pages must be between 1 and 50")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = scrape_books(pages)
    selected = optimize_ceo_purchase(df)
    df.to_csv(args.output_dir / "competitor_books.csv", index=False, float_format="%.2f")
    selected.to_csv(args.output_dir / "ceo_selected_books.csv", index=False, float_format="%.2f")
    save_chart(df, args.output_dir / "rating_distribution.png")
    (args.output_dir / "analysis_report.md").write_text(
        make_analysis_report(df, selected, pages), encoding="utf-8"
    )

    print(f"\nScraped {len(df)} books across {pages} pages")
    print(df.head().to_string(index=False))
    print(f"\nAverage price: GBP {df['Price'].mean():.2f}")
    print(f"Five-star books: {int((df['Rating'] == 5).sum())}")
    print(f"In stock: {df['Availability'].eq('In stock').mean() * 100:.2f}%")
    print(f"CEO selection: {len(selected)} books, GBP {selected['Price'].sum():.2f}, {selected['Rating'].sum()} points")
    print(f"Saved CSV files, analysis report, and chart to {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
