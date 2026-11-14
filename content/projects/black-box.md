---
title: Black Box, the flight recorder for AI agents
description: Black Box records every model and tool call an AI agent makes in a tamper-evident SHA-256 hash chain that anyone can verify offline. A project by Daiwik Khedekar.
slug: projects/black-box
image: img/blackbox.jpg
url: https://tryblackbox.dev
---
# black box
<div class="meta">the flight recorder for ai agents · [tryblackbox.dev](https://tryblackbox.dev)</div>

![Black Box](/img/blackbox.jpg)

when an ai agent goes wrong, can you prove what it actually did?

usually no

the logs are scattered everywhere

the agent's own trace is literally the thing under review

and anyone with access can quietly edit the record

## so black box
- sits at a gateway outside the agent
- records every model call and tool call
- seals every entry in a sha-256 hash chain
- change one entry and the whole chain breaks
- anyone can verify the log offline

built for teams shipping agents, and the insurers covering them

-dk
