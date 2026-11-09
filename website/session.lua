-- Renders a ```session block as a terminal transcript: commands and their
-- output interleaved, the way they appear on screen.
--
-- Write it as it looks in the terminal, prompt and all:
--
--     ```session
--     $ magick --version
--     Version: ImageMagick 7.1.2-18
--     ```
--
-- A line starting with "$ " is a shell command, and one starting with ">>> "
-- is a Python command, typed at the Python or MicroPython REPL; everything
-- else is output. The prompt is stripped here and drawn back by CSS (see
-- theme.scss), so it is not part of the page text: a student who selects a
-- command line and copies it gets the command, without the prompt.
--
-- A block of Python commands with no output gets a copy button, which copies
-- the commands alone. Other blocks get none: a transcript with output has no
-- single right thing to copy, so selecting the wanted line is left to the
-- reader.
--
-- A shell command ending in "\" continues on the next line, which is treated
-- as part of the command rather than as output.

local function esc(s)
  s = s:gsub("&", "&amp;")
  s = s:gsub("<", "&lt;")
  s = s:gsub(">", "&gt;")
  return s
end

function CodeBlock(el)
  if not el.classes:includes("session") then
    return nil
  end

  local lines = {}
  local continuing = false
  local has_output, has_python = false, false

  for line in (el.text .. "\n"):gmatch("([^\n]*)\n") do
    local class, text

    if continuing then
      class, text = "cmd-cont", line
    else
      local command = line:match("^%$ ?(.*)$")
      local python = line:match("^>>> ?(.*)$")
      if command then
        class, text = "cmd", command
      elseif python then
        class, text = "cmd py", python
        has_python = true
      else
        class, text = "out", line
        has_output = true
      end
    end

    -- Only a shell command can continue; a line ending in "\" is otherwise
    -- just what it is.
    continuing = (class == "cmd" or class == "cmd-cont")
      and text:match("\\%s*$") ~= nil

    table.insert(lines, '<span class="' .. class .. '">' .. esc(text) .. "</span>")
  end

  local pre = '<pre class="session"><code>' .. table.concat(lines, "\n") .. "</code></pre>"

  -- Quarto's copy script copies the text of the <code> beside the button, so
  -- reusing its scaffold and button gives the same button, icon and
  -- "Copied!" as every other code block.
  if has_python and not has_output then
    pre = '<div class="code-copy-outer-scaffold">' .. pre
      .. '<button title="Copy to Clipboard" class="code-copy-button"><i class="bi"></i></button></div>'
  end

  return pandoc.RawBlock("html", pre)
end
