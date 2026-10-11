# Bookstore Intelligence: Analysis Report

Generated: 2026-10-11 15:46 UTC
Source: https://books.toscrape.com/ (first 5 catalogue pages)
Books analyzed: 100

Note: This is a practice website. Its prices and star ratings are randomly assigned,
so these findings are an exercise, not evidence of real consumer preferences.

## Mission 1: HTML reconnaissance

| Data | HTML element / class | How it is used |
| --- | --- | --- |
| Title | `article.product_pod h3 a` | Read the `title` attribute |
| Price | `p.price_color` | Extract numeric price |
| Rating | `p.star-rating` | Map word class `One` to `Five` to 1-5 |
| Availability | `p.availability` | Normalize to In stock / Out of stock |

## Mission 4: Seven business intelligence answers

1. **Most expensive:** The Death of Humanity: and the Case for Life (GBP 58.11; 4 stars).
2. **Cheapest:** Patience (GBP 10.16; 3 stars).
3. **Average price:** GBP 34.56.
4. **Number of 5-star books:** 19.
5. **Percentage in stock:** 100.00%.
6. **Top five highest-rated books** (ties ordered by lowest price):

| Title | Price (GBP) | Rating |
| --- | ---: | ---: |
| Princess Between Worlds (Wide-Awake Princess #5) | 13.34 | 5 |
| Princess Jellyfish 2-in-1 Omnibus, Vol. 01 (Princess Jellyfish 2-in-1 Omnibus #1) | 13.61 | 5 |
| Sophie's World | 15.94 | 5 |
| Thirst | 17.27 | 5 |
| Set Me Free | 17.46 | 5 |

7. **Cheapest 5-star book:** Princess Between Worlds (Wide-Awake Princess #5) (GBP 13.34; 5 stars).

## Business recommendation

Prioritize Princess Between Worlds (Wide-Awake Princess #5) (GBP 13.34; 5 stars); Princess Jellyfish 2-in-1 Omnibus, Vol. 01 (Princess Jellyfish 2-in-1 Omnibus #1) (GBP 13.61; 5 stars). They are both rated 5 stars and currently in stock; they are also among the cheapest in-stock 5-star titles in the scraped sample. These criteria help test a highly rated, lower-cost assortment, but do not measure actual demand.

## CEO challenge: Maximum star points for GBP 100

Each title may be purchased at most once. Only in-stock titles qualify.
The 0/1 knapsack algorithm maximizes total star points under the budget,
breaking ties in favor of the lowest total cost.

| Selected title | Price (GBP) | Rating |
| --- | ---: | ---: |
| Patience | 10.16 | 3 |
| Princess Between Worlds (Wide-Awake Princess #5) | 13.34 | 5 |
| Princess Jellyfish 2-in-1 Omnibus, Vol. 01 (Princess Jellyfish 2-in-1 Omnibus #1) | 13.61 | 5 |
| Mama Tried: Traditional Italian Cooking for the Screwed, Crude, Vegan, and Tattooed | 14.02 | 4 |
| Untitled Collection: Sabbath Poems 2014 | 14.27 | 4 |
| Sophie's World | 15.94 | 5 |
| Thirst | 17.27 | 5 |

**Selected books:** 7
**Total cost:** GBP 98.61
**Total rating score:** 31
**Remaining budget:** GBP 1.39

## Bonus: Rating distribution

| Stars | Number of books |
| ---: | ---: |
| 1 | 22 |
| 2 | 19 |
| 3 | 22 |
| 4 | 18 |
| 5 | 19 |

See `rating_distribution.png` for the chart.
