"""Render an existing GentleSort plan as a self-contained, inert review report."""
from html import escape
import json
import unicodedata


def visible_name(value: str) -> str:
    """Keep readable Unicode but expose control/bidi/format characters literally."""
    return ''.join(
        json.dumps(c, ensure_ascii=True)[1:-1]
        if unicodedata.category(c).startswith('C') else c for c in value
    )


def render_preview(plan: dict) -> str:
    groups = []
    for decision, title in [('review', 'Needs review'), ('suggest', 'Folder suggestions')]:
        rows = [r for r in plan['items'] if r['decision'] == decision]
        cards = []
        for row in rows:
            destination = row.get('proposed_directory') or 'No folder proposed'
            candidate = row.get('candidate') or 'None'
            cards.append(
                '<article class="file" data-decision="' + decision + '">'
                '<h3><code>' + escape(visible_name(row['name'])) + '</code></h3>'
                '<dl><div><dt>Proposed folder</dt><dd>' + escape(destination) + '</dd></div>'
                '<div><dt>Model candidate</dt><dd>' + escape(candidate) + '</dd></div>'
                '<div><dt>Reason</dt><dd><code>' + escape(row['reason']) + '</code></dd></div>'
                '</dl></article>'
            )
        groups.append('<section aria-labelledby="' + decision + '"><h2 id="' + decision
                      + '">' + title + ' (' + str(len(rows)) + ')</h2>'
                      + (''.join(cards) or '<p>No items in this group.</p>') + '</section>')
    summary = plan['summary']
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>GentleSort — review plan</title><style>
*{box-sizing:border-box}body{margin:0;background:#f5f4ee;color:#17352d;font:17px/1.6 system-ui,sans-serif}
main{max-width:980px;margin:auto;padding:40px 24px}h1{font-size:clamp(2rem,5vw,3rem);line-height:1.15;margin:.3em 0}
h2{margin:2rem 0 1rem;font-size:1.5rem}h3{font-size:1.1rem;margin:0 0 1rem}p{max-width:75ch}
.eyebrow{font-size:.8rem;letter-spacing:.12em;font-weight:700}.note{border-left:5px solid #8c5910;padding:12px 18px;background:#fff5d9}
.summary{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}.stat{flex:1 1 160px;background:#dfeae3;border-radius:12px;padding:16px}
.stat strong{font-size:2rem;display:block}.file{padding:20px;background:white;border:1px solid #c7d2cc;border-radius:12px;margin:12px 0}
.file[data-decision=review]{border-left:5px solid #8c5910}dl{display:grid;grid-template-columns:1fr 1fr 2fr;gap:16px;margin:0}
dt{font-size:.8rem;font-weight:700}dd{margin:2px 0}code{font-size:.9em;overflow-wrap:anywhere;white-space:pre-wrap;unicode-bidi:plaintext}
a{color:#145647;text-underline-offset:4px}a:focus-visible{outline:3px solid #8c5910;outline-offset:4px}
footer{border-top:1px solid #c7d2cc;margin-top:32px;padding-top:18px;font-size:.9rem}
@media(max-width:600px){main{padding:24px 16px}dl{grid-template-columns:1fr}.file{padding:16px}.stat{flex-basis:120px}}
</style></head><body><main><header><div class="eyebrow">OFFLINE · FILENAMES ONLY · PREVIEW</div>
<h1>Less filing.<br>Every choice stays yours.</h1>
<p>This is a saved review plan from GentleSort. The machine-learning model suggests folders from filenames; it does not interpret document contents.</p>
<p class="note"><strong>Nothing was moved, renamed or deleted.</strong> Review every item. A model candidate is diagnostic, not permission to file it. Scores are not calibrated probabilities of correctness.</p>
</header><div class="summary" aria-label="Plan summary">'''+''.join(
        '<div class="stat"><strong>'+str(summary[key])+'</strong>'+label+'</div>'
        for key,label in [('entries','Entries'),('suggestions','Suggestions'),('needs_review','Need review')]
    )+'</div>'+''.join(groups)+'''
<footer><p>Saved preview only. This page runs no model and has no apply action. To generate a new plan, run the Python CLI on a trusted local directory.</p>
<p><a href="plan.json">Full plan JSON</a> · <a href="review.md">Plain Markdown report</a></p>
<p>Reports contain filenames. Keep them private if those names are sensitive.</p></footer></main></body></html>'''
