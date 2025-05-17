# NOT DONE YET IT'S UNDER PROGRESS.
from flask import Flask, jsonify
import feedparser
from flask_cors import CORS  # Add CORS support for React frontend

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

RSS_FEEDS = {
    'Krebs on Security': 'https://krebsonsecurity.com/feed/',
    'The Hacker News': 'https://thehackernews.com/feeds/posts/default',
    'BleepingComputer': 'https://www.bleepingcomputer.com/feed/',
    'Dark Reading': 'https://www.darkreading.com/rss.xml',
    'Threatpost': 'https://threatpost.com/feed/',
    'SC Media': 'https://www.scmagazine.com/rss.xml',
    'SecurityWeek': 'https://www.securityweek.com/rss.xml',
    'Help Net Security': 'https://www.helpnetsecurity.com/feed/',
    'Malwarebytes Labs': 'https://blog.malwarebytes.com/feed/',
    'CSO Online': 'https://www.csoonline.com/index.rss',
    'National Vulnerability Database (NVD)': 'https://nvd.nist.gov/feeds',
    'CVE Details': 'https://www.cvedetails.com/rss-feed.php',
    'Exploit Database': 'https://www.exploit-db.com/rss.xml',
    'Packet Storm Security': 'https://packetstormsecurity.com/feeds/',
    'SANS Internet Storm Center': 'https://isc.sans.edu/rssfeed.xml',
    'FireEye Threat Research': 'https://www.mandiant.com/rss.xml',
    'Cisco Talos Blog': 'https://blog.talosintelligence.com/feeds/posts/default',
    'Rapid7 Blog': 'https://www.rapid7.com/blog/rss/',
    'CrowdStrike Blog': 'https://www.crowdstrike.com/blog/feed/',
    'PortSwigger Research': 'https://portswigger.net/blog/rss',
    'Nmap Blog': 'https://nmap.org/changelog.xml',
    'OWASP Blog': 'https://owasp.org/blog/rss.xml',
    'Metasploit Blog': 'https://blog.metasploit.com/feeds/posts/default',
    'Wired Security': 'https://www.wired.com/feed/category/security/latest/rss',
    'Ars Technica Security': 'https://feeds.arstechnica.com/arstechnica/security',
    'TechCrunch Security': 'https://techcrunch.com/tag/security/feed/'
}

@app.route('/')
def feeds():
    articles = []
    for source, feed_url in RSS_FEEDS.items():
        try:
            parsed_feed = feedparser.parse(feed_url)
            for entry in parsed_feed.entries:
                # Handle missing fields
                title = entry.get('title', 'No title available')
                summary = entry.get('summary', 'No summary available')
                link = entry.get('link', '#')

                articles.append({
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'source': source
                })
        except Exception as e:
            print(f"Error parsing feed {source}: {e}")
            continue

    return jsonify(articles)

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Run on port 5000