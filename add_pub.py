import arxiv
import os
import requests
import sys

client = arxiv.Client()
search = arxiv.Search(id_list=[sys.argv[1]])
paper = next(client.results(search))
lastnames = [author.name.split()[-1] for author in paper.authors]
if len(lastnames) > 3:
    dir_authors = lastnames[:3] + ["etal"]
else:
    dir_authors = lastnames
year = paper.published.year
short_list = "-".join(dir_authors)
dirname    = os.path.join("content/publication", f"{year}-{short_list}")
os.makedirs(dirname, exist_ok=True)

# Fetch BibTeX
resp = requests.get(f"https://arxiv.org/bibtex/{paper.entry_id.split('/')[-1]}")
with open(os.path.join(dirname, "cite.bib"), "w") as f:
    f.write(resp.text)

# Build index.md
title       = paper.title
authors_md  = "\n  ".join(f"- {a.name}" for a in paper.authors)
date        = paper.published.strftime("%Y-%m-%d")
abstract    = paper.summary.replace("\n", " ")
if paper.journal_ref:
    publication, pub_type = paper.journal_ref, "2"
else:
    publication, pub_type = f"arXiv:{paper.entry_id.split('/')[-1]}", "3"

index_md = f"""---
title: {title}
subtitle: ''
summary: ''
authors:
  {authors_md}
tags:
categories: []
date: '{date}'
lastmod: '{date}T00:00:00-05:00'
featured: false
draft: false
projects: []
publishDate: '{date}T00:00:00.000000Z'
publication_types:
  - '{pub_type}'
abstract: "{abstract}"
publication: '{publication}'
url_pdf: https://arxiv.org/pdf/{paper.entry_id.split('/')[-1]}.pdf
---
"""
with open(os.path.join(dirname, "index.md"), "w") as f:
    f.write(index_md)
