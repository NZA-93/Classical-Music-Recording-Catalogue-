# Community layer (not editorial)

Public comments that help review identity matches and author the site.

| Path | Role |
|---|---|
| `data/community/comments.json` | Community notes (`layer: community`) |
| `data/editorial/` | **Critic-signed** editorial entries only (named role; lands on main) |
| `data/statements/` | **Human-ratified** assessment facts only |

Community text is shown on the online review board (`docs/review/`) and must
never be copied into statements, scores, or signed editorial prose by a
harvest or seed agent. Critic writes the entry; community notes are briefing
only.

To add a comment:

1. Open a GitHub issue with the **Community review comment** template, or
2. PR a change to `comments.json`, or
3. Locally: `python3 agents/community_comments.py add --target … --author github:you --body "…"`

Owner (repository owner login) alone runs `make review-apply` / the
**Review apply** workflow to land accepted identity decisions.
