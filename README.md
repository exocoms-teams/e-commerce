# e-commerce
- Test Commit


git branch --show-current
git switch rebecca-work
git pull --ff-only origin rebecca-work "this is to pull all work done at home"

why do we need playwright? how were we able to het these information"check code"

### Source-score scale audit

The assumption that every source supplies `score_site_x` out of 10
is not valid.

- Shopify: the current collector does not send `score_site_x`.
- eBay: `seller.feedbackScore` is an aggregate feedback count, not
  a rating out of 10. Its mapping to `score_site_x` has been removed.
- TikTok and Meta: the current advertisement collectors do not
  supply `score_site_x`.
- Crowdsourcing: the inspected submission flow does not supply
  `score_site_x`.

In this implementation, `compute_trend_score()` obtains source
reliability from `winners.source_score_scraping`,
`winners.source_score_api`, or `winners.source_score_crowdsourcing`.
These values use a 0–1 scale and are clamped to that range.
`score_site_x` does not contribute to the current scoring formula.

No `normalize_source_score()` function exists in the inspected
tracked module. The ticket's hard-coded `/10` assumption refers
to a different or older implementation.

Future collectors supplying ratings must document their metric
and scale before those ratings are used in scoring. Previously
stored eBay values have not been converted by this change.