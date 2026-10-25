---
title: "GentleSort: the laziest file tidier is the one that never touches your files"
published: false
tags: devchallenge, hf26challenge
---

UNPUBLISHED WORKING DRAFT — not submitted. Missing public code and demo links must be replaced after review, not published as placeholders. The local actual-output replay video is ready, but not publicly hosted. This draft must not be presented as Rahmatulla's personal hands-on experience before he has reviewed it.

## What I Built

GentleSort turns a small folder of business documents into a review plan. It looks at names, not document contents. Its four suggested folders are Agreements, Correspondence, Invoices and Reports.

The intentionally lazy part is the stopping point. It does not ask someone to configure twenty filename rules, and it does not ask them to trust a bulk move. A person reads the plan and decides what to do. There is no apply button or command.

## Demo

[REQUIRED BEFORE PUBLICATION: insert a public link/embed for the reviewed demo video. Local file: demo_video/GentleSort_Demo_20261020.mp4.]

The 73-second video replays real CLI output on eight synthetic files: five receive folder suggestions and three remain for review. Names and SHA-256 hashes match before and after. It is an output replay with extended reading pauses, not a desktop recording or performance benchmark. Full captured stdout/stderr and verification data are included. The fixture extensions are labels, not valid sample PDF/Word documents.

The current CLI also writes an offline `review.html` report. It groups items needing review before folder suggestions and can be opened without installing Python. This is a saved result, not browser-based model inference. The original video does not show this later interface addition.

## Code

[REQUIRED BEFORE PUBLICATION: public repository URL, newly created during the challenge window.]

## How I Built It

The decision-making core is a small scikit-learn model: character TF-IDF features and logistic regression trained on 48 original synthetic names. No cloud API or pretrained download is involved. Unlike a list of hard-coded category words, the labels affect the fitted classifier; a test verifies that swapping labels changes its answer.

Prediction is not permission. A low score, narrow margin or weak similarity to training examples leads to review. Unsupported extensions, control characters, case collisions and symbolic links also remain for review. No folder is traversed recursively.

Twenty-six automated tests passed, including checks that hostile filename markup stays literal in the HTML report and that all decisions match the generated JSON. A fresh CLI run preserved the names and hashes of ten synthetic files. Sixteen hand-written holdout names produced sixteen matching candidate labels, with one withheld from suggestions. That small result is evidence of a working prototype, not a claim of production accuracy. The evaluation set is public and inspectable, not an independent blind benchmark. There has been no real-user time-savings study. Targeted Chromium checks subsequently passed at 1280px, 375px and 320px, with working keyboard focus and sibling-report links. The desktop and narrow layout were visually reviewed. Real-device, Windows, screen-reader and full accessibility checks remain outside this validation.

## Why Does Open Innovation Matter?

The training examples, feature extraction and classifier are inspectable. Someone can change the categories and retrain without sending business filenames to a remote service. Once dependencies are installed, the application can run disconnected. A closed API could support a similar workflow, but it is unnecessary for this deliberately small task.

The tradeoff is coverage. An opaque scan number has no meaningful category evidence, and a misleading name can fool this model. A bigger model would not justify silent changes either. The useful boundary here is not intelligence without limits; it is a modest prediction with an explicit place for uncertainty.

No partner technology is claimed. The prototype uses classical open-source machine learning, not an LLM. It was prepared with AI assistance and still needs personal review before any entry is published.
