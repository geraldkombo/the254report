# THE 254 REPORT | Beehiiv GEO Setup Guide
> Paste these into beehiiv settings to push AI visibility from 51→68+

## 1. SITE SETTINGS > SEO (Set These Now)

| Field | Value |
|---|---|
| Meta Description | Independent Kenyan investigative journalism covering power, politics, technology, and human rights. The 254 Report publishes original reporting on custody deaths, governance, and the institutions that shape East Africa's largest economy. |
| OG Title | The 254 Report — Independent Kenyan Journalism |
| OG Description | Original investigative journalism from Kenya. Covering custody deaths, governance, tech, and the institutions shaping East Africa's future. |

## 2. SITE SETTINGS > Custom Code (Paste in <head>)

### Organization + WebSite Schema (paste once)
```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "The 254 Report",
  "url": "https://www.the254report.co.ke",
  "logo": "https://media.beehiiv.com/cdn-cgi/image/fit=scale-down,format=auto,onerror=redirect,quality=80/uploads/asset/file/982c95a8-df30-4a16-875e-6b6e9b91b18c/_MGN9945__1___1_.JPG",
  "description": "Independent Kenyan investigative journalism covering power, politics, technology, and human rights.",
  "sameAs": [
    "https://x.com/the254report",
    "https://www.facebook.com/the254report",
    "https://www.threads.net/@the254report"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "editorial",
    "email": "info@the254report.co.ke"
  },
  "address": {
    "@type": "PostalAddress",
    "addressCountry": "KE"
  }
}
</script>
```

```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "The 254 Report",
  "url": "https://www.the254report.co.ke",
  "description": "Independent Kenyan investigative journalism covering power, politics, technology, and human rights.",
  "potentialAction": {
    "@type": "SearchAction",
    "target": {
      "@type": "EntryPoint",
      "urlTemplate": "https://www.the254report.co.ke/search?q={search_term_string}"
    },
    "query-input": "required name=search_term_string"
  }
}
</script>
```

## 3. ARTICLE CUSTOM HTML (Add Below Each Article Body)

### FAQPage + Article Schema (paste per-article, update fields)
```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "NewsArticle",
  "headline": "ARTICLE TITLE HERE",
  "datePublished": "2026-06-14T00:00:00+03:00",
  "dateModified": "2026-06-14T00:00:00+03:00",
  "author": {
    "@type": "Person",
    "name": "Gerald Kombo",
    "url": "https://www.the254report.co.ke/authors/gerald-kombo"
  },
  "publisher": {
    "@type": "Organization",
    "name": "The 254 Report",
    "url": "https://www.the254report.co.ke",
    "logo": {
      "@type": "ImageObject",
      "url": "https://media.beehiiv.com/cdn-cgi/image/fit=scale-down,format=auto,onerror=redirect,quality=80/uploads/asset/file/982c95a8-df30-4a16-875e-6b6e9b91b18c/_MGN9945__1___1_.JPG"
    }
  },
  "image": "FEATURED IMAGE URL HERE",
  "description": "META DESCRIPTION HERE",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "ARTICLE URL HERE"
  }
}
</script>
```

```json
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "QUESTION 1",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "ANSWER 1"
      }
    },
    {
      "@type": "Question",
      "name": "QUESTION 2",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "ANSWER 2"
      }
    }
  ]
}
</script>
```

## 4. REFERENCE FILES (For Scale/Max Upgrade)

When you upgrade from Free to Scale ($49/mo), upload these:

| File | Path | Purpose | GEO Points |
|---|---|---|---|
| `254-llms.txt` | `https://www.the254report.co.ke/llms.txt` | AI crawler content map | +7 |
| `254-ai-summary.json` | `https://www.the254report.co.ke/ai/summary.json` | AI site summary | +2 |
| `254-ai-faq.json` | `https://www.the254report.co.ke/ai/faq.json` | AI FAQ extraction | +2 |
| `254-ai-service.json` | `https://www.the254report.co.ke/ai/service.json` | AI service description | +2 |

Total gain from files: +13 points (would push 51 → 64 before other fixes)

## 5. ADDITIONAL BOOSTS

| Action | Points | How |
|---|---|---|
| Create About page post | +2 | `/about` page with brand mission, team, contact |
| Add LinkedIn page + sameAs | +1 | Create, then add URL to Organization schema |
| Add Wikipedia entry | +2 | Notability required — aim for citation from existing coverage |
| Fix image alt text on all articles | +2 | Per article — Gemini/Perplexity read through alt text |
| Add Author bio page | +1 | `/authors/gerald-kombo` with credentials and article list |
| Add HSTS security header | +1 | Via Cloudflare dashboard (Free plan) |
