# AI policy for IT departments

A company decides which AI DX-CAD may use, and whether it may use any. The
policy is set by IT, in the registry or in a policy file; users cannot
override it. A setting the policy makes is not offered to the user, and
Settings says "set by your organisation" beside it. `dxcad doctor --report`
states the policy in force.

## Where DX-CAD reads it

Each setting is taken from the first of these that sets it:

1. `HKEY_LOCAL_MACHINE\Software\Policies\Designmatix\DX-CAD`
2. `HKEY_CURRENT_USER\Software\Policies\Designmatix\DX-CAD`
3. the policy file, `%ProgramData%\DX-CAD\policy.json` on Windows and
   `/etc/dxcad/policy.json` elsewhere.

An environment variable, `DXCAD_POLICY_FILE`, may name another policy file;
that file is then the whole policy and the registry is not read, which is a
way to try a policy out before deploying it.

## The settings

| Name | Type | What it does |
| --- | --- | --- |
| `AIFeatures` | DWORD, 0 or 1 | The master switch. 0 removes every AI surface together: the Assistant panel, its menu entry, toolbar button and shortcut; Connect Claude Desktop on the start page; the agent door (`dxcad serve`, `dxcad serve --install` and the live window link); and the AI mentions in Help and on the start page. With it off DX-CAD makes no connection to any AI provider. Modelling is unaffected: smart mates use no AI. |
| `Assistant` | DWORD, 0 or 1 | Whether the Assistant may run at all. |
| `AgentDoor` | DWORD, 0 or 1 | Whether `dxcad serve`, its `--install` and the live window link may run. With 0, `dxcad serve` refuses with the policy's message. |
| `AllowedProviders` | REG_SZ, comma-separated, or REG_MULTI_SZ | The Assistant's providers that may be used, by key: `own_key` (Anthropic, the user's own key), `openai`, `azure_openai`, `gemini`, `openai_compatible` and `account` (the DX-CAD account). The rest are not offered. Unset, all are. |
| `AllowedEndpoints` | REG_SZ, comma-separated, or REG_MULTI_SZ | The addresses an Azure OpenAI or OpenAI-compatible provider may use, each a prefix such as `https://contoso.openai.azure.com`. Unset, any. |
| `SendScripts` | DWORD, 0 or 1 | Whether a document's model script may be sent to a provider. With 0, the Assistant's tools that would answer it (`get_model`, `model_values`) are refused inside the chat with the policy's reason. |
| `SendRenders` | DWORD, 0 or 1 | Whether pictures of the view may be sent. With 0, a render the Assistant asks for is refused inside the chat with the policy's reason. |
| `SendImages` | DWORD, 0 or 1 | Whether scans and photos may be attached to a prompt and sent (the hosted Assistant add-on). With 0, the attach button is hidden whatever the licence, and paste and drop attach nothing. |
| `Message` | REG_SZ | What DX-CAD adds when it refuses, such as who to ask. |

A setting left out is allowed, so an empty policy changes nothing.

## A sample registry file

Only Azure OpenAI, in the company's own tenant; no agent door; no renders
sent. Save it as `dxcad-policy.reg` and import it, or deploy the same values
by Group Policy.

```reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\Software\Policies\Designmatix\DX-CAD]
"AIFeatures"=dword:00000001
"Assistant"=dword:00000001
"AgentDoor"=dword:00000000
"AllowedProviders"="azure_openai"
"AllowedEndpoints"="https://contoso.openai.azure.com"
"SendScripts"=dword:00000001
"SendRenders"=dword:00000000
"Message"="Ask the IT service desk, extension 4400."
```

## A sample policy file

The same policy as `policy.json`:

```json
{
  "AIFeatures": 1,
  "Assistant": 1,
  "AgentDoor": 0,
  "AllowedProviders": ["azure_openai"],
  "AllowedEndpoints": ["https://contoso.openai.azure.com"],
  "SendScripts": 1,
  "SendRenders": 0,
  "Message": "Ask the IT service desk, extension 4400."
}
```

## No AI at all

For a company that allows no AI, one setting does it:

```reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\Software\Policies\Designmatix\DX-CAD]
"AIFeatures"=dword:00000000
```

The installer offers the same as "Install without AI features", and an
unattended install takes it as `/NOAI`, which writes this value (under
`HKEY_LOCAL_MACHINE` for an install for all users, under `HKEY_CURRENT_USER`
for a per-user install):

```bat
DX-CAD-0.1.0-windows-x64-setup.exe /VERYSILENT /NOAI
```

`dxcad doctor --report` then says "AI features: off (set by your
organisation)".

An install over a DX-CAD that Claude Desktop is connected to finds the
connection, a process started from the install folder, before it copies
anything, says what it is and asks "Close it and carry on?". It is never
closed without that answer. An unattended install answers No and installs
nothing, saying how to quit Claude Desktop by hand, unless it is given
`/CLOSECONNECTION`:

```bat
DX-CAD-0.1.0-windows-x64-setup.exe /VERYSILENT /SUPPRESSMSGBOXES /CLOSECONNECTION
```

Claude Desktop connects to DX-CAD again the next time it is started. DX-CAD's
own window, still open, is asked to be closed as before.
