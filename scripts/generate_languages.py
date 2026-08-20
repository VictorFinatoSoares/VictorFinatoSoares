import os
import requests
from collections import defaultdict

USERNAME = "VictorFinatoSoares"
TOKEN = os.environ["SUMMARY_GITHUB_TOKEN"]

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

language_totals = defaultdict(int)

page = 1

while True:
    response = requests.get(
        "https://api.github.com/user/repos",
        headers=headers,
        params={
            "per_page": 100,
            "page": page,
            "affiliation": "owner"
        }
    )

    response.raise_for_status()
    repos = response.json()

    if not repos:
        break

    for repo in repos:
        if repo["fork"]:
            continue

        languages_url = repo["languages_url"]

        lang_response = requests.get(
            languages_url,
            headers=headers
        )

        lang_response.raise_for_status()

        for language, bytes_count in lang_response.json().items():
            language_totals[language] += bytes_count

    page += 1


total_bytes = sum(language_totals.values())

languages = sorted(
    language_totals.items(),
    key=lambda item: item[1],
    reverse=True
)

percentages = [
    (language, (bytes_count / total_bytes) * 100)
    for language, bytes_count in languages
]


WIDTH = 600
ROW_HEIGHT = 38
HEADER_HEIGHT = 75
BOTTOM_PADDING = 25

HEIGHT = HEADER_HEIGHT + len(percentages) * ROW_HEIGHT + BOTTOM_PADDING


def escape_svg(text):
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}"
>

<style>
    .background {{
        fill: #0d1117;
    }}

    .title {{
        fill: #58a6ff;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 22px;
        font-weight: 600;
    }}

    .language {{
        fill: #c9d1d9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 14px;
    }}

    .percentage {{
        fill: #8b949e;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 14px;
        text-anchor: end;
    }}

    .bar-bg {{
        fill: #21262d;
    }}

    .bar {{
        fill: #58a6ff;
    }}
</style>

<rect
class="background"
width="100%"
height="100%"
rx="6"
/>

<text
x="28"
y="38"
class="title"
>
Languages
</text>
"""


y = HEADER_HEIGHT

for language, percentage in percentages:

    bar_width = percentage * 3

    svg += f"""
<text
x="28"
y="{y}"
class="language"
>
{escape_svg(language)}
</text>

<text
x="570"
y="{y}"
class="percentage"
>
{percentage:.1f}%
</text>

<rect
x="180"
y="{y - 12}"
width="300"
height="8"
rx="4"
class="bar-bg"
/>

<rect
x="180"
y="{y - 12}"
width="{bar_width:.2f}"
height="8"
rx="4"
class="bar"
/>
"""

    y += ROW_HEIGHT


svg += "</svg>"


os.makedirs("generated", exist_ok=True)

with open(
    "generated/languages.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write(svg)


print("Language statistics generated successfully.")

for language, percentage in percentages:
    print(f"{language}: {percentage:.2f}%")
