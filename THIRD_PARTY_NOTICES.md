# Dependency and data licensing

Only original application source, original synthetic data, documentation and QA outputs are distributed in this package. No dependencies, binary libraries, external model weights, customer files or third-party datasets are bundled. The fitted model is rebuilt from the included data, not loaded from a pickle.

The installed package metadata and installed license files were checked. The Python package dependencies below permit commercial use under BSD-style terms; installations must retain their own full notices. The upstream URLs are references; the joblib/threadpoolctl/SciPy versioned GitHub URLs could not be fetched by the web reader in this run, so their installed license files were used. Binary wheels can include separately licensed native components (for example GCC/OpenMP runtime and BLAS). Their package license files remain authoritative; this source-only package does not relicense or redistribute those binaries.

| Dependency | Tested version | Core license | Official source |
| --- | --- | --- | --- |
| scikit-learn | 1.8.0 | BSD-3-Clause | https://github.com/scikit-learn/scikit-learn/blob/1.8.0/COPYING |
| NumPy | 2.3.5 | BSD-3-Clause | https://numpy.org/doc/stable/license.html |
| SciPy | 1.17.0 | BSD-3-Clause | https://github.com/scipy/scipy/blob/v1.17.0/LICENSE.txt |
| joblib | 1.5.3 | BSD-3-Clause | https://github.com/joblib/joblib/blob/1.5.3/LICENSE.txt |
| threadpoolctl | 3.6.0 | BSD-3-Clause | https://github.com/joblib/threadpoolctl/blob/3.6.0/LICENSE |

All training, holdout and demo names were authored for this prototype and are covered by the project's MIT license. They are not client examples or evidence of customer engagements. The core classifier uses no media assets or foundation models. The optional demo renderer's font/tool notices follow.

## Optional demo rendering tools (20 October 2026 addition)

The new original video/PNG scenes contain rendered text and layout authored for this project. The classifier itself has no new dependencies. The rendering/checking scripts optionally use Pillow 12.3.0 (installed metadata: MIT-CMU; https://pillow.readthedocs.io/en/stable/about.html). They call the separately installed FFmpeg 6.1.1 GPL-enabled build and ffprobe as command-line tools (https://ffmpeg.org/legal.html); these executables and their libraries are **not bundled**. This is not a proprietary license for FFmpeg, and no claim about patent clearance in every jurisdiction is made.

The rendered text uses the locally installed DejaVu Sans Mono font: DejaVu changes are public domain, with the Bitstream Vera permission notice (Copyright (c) 2003 Bitstream, Inc.; https://dejavu-fonts.github.io/License.html). The installed `/usr/share/doc/fonts-dejavu-core/copyright` permission text was read. No TTF/font file is distributed. No stock graphics, music, voice, client content or other external media assets are used. Upstream tool/font licensing is distinct from the project's MIT license.

## scikit-learn core notice (from installed 1.8.0 COPYING)

BSD 3-Clause License

Copyright (c) 2007-2024 The scikit-learn developers.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## Optional browser QA tools (22 October 2026)

QA-only packages: `playwright-core` 1.62.1 (Apache-2.0, installed LICENSE checked) and `@sparticuz/chromium` 153.0.0 (MIT, installed LICENSE checked). They are not application runtime dependencies and are not bundled. Chromium itself and bundled native components retain their upstream notices; no browser binary or third-party fonts are redistributed. The original `browser_qa.cjs` is covered by this project's MIT license. Internal browser captures were inspected for QA and are not distributed.
