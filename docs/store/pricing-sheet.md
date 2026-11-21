# Store pricing sheet (draft, 2026-10-11)

Status: no real costs loaded yet. Costs come from the Printify API (GET /v1/catalog/blueprints/{id}/print_providers/{pp}/variants.json and shipping.json) once an account token exists. Nothing is priced publicly until Joey approves.

## Formula
net price floor = (base cost + provider shipping + tax buffer) / (1 - card fee rate) + fixed card fee + target profit

- Tax buffer: 8 to 10 percent of cost. Printify charges tax on its own cost and withholds it; in a Pop-Up store an order whose margin cannot cover it is cancelled and refunded.
- Card fee: Shopify Basic online 2.9% + 30c. Pop-Up Stripe fee is not published on Printify pages: read it during Stripe setup before quoting net profit.
- Target net margin: at least 35 to 40 percent on tees and mugs. Round to .00 or .99 style price points.
- Shipping: charge what the provider charges. Free shipping only as a threshold set 15 to 25 percent above average order value.

## Worked example (sourced, mug)
Printify help article "How does the payment process work": retail $8.98, shipping $6.09, tax $1.67 collected; Printify cost $4.09 + shipping $6.09 = $10.18; profit $4.89 (54 percent of retail). That mug price is too low for a devotional product and shows why the floor formula matters.

## SKU table (fill from API)
| SKU | Blueprint | Provider | Base cost | Ship (US) | Floor | Proposed | Net |
|---|---|---|---|---|---|---|---|
| tee-classic | to verify | to verify | n/a | n/a | n/a | n/a | n/a |
| mug-11oz | to verify | to verify | n/a | n/a | n/a | n/a | n/a |
| tote-canvas | to verify | to verify | n/a | n/a | n/a | n/a | n/a |
| poster-matte | to verify | to verify | n/a | n/a | n/a | n/a | n/a |
| cards-prayer | to verify, optional | to verify | n/a | n/a | n/a | n/a | n/a |
