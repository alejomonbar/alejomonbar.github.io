---
layout: page
permalink: /repositories/
title: repositories
description: Open source quantum computing projects and contributions.
nav: true
nav_order: 4
---

## GitHub Repositories

{% if site.data.repositories.github_repos %}
<div class="repositories d-flex flex-wrap flex-md-row flex-column justify-content-between align-items-center">
  {% for repo in site.data.repositories.github_repos %}
    {% include repository/repo.html repository=repo %}
  {% endfor %}
</div>
{% endif %}

<script>
  (function () {
    const nodes = Array.from(document.querySelectorAll('.repo-stars[data-repo]'));
    if (!nodes.length) return;

    function setText(node, stars) {
      const text = node.querySelector('.repo-stars-text');
      if (!text) return;
      if (typeof stars === 'number') {
        text.textContent = `★ ${stars}`;
      } else {
        text.textContent = '';
      }
    }

    // First, render any values already provided in YAML.
    for (const node of nodes) {
      const raw = node.getAttribute('data-stars');
      if (raw && !Number.isNaN(Number(raw))) {
        setText(node, Number(raw));
      }
    }

    // Then, fill missing values from the GitHub API.
    for (const node of nodes) {
      const already = node.querySelector('.repo-stars-text')?.textContent?.trim();
      if (already) continue;

      const repo = node.getAttribute('data-repo');
      if (!repo) continue;

      fetch(`https://api.github.com/repos/${repo}`, {
        headers: { 'Accept': 'application/vnd.github+json' }
      })
        .then((r) => (r.ok ? r.json() : null))
        .then((json) => {
          const stars = json && typeof json.stargazers_count === 'number' ? json.stargazers_count : null;
          if (typeof stars === 'number') setText(node, stars);
        })
        .catch(() => {
          // Silent fail: avoid breaking page rendering on rate limits / network errors.
        });
    }
  })();
</script>
