## Delta for oauth-button-component

No requirement changes. The `oauth-button-component` spec at `openspec/specs/oauth-button-component/spec.md` remains correct.

This change corrects the implementation of the "Button click when provider is configured" scenario (line 16) to use `page.launch_url()` instead of `ft.UrlLauncher().launch_url()`. The behavioral contract — "opens the provider's authorization URL in the browser" — is unchanged. The fix replaces an unawaited async call with its synchronous equivalent.
