import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

class DataIngestionEngine:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    def fetch_yc_directory(self) -> List[Dict[str, Any]]:
        signals = []
        url = "https://www.ycombinator.com/companies"
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.select('a[class*="_company_"]')
                for card in cards:
                    name_elem = card.select_one('span[class*="_companyName_"]')
                    desc_elem = card.select_one('span[class*="_tagline_"]')
                    batch_elem = card.select_one('span[class*="_pill_"]')
                    
                    if name_elem:
                        company_name = name_elem.text.strip()
                        href = card.get("href", "")
                        full_url = f"https://www.ycombinator.com{href}" if href.startswith("/") else href
                        batch = batch_elem.text.strip() if batch_elem else "YC Current"
                        desc = desc_elem.text.strip() if desc_elem else "No description available."
                        
                        signals.append({
                            "company_name": company_name,
                            "canonical_domain": "",
                            "batch_identifier": batch,
                            "program_type": "YC_MAIN",
                            "official_status": "CONFIRMED_OFFICIAL",
                            "source_platform": "YC Directory",
                            "source_url": full_url,
                            "description": desc,
                            "founder_info": "Confirmed in Official Directory"
                        })
        except Exception as e:
            print(f"[ERROR] Failed fetching YC Directory: {e}")
        return signals

    def fetch_speedrun_directory(self) -> List[Dict[str, Any]]:
        signals = []
        url = "https://speedrun.a16z.com/"
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for elem in soup.find_all(["div", "a"], class_=re.compile(r"company|cohort|card", re.I)):
                    text = elem.text.strip()
                    if "Speedrun" in text or "SR" in text:
                        lines = [line.strip() for line in text.split("\n") if line.strip()]
                        if lines:
                            c_name = lines[0]
                            signals.append({
                                "company_name": c_name,
                                "canonical_domain": "",
                                "batch_identifier": "Speedrun Current",
                                "program_type": "SPEEDRUN",
                                "official_status": "CONFIRMED_OFFICIAL",
                                "source_platform": "Speedrun Page",
                                "source_url": url,
                                "description": "Accelerated tech startup cohort member.",
                                "founder_info": "Confirmed Speedrun Cohort"
                            })
        except Exception as e:
            print(f"[ERROR] Failed fetching Speedrun Directory: {e}")
        return signals

    def fetch_x_early_signals(self) -> List[Dict[str, Any]]:
        signals = []
        mock_social_posts = [
            {
                "author_handle": "@beknabdik",
                "author_name": "Bek",
                "post_text": "Building @speko_ai (YC S26). OpenRouter for voice AI.",
                "post_url": "https://x.com/beknabdik/status/2061493360150601738",
                "company_name": "Speko AI",
                "company_url": "https://speko.ai",
                "batch": "YC S26"
            }
        ]
        
        for post in mock_social_posts:
            signals.append({
                "company_name": post["company_name"],
                "canonical_domain": post["company_url"],
                "batch_identifier": post["batch"],
                "program_type": "YC_MAIN",
                "official_status": "EARLY_FOUNDER_SIGNAL",
                "source_platform": "X",
                "source_url": post["post_url"],
                "description": post["post_text"],
                "founder_info": f"{post['author_name']} ({post['author_handle']})"
            })
        return signals

    def fetch_linkedin_early_signals(self) -> List[Dict[str, Any]]:
        signals = []
        return signals
