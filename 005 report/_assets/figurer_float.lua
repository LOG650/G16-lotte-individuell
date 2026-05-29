-- Slår sammen «bilde-avsnitt» + påfølgende kursiv bildetekst til ett flytende,
-- sentrert figur-objekt. Beholder den manuelle figurnummereringen (Figur 1.1, 4.1 ...)
-- ved å sette teksten manuelt i kursiv, uten LaTeX sin \caption (som ville auto-nummerert).
function Pandoc(doc)
  local blocks = doc.blocks
  local out = {}
  local i = 1
  while i <= #blocks do
    local b = blocks[i]
    local nxt = blocks[i + 1]
    local isImg = (b.t == "Para" and #b.content == 1 and b.content[1].t == "Image")
    local isCap = (nxt and nxt.t == "Para" and #nxt.content == 1 and nxt.content[1].t == "Emph")
    if isImg and isCap then
      table.insert(out, pandoc.RawBlock("latex", "\\begin{figure}[!htbp]\n\\centering"))
      table.insert(out, b) -- bildet -> \includegraphics
      local capPara = { pandoc.RawInline("latex", "\\par\\vspace{3pt}{\\itshape\\small ") }
      for _, il in ipairs(nxt.content[1].content) do
        table.insert(capPara, il)
      end
      table.insert(capPara, pandoc.RawInline("latex", "}"))
      table.insert(out, pandoc.Para(capPara))
      table.insert(out, pandoc.RawBlock("latex", "\\end{figure}"))
      i = i + 2
    else
      table.insert(out, b)
      i = i + 1
    end
  end
  return pandoc.Pandoc(out, doc.meta)
end
