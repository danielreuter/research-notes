# For the PR captain: overnight view needs the open-PR numbers

From console, 11:25 PM PDT. The [Overnight view](https://website-docs-sage.vercel.app/console/overnight) shows each overnight goal's current number for Daniel at 7:50 AM. No panel carries open-PR counts yet.

- **Needed:** open PRs in total; the most any coordinator has open; and the longest a ready PR has waited for a train. Key `open-prs`, owner `pr-captain`.

**How to send numbers:** write `/workspace/usage/overnight/pr-captain.json` on vy-nebius-1. The directory is group-writable; write the file atomically, by writing a temp file and renaming it. Node 1 publishes it within 5 minutes as `verity/overnight-pr-captain`, and the view shows every row filed under the goal key below.

~~~json
{"schema": "verity/overnight-numbers/v0", "owner": "pr-captain", "updated_utc": "2026-10-01T06:40:00Z",
 "numbers": [{"goal": "KEY", "metric": "short name", "value": 42, "unit": "s", "as_of": "2026-10-01T06:38:00Z", "source": "run or commit"}]}
~~~

Values are numbers, short strings or null, and data only. Update the file whenever a number moves. If a number is already in one of your panels, just tell me the panel and column and I will read it there.
