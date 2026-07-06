import arxiv
import os
import re
import requests
import sys


def strip_arxiv_version(arxiv_id):
    return re.sub(r"v\d+$", "", arxiv_id)


def format_doi_link(doi):
    return f"[DOI:{doi}](https://doi.org/{doi})"

client = arxiv.Client()
search = arxiv.Search(id_list=[sys.argv[1]])
paper = next(client.results(search))
arxiv_id = paper.entry_id.split("/")[-1]
arxiv_id_without_version = strip_arxiv_version(arxiv_id)
doi = (getattr(paper, "doi", None) or f"10.48550/arXiv.{arxiv_id_without_version}").strip()
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
resp = requests.get(f"https://arxiv.org/bibtex/{arxiv_id}")
with open(os.path.join(dirname, "cite.bib"), "w") as f:
    f.write(resp.text)

# Build index.md
title       = paper.title
authors_md  = "\n  ".join(f"- {a.name}" for a in paper.authors)
date        = paper.published.strftime("%Y-%m-%d")
abstract    = paper.summary.replace("\n", " ")
doi_link    = format_doi_link(doi)
if paper.journal_ref:
    publication, pub_type = f"{paper.journal_ref.rstrip('.')}. {doi_link}", "2"
else:
    publication, pub_type = f"arXiv:{arxiv_id} {doi_link}", "3"

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
url_pdf: https://arxiv.org/pdf/{arxiv_id}.pdf
---
"""
with open(os.path.join(dirname, "index.md"), "w") as f:
    f.write(index_md)
