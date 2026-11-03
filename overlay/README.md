# Stable compatibility overlay

This fork preserves Zulko/moviepy history. The stable branch starts at upstream v2.2.1 (`f515b100e1fd069da6f29d5b01b1d42b52d8068d`); the master branch retains upstream development history.

The library overlay backports the Pillow compatibility portion of upstream commit `97316f37f6a8d3843abfb53eba8f3bb0ea46a008`: replace the removed private multiline-spacing method with the upstream public textbbox calculation, and remove the obsolete Pillow upper bound. It carries no application-specific behavior.

The compatibility regression exercises actual multiline text rendering with current Pillow. The repository gate installs declared dependencies and runs upstream tests on the shared runner.

The current FFmpeg bundle also needs three narrow compatibility fixes: parse the
`n` release-tag prefix shared by FFmpeg and FFplay, recognise the title-case
`Display Matrix` side-data field, and select supported `yuva420p` for transparent
VP9 output. Existing upstream assertions remain unchanged. New regressions cover
both release-version callers, rotation metadata and real VP9 alpha round trips.

The verifier derives its worker count from the contract and limits BLAS/FFmpeg
thread pools only inside its test environment. It also proves that restoring the
old Pillow fallback causes the clipping regression to fail on an isolated copy.
Production library defaults and shared runner limits are unchanged.

When upstream publishes a stable release containing this change, compare it against this stable base, run the same gate and retire the compatibility overlay if it is redundant. Preserve the upstream remote and review `upstream/v2.2.1...stable` to inspect the overlay.
