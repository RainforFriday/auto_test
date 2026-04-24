from markitdown import *

md = MarkItDown()
res = md.convert("./CSLR.pdf")
print(res.txt_content)