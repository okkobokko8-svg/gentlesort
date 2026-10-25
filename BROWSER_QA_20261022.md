# GentleSort targeted browser QA — 22 October 2026

The saved synthetic HTML report now has executed browser evidence. No classifier or renderer code was changed in this checkpoint.

Environment: Linux x86_64, Chromium 153.0.8010.0, playwright-core 1.62.1, @sparticuz/chromium 153.0.0. The exact Node runtime is recorded in the JSON evidence.

Four browser cases passed:

| Case | Actual checks |
| --- | --- |
| 1280 × 900 | Ten file cards match the saved plan by name and decision; six suggestions/four reviews; no horizontal overflow; English language/main landmark and two report links present |
| 375 × 812 | Same checks; responsive single-column file details |
| 320 × 800 | Same checks; long filenames wrap within the viewport |
| Keyboard and local links | Tab reaches JSON then Markdown in order; the focused link has a visible 3px solid outline; both sibling files load with nonempty text |

The browser context was offline throughout. There were zero HTTP/HTTPS requests and zero page errors. The SHA-256 hashes of review.html, plan.json and review.md matched before and after all browser checks. Exact observations and hashes are in `browser_qa_20261022.json`.

Full-page 1280px and 320px captures were visually inspected: headings, warning, counters, ten cards and footer remain readable without clipping or overlap. The 375px case was checked through rendered DOM/layout assertions. Internal browser captures are not included in the deliverable.

## Reproduce

Use an isolated Node directory with `playwright-core@1.62.1` and `@sparticuz/chromium@153.0.0` installed. Make those modules available on NODE_PATH, then run:

```sh
node browser_qa.cjs qa_20261022/preview browser_qa_20261022.json
```

An optional fourth argument is a directory for local inspection captures. These contain synthetic filenames only, but keep real customer filenames private.

Setup caveat: the first Sparticuz extraction on this host reported an EINVAL chown error for /tmp/fonts after unpacking the Chromium executable. The unpacked browser passed `--version`; repeating the check then ran successfully using the existing executable and host fonts. This setup is not guaranteed to work unchanged on another operating system. No package binaries, browser or external fonts are shipped in the ZIP. The earlier failed Playwright CDN download remains historical evidence, not the current browser outcome.

## Limits

This is targeted functional and visual QA, not a WCAG certification, screen-reader audit, real-phone test, Windows test, cross-browser comparison, production classifier evaluation or real-user usability study. The 26 Python unit-test result and ten-file CLI integrity result are the earlier checkpoint; this run does not relabel them as new tests. Public hosting, contest entry and owner approval remain separate unfinished steps. No money, account or contract was involved.
