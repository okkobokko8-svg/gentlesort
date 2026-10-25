# GentleSort — less filing, no silent changes

An offline, filenames-only machine-learning prototype. It suggests one of four folders for business documents and leaves uncertain items for human review. It never opens document contents, traverses subfolders, or moves, renames or deletes input files. There is deliberately no `apply` command.

Status: original prototype started on 19 October 2026 UTC (20 October in Tashkent), during DEV Week 3. Not published, submitted, awarded, or a paid customer project. Not a continuation of ReviewQueue.

## Run

Python 3.12 was tested. Use a trusted local directory and a virtual environment. Dependency installation needs internet/package downloads; inference does not. Do not replace an existing environment's dependencies without reviewing the pins.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python gentlesort.py /absolute/path/to/small-inbox --output /absolute/path/to/new-preview
.venv/bin/python -m unittest -v
.venv/bin/python evaluate.py
.venv/bin/python run_qa.py --output /absolute/path/to/new-qa-directory
```

The output parent must exist, the output directory must not exist, and output must be outside the source directory. Inputs are limited to 1,000 top-level entries. Only `.pdf`, `.docx`, and `.txt` names receive model suggestions; extensions are not a check of file format validity. Other entries remain visible for review.

Open `review.html` in a browser, or read `plan.json` / `review.md`. The HTML is a saved report, not a live classifier. It has no scripts, external resources, or apply action. Review every suggestion, including high-scoring ones. A `candidate` on a review item is diagnostic, not permission to move it. Only `proposed_directory` on a suggestion gives a possible destination; it still requires human judgment.

## The open-source AI core

scikit-learn's character TF-IDF vectorizer and logistic regression learn from 48 original, synthetic filenames in four categories: Agreements, Correspondence, Invoices and Reports. There are English, Russian, Turkish and Uzbek examples, not a claim of broad multilingual support. The model fits locally on each run. No LLM, pretrained weights, API, account, network request or customer dataset is used by this application.

Thresholds require a model score of at least 0.60, a class margin of 0.25 and training-example cosine similarity of 0.30; otherwise the result is review-only. These are manually chosen heuristics, not calibrated probabilities of correctness. `test_model_really_learns_from_labels` changes the labels and confirms that the learned prediction changes. This is not a keyword-routing-only wrapper.

## Evidence and limits

The included `qa/` contains outputs of actual tests and CLI execution. The generated input files are excluded from the ZIP (one deliberately has an unsafe control character in its name); `run_qa.py` recreates them in a new directory. Twenty-three unit tests passed. On 16 hand-written holdout names, 16 candidate labels matched, 15 were suggested and one was withheld for review. The majority-category baseline is 4/16. Unknown and ambiguous probes were withheld. The CLI demo preserved the names and SHA-256 hashes of all 10 synthetic files.

This is a tiny, inspectable demonstration dataset, not blind external validation. No measured real-user time saving, real-client accuracy, or general language/legal expertise is claimed. A meaningful production evaluation needs representative consented examples, separately frozen evaluation data, error analysis and threshold calibration. Generic names such as `scan001.pdf` carry no useful semantic evidence. Misleading names can be confidently misclassified. This tool does not interpret documents or provide legal advice.

The app itself does not read document contents, but the user's OS, antivirus and dependencies are outside that narrow claim. Reports expose filenames and the selected directory path: keep them private if names are sensitive. Do not run on hostile/shared directories that another process is changing. Symlink checks are safeguards, not a race-proof sandbox. If output writing fails, a partial newly created output directory may remain; the program never deletes it automatically.

## Before any contest submission

See `OPPORTUNITY.md`. The article in `DEV_DRAFT.md` is an unpublished draft with explicit missing public links. A public new repository, public demo hosting/link, personal review and final owner approval are still required. This package is not an entry receipt. Classical ML appears consistent with the broad open-source-AI prompt, but judges alone determine eligibility; no foundation model or partner-category use is claimed.

## Actual-output demo video — added 20 October 2026

`demo_video/GentleSort_Demo_20261020.mp4` is a 73-second, 1600x900, 12 fps silent video replay of **actual captured subprocess output**, plus inspection of the actual generated plan and fixture hashes. It is prominently labelled as a replay, **not a desktop screen recording**. Static output is held on screen for readability; presentation duration is not execution latency. No fake command results or personal hands-on claims were added.

This separate run uses eight safe synthetic filenames: five suggestions, three review items. All eight names/content hashes matched afterwards; the 23 tests passed again. The earlier ten-file QA above remains a separate run, not a claim that the video shows ten inputs. The classifier reads names only; the independent integrity verifier reads synthetic fixture bytes to hash them.

`demo_capture/execution.json` retains full stdout/stderr, argument arrays, process exit codes and before/after hashes. All six source PNG scenes were visually inspected; six decoded samples were checked against them numerically, with two final encoded frames also visually inspected after quality tuning. `demo_video/video_qa/verification.json` records full decode success, metadata and encoded-scene/source comparisons. No browser screenshot, customer file or desktop session was captured. No public video/repository/DEV entry has been published.

To reproduce in **new** directories, install the optional `requirements-demo.txt`, provide FFmpeg/ffprobe and a commercially usable font, then run:

```sh
python3 capture_demo.py --output new_capture
python3 render_demo.py new_capture --output new_video --font /absolute/path/to/DejaVuSansMono.ttf
python3 verify_video.py new_video
```

The supplied rendering workflow was tested on Linux only. The pinned Python executable path in the recorded arguments reflects the actual capture environment, not a command that Windows users must copy.

Code and original synthetic data: MIT, see `LICENSE`. Dependencies are not bundled; see `THIRD_PARTY_NOTICES.md`. Prepared with AI assistance; human review remains necessary before public release.

## Browser-readable review report — added 22 October 2026

Each new CLI run now creates `review.html` alongside the original JSON and Markdown. The report puts review-only items first, keeps original Unicode filenames readable, exposes control/bidi characters as literal escapes, and shows model candidates separately from proposed folders. Filename text is escaped as data. The page uses semantic headings and a narrow-screen layout with no JavaScript, network resources, or apply action.

An actual ten-file synthetic CLI run is in `qa_20261022/preview/`; open `review.html` after extracting this ZIP. The independently recorded source names and SHA-256 hashes matched 10/10 after generation. All 26 unit tests passed, including three report checks covering exact row/decision counts, hostile filename markup, bidi characters, and empty folders. The 16-name synthetic holdout remains 16 matching candidate labels; it is not independent real-world validation. The original 73-second video predates this report and does not show the new HTML interface.

HTML structure and data checks passed. Targeted browser QA was subsequently completed on 22 October with Chromium 153: desktop 1280px and narrow 375px/320px layouts, exact file/decision matching, keyboard focus, and both sibling-report links passed. Desktop and 320px captures were visually reviewed; they are internal QA captures and are not bundled. This is not a full accessibility audit or a Windows/real-phone test. See `BROWSER_QA_20261022.md` and `browser_qa_20261022.json` for scope and reproduction. No public repository, hosting or entry was created.
