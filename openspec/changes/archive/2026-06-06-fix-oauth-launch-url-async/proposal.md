## Why

`ft.UrlLauncher().launch_url()` is an async method, but `_oauth_click()` in `oauth_buttons.py` calls it synchronously without `await`. This causes a `RuntimeWarning: coroutine was never awaited` and the OAuth authorization URL never opens — the button appears dead to the user. `page.launch_url()` is the synchronous equivalent and works in the same context.

## What Changes

- Replace `ft.UrlLauncher().launch_url(uri)` with `page.launch_url(uri)` in `_oauth_click()`

## Capabilities

### New Capabilities

None — this is a bug fix.

### Modified Capabilities

None — the `oauth-button-component` spec already requires the system to "open the provider's authorization URL in the browser." The behavioral contract is unchanged; only the API call is corrected.

## Impact

- `app/controls/oauth_buttons.py` — line 9
