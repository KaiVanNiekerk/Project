-- Quarto applies fig-scap to figures but ignores tbl-scap on tables.
-- This sets the short caption shown in the List of Tables from tbl-scap.
-- Run at post-render, after Quarto has rebuilt the table caption.
-- Quarto strips $ from attributes, so write K^2^VAE rather than K$^2$VAE.
function Table(tbl)
  local scap = tbl.attr.attributes["tbl-scap"]
  if scap == nil then
    return nil
  end
  tbl.caption.short = pandoc.read(scap, "markdown").blocks[1].content
  tbl.attr.attributes["tbl-scap"] = nil
  return tbl
end
