-- Mark teaching sections for the Codex-first learning buttons in learn.js.
-- Only the real section anchor is embedded; the browser resolves it against the
-- active course page so previews and later deployments never point at the source site.

-- A model line is a paragraph that opens in bold with "The model:", either as a label
-- ("**The model:** a flow is ...") or as a whole bold sentence ("**The model: a flow is ...**").
local function is_model_line(block)
  if block.t ~= "Para" or #block.content == 0 then return false end
  local first = block.content[1]
  return first.t == "Strong" and pandoc.utils.stringify(first):match("^The model:") ~= nil
end

local function has_model_line(block)
  if is_model_line(block) then return true end
  local found = false
  if block.t == "Div" or block.t == "BlockQuote" then
    pandoc.Blocks(block.content):walk({
      Para = function(p) if is_model_line(p) then found = true end end,
    })
  end
  return found
end

local function is_marker(block)
  return block.t == "RawBlock"
    and (block.format == "html" or block.format == "markdown")
    and block.text:match("^%s*<!%-%-%s*learn%s*%-%->%s*$") ~= nil
end

-- Anchors cited by the practice form, as a set of "<chapter>.qmd#<anchor>". Read once per
-- render; a missing or unreadable file means no practice sections.
local practice_sections = nil
local function practice_cited()
  if practice_sections then return practice_sections end
  practice_sections = {}
  local f = io.open("practice/version-a.json", "r")
  if not f then return practice_sections end
  local ok, bank = pcall(pandoc.json.decode, f:read("a"), false)
  f:close()
  if not ok or type(bank) ~= "table" then
    quarto.log.warning("learn: practice/version-a.json could not be read; no practice buttons")
    return practice_sections
  end
  for _, it in ipairs(bank.items or {}) do
    for _, s in ipairs(it.sections or {}) do practice_sections[s] = true end
  end
  return practice_sections
end

local function page_name()
  local input = quarto.doc.input_file or ""
  local name = input:match("([^/\\]+)%.[^.]+$") or input
  return name .. ".html"
end

function Pandoc(doc)

  -- pass 1: which ## sections state a model, are cited by the practice form, or carry a marker
  local marked, section = {}, nil
  local cited = practice_cited()
  local chapter = page_name():gsub("%.html$", ".qmd")
  for _, block in ipairs(doc.blocks) do
    if block.t == "Header" and block.level <= 2 then
      section = (block.level == 2) and block.identifier or nil
      if section and cited[chapter .. "#" .. section] then marked[section] = true end
    elseif section and section ~= "" and (has_model_line(block) or is_marker(block)) then
      marked[section] = true
    end
  end

  -- pass 2: drop the markers and tag the marked headings
  local out, found = pandoc.Blocks({}), 0
  for _, block in ipairs(doc.blocks) do
    if not is_marker(block) then
      if block.t == "Header" and block.level == 2 and marked[block.identifier] then
        block.attributes["data-learn"] = "#" .. block.identifier
        found = found + 1
      end
      out:insert(block)
    end
  end
  doc.blocks = out

  if found > 0 then
    quarto.doc.add_html_dependency({
      name = "learn-button",
      version = "3.0.0",
      scripts = { "learn.js" },
      stylesheets = { "learn.css" },
    })
  end
  return doc
end
