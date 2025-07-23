# llmauto

{% include navigation.html %}

Welcome to my project updates and blog!

## About llmauto

This is a repository for [brief description of your project].

## Latest Blog Posts

{% for post in site.posts limit:3 %}
- [{{ post.title }}]({{ post.url }}) - {{ post.date | date: "%B %d, %Y" }}
{% endfor %}

[View all posts →](/blog/)

## Features

- [List your main features here]
- [Feature 2]
- [Feature 3]

## Getting Started

[Add instructions on how to use your project]

---

*Last updated: {{ site.time | date: "%B %d, %Y" }}*
