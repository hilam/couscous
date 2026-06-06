## Delta for oauth-authentication

No requirement changes. The `oauth-authentication` spec at `openspec/specs/oauth-authentication/spec.md` remains correct.

This change corrects the implementation of "OAuth state stored in Flet session" (lines 23-24 of the spec) to use the proper `SessionStore` API (`set`/`get`/`remove`) instead of dict-style access (`[]` / `.pop()`). The behavioral contract — store state, retrieve state, clean state after callback — is unchanged.
