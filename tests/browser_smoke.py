"""Exercise the built starter at a project subpath in Chromium."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import tempfile
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    screenshots = ROOT / "browser-checks"
    screenshots.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary:
        shutil.copytree(ROOT / "dist", Path(temporary) / "example-tool")
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=temporary))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1280, "height": 1000})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/example-tool/halifax-phone-prefixes/")
                page.wait_for_function("document.getElementById('query').value === 'Halifax'")
                page.locator("#query").fill("+1 (942) 945-4123")
                page.wait_for_function("document.getElementById('block').textContent.includes('942-945-4xxx')")
                page.goto(f"http://127.0.0.1:{server.server_port}/example-tool/")

                page.locator("#rows tr").first.wait_for()
                page.locator("#example").click()
                assert page.locator("#query").input_value() == "604-200"
                assert "New Westminster" in page.locator("#summary").inner_text()
                page.locator("#area").select_option("902")
                page.locator("#query").fill("Halifax")
                assert "Halifax" in page.locator("#rows").inner_text()
                page.locator("#rows button").first.click()
                page.get_by_role("button", name="Save prefix", exact=True).click()
                page.locator("#saved").check()
                assert page.locator("#rows tr").count()==1
                page.locator("#query").fill("zzzz_no_prefix")
                assert page.locator("#rows tr").count()==0
                page.locator("#query").fill("")
                page.locator("#saved").uncheck()
                page.screenshot(path=str(screenshots / "desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(screenshots / "mobile.png"), full_page=True)
                page.get_by_role("link", name="Look up Canadian IPv4 and IPv6 registrations").click()
                page.locator("#matches tr").first.wait_for()
                assert "137.82.0.0/16" in page.locator("#matches").inner_text()
                page.get_by_role("button", name="BCNET · IPv6").click()
                assert page.locator("#matches tr").count() == 3
                assert "2607:f8f0::/32" in page.locator("#matches").inner_text()
                page.locator("#query").fill("192.0.2.1")
                page.get_by_role("button", name="Look up", exact=True).click()
                assert "No matching CA registration" in page.locator("#matches").inner_text()
                assert page.get_by_role("link", name="Check observed BGP routing").get_attribute("href").endswith("q=192.0.2.1")
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                assert not errors, errors
                browser.close()
            print("Browser checks passed: project subpath, source data, filtering and mobile layout")
        finally:
            server.shutdown()


if __name__ == "__main__":
    main()
