# SublimeFmt

Sublime Text 3 plugin for running code formatters such as `gofmt`, `ocp-indent`, etc. on save.

## Prereqs

If you're running on a Mac, you'll want to install the [FixMacPath](https://github.com/int3h/SublimeFixMacPath) plugin, so that other plugins have access to your `$PATH`.

## Configuration options

Configuration is available under Preferences > Package Settings > SublimeFmt.

You'll want to create formatter entries under the `formatters` object:

```
{
  "formatters": [
    {
      "cmd": "ocp-indent",
      "extensions": [".ml"]
    },
    {
      "cmd": "black --py36 -",
      "extensions": [".py"],
      "use_stdin": true
    }
  ]
}
```

A formatter configuration has two required parameters:

Name | Type | Description
--- | --- | ---
`cmd` | string | Absolute path to formatting command. SublimeFmt assumes that the command takes an input filename as its last argument, and emits the result to stdout.
`extensions` | array<string> | The plugin will only run for files with extensions specified here.
`use_stdin` | bool | By default, the plugin will run `cmd` using the source file as a command-line argument. By setting this configuration parameter to `true`, the plugin will instead pipe the contents of the source file to the formatter's stdin.

You can also further restrict where the formatter runs by using exclude and include paths:

Name | Type | Description
--- | --- | ---
`folder_exclude_path` | array<string> | The plugin will ignore files whose paths contain patterns in this setting. Defaults to `[]` (no paths will be excluded).
`folder_include_path` | array<string> | If this setting is non-empty, the plugin will only run for files whose paths are specified in this setting. Defaults to `[]` (all paths will be accepted, except those excluded by `folder_exclude_path`).

SublimeFmt will run the first formatter whose settings match the path of the file being saved.
