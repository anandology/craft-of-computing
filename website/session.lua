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
-- A line starting with "$ " is a command; everything else is output. The "$"
-- is stripped here and drawn back by CSS (see styles.css), so it is not part
-- of the page text: a student who selects a command line and copies it gets
-- the command, without the prompt. There is no copy button on these blocks --
-- a transcript has no single right thing to copy, so selecting the wanted line
-- is left to the reader.
--
-- A command ending in "\" continues on the next line, which is treated as part
-- of the command rather than as output.

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

  local html = { '<pre class="session"><code>' }
  local continuing = false

  for line in (el.text .. "\n"):gmatch("([^\n]*)\n") do
    local class, text

    if continuing then
      class, text = "cmd-cont", line
    else
      local command = line:match("^%$ ?(.*)$")
      if command then
        class, text = "cmd", command
      else
        class, text = "out", line
      end
    end

    -- Only a command can continue; an output line ending in "\" is just output.
    continuing = (class ~= "out") and text:match("\\%s*$") ~= nil

    table.insert(html, '<span class="' .. class .. '">' .. esc(text) .. "</span>\n")
  end

  table.insert(html, "</code></pre>")
  return pandoc.RawBlock("html", table.concat(html))
end
