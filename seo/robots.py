from django.http import HttpResponse

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/login/",
        "Disallow: /accounts/logout/",
        "Disallow: /accounts/register/",
        "Disallow: /appointments/emergency/",
        "",
        "Sitemap: https://www.bishanildental.com/sitemap.xml",
        "",
        "# Crawl delay",
        "Crawl-delay: 1",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
