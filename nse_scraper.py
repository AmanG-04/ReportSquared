from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
from datetime import datetime
import os

class NSEFinancialDownloader:
    def __init__(self, download_folder="nse_downloads"):
        """Initialize Selenium WebDriver with download preferences"""
        print("🔧 Setting up Brave browser with download folder...")
        
        # Create download folder
        self.download_folder = os.path.abspath(download_folder)
        os.makedirs(self.download_folder, exist_ok=True)
        
        chrome_options = Options()
        
        # Set Brave browser path
        brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        chrome_options.binary_location = brave_path
        
        # Set download preferences for Brave
        prefs = {
            "download.default_directory": self.download_folder,
            "download.prompt_for_download": False,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.downloads": 1,
            "safebrowsing.enabled": False,
            "download_restrictions": 0,
            "profile.default_content_setting_values.notifications": 2,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.popups": 0
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Disable all dialogs and prompts
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-prompt-on-exit")
        chrome_options.add_argument("--disable-download-protection")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")
        
        # Auto-accept downloads - suppress all dialogs
        chrome_options.add_argument("--disable-extensions")
        
        # Set to automatically download without asking
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        # Anti-detection settings - hide automation
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # More realistic user-agent
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Additional stealth arguments
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--disable-notifications')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            
            # Execute script to hide webdriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
            
            # Enable Chrome DevTools Protocol to handle downloads silently
            try:
                self.driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                    "behavior": "allow",
                    "downloadPath": self.download_folder
                })
            except:
                pass  # CDP may not be available in all versions
            
            print(f"✅ Brave browser initialized")
            print(f"📁 Downloads will be saved to: {self.download_folder}\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Make sure Brave is installed and ChromeDriver is available")
            print("   Download ChromeDriver from: https://chromedriver.chromium.org/")
            print("   Make sure ChromeDriver version matches your Brave version")
            raise
        
        self.wait = WebDriverWait(self.driver, 15)
    
    def get_nifty50_list(self):
        """Hardcoded Nifty 50 companies"""
        return [
            {'symbol': 'ADANIPORTS', 'company_name': 'Adani Ports and Special Economic Zone Ltd.'},
            {'symbol': 'APOLLOHOSP', 'company_name': 'Apollo Hospitals Enterprise Ltd.'},
            {'symbol': 'ASIANPAINT', 'company_name': 'Asian Paints Ltd.'},
            {'symbol': 'AXISBANK', 'company_name': 'Axis Bank Ltd.'},
            {'symbol': 'BAJAJ-AUTO', 'company_name': 'Bajaj Auto Ltd.'},
            {'symbol': 'BAJFINANCE', 'company_name': 'Bajaj Finance Ltd.'},
            {'symbol': 'BAJAJFINSV', 'company_name': 'Bajaj Finserv Ltd.'},
            {'symbol': 'BHARTIARTL', 'company_name': 'Bharti Airtel Ltd.'},
            {'symbol': 'BPCL', 'company_name': 'Bharat Petroleum Corporation Ltd.'},
            {'symbol': 'BRITANNIA', 'company_name': 'Britannia Industries Ltd.'},
            {'symbol': 'CIPLA', 'company_name': 'Cipla Ltd.'},
            {'symbol': 'COALINDIA', 'company_name': 'Coal India Ltd.'},
            {'symbol': 'DIVISLAB', 'company_name': 'Divi\'s Laboratories Ltd.'},
            {'symbol': 'DRREDDY', 'company_name': 'Dr. Reddy\'s Laboratories Ltd.'},
            {'symbol': 'EICHERMOT', 'company_name': 'Eicher Motors Ltd.'},
            {'symbol': 'GRASIM', 'company_name': 'Grasim Industries Ltd.'},
            {'symbol': 'HCLTECH', 'company_name': 'HCL Technologies Ltd.'},
            {'symbol': 'HDFCBANK', 'company_name': 'HDFC Bank Ltd.'},
            {'symbol': 'HDFCLIFE', 'company_name': 'HDFC Life Insurance Company Ltd.'},
            {'symbol': 'HEROMOTOCO', 'company_name': 'Hero MotoCorp Ltd.'},
            {'symbol': 'HINDALCO', 'company_name': 'Hindalco Industries Ltd.'},
            {'symbol': 'HINDUNILVR', 'company_name': 'Hindustan Unilever Ltd.'},
            {'symbol': 'ICICIBANK', 'company_name': 'ICICI Bank Ltd.'},
            {'symbol': 'INDUSINDBK', 'company_name': 'IndusInd Bank Ltd.'},
            {'symbol': 'INFY', 'company_name': 'Infosys Ltd.'},
            {'symbol': 'ITC', 'company_name': 'ITC Ltd.'},
            {'symbol': 'JSWSTEEL', 'company_name': 'JSW Steel Ltd.'},
            {'symbol': 'KOTAKBANK', 'company_name': 'Kotak Mahindra Bank Ltd.'},
            {'symbol': 'LT', 'company_name': 'Larsen & Toubro Ltd.'},
            {'symbol': 'M&M', 'company_name': 'Mahindra & Mahindra Ltd.'},
            {'symbol': 'MARUTI', 'company_name': 'Maruti Suzuki India Ltd.'},
            {'symbol': 'NESTLEIND', 'company_name': 'Nestle India Ltd.'},
            {'symbol': 'NTPC', 'company_name': 'NTPC Ltd.'},
            {'symbol': 'ONGC', 'company_name': 'Oil and Natural Gas Corporation Ltd.'},
            {'symbol': 'POWERGRID', 'company_name': 'Power Grid Corporation of India Ltd.'},
            {'symbol': 'RELIANCE', 'company_name': 'Reliance Industries Ltd.'},
            {'symbol': 'SBILIFE', 'company_name': 'SBI Life Insurance Company Ltd.'},
            {'symbol': 'SBIN', 'company_name': 'State Bank of India'},
            {'symbol': 'SUNPHARMA', 'company_name': 'Sun Pharmaceutical Industries Ltd.'},
            {'symbol': 'TATACONSUM', 'company_name': 'Tata Consumer Products Ltd.'},
            {'symbol': 'TATAMOTORS', 'company_name': 'Tata Motors Ltd.'},
            {'symbol': 'TATASTEEL', 'company_name': 'Tata Steel Ltd.'},
            {'symbol': 'TCS', 'company_name': 'Tata Consultancy Services Ltd.'},
            {'symbol': 'TECHM', 'company_name': 'Tech Mahindra Ltd.'},
            {'symbol': 'TITAN', 'company_name': 'Titan Company Ltd.'},
            {'symbol': 'ULTRACEMCO', 'company_name': 'UltraTech Cement Ltd.'},
            {'symbol': 'WIPRO', 'company_name': 'Wipro Ltd.'},
            {'symbol': 'ADANIENT', 'company_name': 'Adani Enterprises Ltd.'},
            {'symbol': 'LTIM', 'company_name': 'LTIMindtree Ltd.'},
            {'symbol': 'SHRIRAMFIN', 'company_name': 'Shriram Finance Ltd.'}
        ]
    
    def navigate_to_financial_results(self):
        """Navigate directly to NSE Financial Results page"""
        print("🌐 Opening NSE Corporate Integrated Filing page...")
        url = "https://www.nseindia.com/companies-listing/corporate-integrated-filing"
        self.driver.get(url)
        print("⏳ Waiting for page to load...")
        time.sleep(10)  # Longer wait for page load
        
        # Close any popups/modals
        try:
            close_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.close, .close-button, [aria-label='Close']")
            for btn in close_buttons:
                try:
                    btn.click()
                    time.sleep(1)
                except:
                    pass
        except:
            pass
        
        print("✅ Corporate Integrated Filing page loaded\n")
    
    def search_and_download(self, symbol, company_name):
        """Search for company, click top result, then download XBRL file"""
        try:
            print(f"🔍 Searching for {symbol}...", end=" ")
            
            # Find the "Company Name or Symbol" input box
            search_box = None
            try:
                # The input field next to "Company" label
                search_box = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Company']"))
                )
            except:
                try:
                    # Try finding any visible text input
                    inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                    for inp in inputs:
                        if inp.is_displayed():
                            search_box = inp
                            break
                except:
                    pass
            
            if not search_box:
                print("❌ Search box not found")
                return {
                    'symbol': symbol,
                    'company_name': company_name,
                    'status': 'Search box not found',
                    'file_type': 'N/A'
                }
            
            # Clear and enter stock symbol
            search_box.click()
            time.sleep(0.3)
            search_box.send_keys(Keys.CONTROL + 'a')  # Select all
            time.sleep(0.2)
            search_box.send_keys(Keys.BACKSPACE)  # Delete all
            time.sleep(0.5)
            
            # Type symbol slowly with delay between each character
            for char in symbol:
                search_box.send_keys(char)
                time.sleep(0.2)  # 200ms delay between each character for better detection
            
            print(f"✍️  Entered '{symbol}'...", end=" ")
            time.sleep(4)  # Longer wait for dropdown search results to appear
            
            # Wait for results to load
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
                )
            except:
                print("⏳ Waiting for results...")
                time.sleep(2)
            
            # Press down arrow to select from dropdown
            search_box.send_keys(Keys.DOWN)
            time.sleep(0.5)
            
            # Press Enter to search/select
            search_box.send_keys(Keys.RETURN)
            print(f"✅ Pressed Enter...", end=" ")
            time.sleep(4)  # Wait for page/results to load
            
            # Step 1: Find and CLICK the first/top result row
            try:
                first_row = None
                rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                
                for row in rows:
                    if row.is_displayed():
                        # Check if row has content (not empty)
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if cells and len(cells) > 0:
                            # Check if this row has actual company data
                            first_cell_text = cells[0].text.strip()
                            if first_cell_text:  # Not empty
                                first_row = row
                                break
                
                if not first_row:
                    print("❌ No results found")
                    # Clear search box for next attempt
                    search_box.clear()
                    time.sleep(0.5)
                    return {
                        'symbol': symbol,
                        'company_name': company_name,
                        'status': 'No results in table',
                        'file_type': 'N/A'
                    }
                
                # Click on the first row to open details/expand
                print(f"👆 Clicking top result...", end=" ")
                time.sleep(0.5)
                
                # Try clicking the company name link in first cell
                # try:
                #     company_link = first_row.find_element(By.CSS_SELECTOR, "td a")
                #     self.driver.execute_script("arguments[0].click();", company_link)
                # except:
                #     # If no link, just click the row
                #     self.driver.execute_script("arguments[0].click();", first_row)
                
                # time.sleep(3)  # Wait for row to expand or page to load
                # print(f"✅ Opened...", end=" ")
                
                # Step 2: Now find and click the XBRL icon/download link
                xbrl_link = None
                
                # Method 1: Look for XBRL icon in the expanded/clicked row
                try:
                    xbrl_link = first_row.find_element(By.XPATH, ".//a[.//img]")
                except:
                    pass
                
                # Method 2: Look anywhere on page for XBRL download after clicking
                if not xbrl_link:
                    try:
                        # Look for XBRL links that appeared after clicking
                        xbrl_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'XBRL') or contains(@href, '.zip') or .//img[contains(@alt, 'XBRL')]]")
                        if xbrl_links:
                            xbrl_link = xbrl_links[0]
                    except:
                        pass
                
                # Method 3: Look for link with document/download icon
                if not xbrl_link:
                    try:
                        all_links_in_row = first_row.find_elements(By.TAG_NAME, "a")
                        for link in all_links_in_row:
                            # Check if link has an image (icon)
                            imgs = link.find_elements(By.TAG_NAME, "img")
                            if imgs:
                                xbrl_link = link
                                break
                    except:
                        pass
                
                if xbrl_link:
                    # Click the XBRL icon directly without scrolling
                    self.driver.execute_script("arguments[0].click();", xbrl_link)
                    print(f"📥 Downloaded XBRL!")
                    time.sleep(2)  # Wait for download to complete
                    
                    # Re-find and clear search box for next search
                    try:
                        search_box_fresh = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Company']"))
                        )
                        search_box_fresh.click()
                        time.sleep(0.3)
                        search_box_fresh.send_keys(Keys.CONTROL + 'a')
                        time.sleep(0.2)
                        search_box_fresh.send_keys(Keys.BACKSPACE)
                        time.sleep(0.5)
                    except:
                        try:
                            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                            for inp in inputs:
                                if inp.is_displayed():
                                    inp.click()
                                    time.sleep(0.3)
                                    inp.send_keys(Keys.CONTROL + 'a')
                                    time.sleep(0.2)
                                    inp.send_keys(Keys.BACKSPACE)
                                    time.sleep(0.5)
                                    break
                        except:
                            pass
                    
                    return {
                        'symbol': symbol,
                        'company_name': company_name,
                        'status': 'Downloaded',
                        'file_type': 'XBRL',
                        'period': 'Latest Quarter'
                    }
                else:
                    print("❌ XBRL icon not found after clicking")
                    # Re-find and clear search box for next attempt
                    try:
                        search_box_fresh = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Company']"))
                        )
                        search_box_fresh.click()
                        time.sleep(0.3)
                        search_box_fresh.send_keys(Keys.CONTROL + 'a')
                        time.sleep(0.2)
                        search_box_fresh.send_keys(Keys.BACKSPACE)
                        time.sleep(0.5)
                    except:
                        try:
                            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                            for inp in inputs:
                                if inp.is_displayed():
                                    inp.click()
                                    time.sleep(0.3)
                                    inp.send_keys(Keys.CONTROL + 'a')
                                    time.sleep(0.2)
                                    inp.send_keys(Keys.BACKSPACE)
                                    time.sleep(0.5)
                                    break
                        except:
                            pass
                    
                    return {
                        'symbol': symbol,
                        'company_name': company_name,
                        'status': 'XBRL icon not found',
                        'file_type': 'N/A'
                    }
                    
            except Exception as e:
                print(f"❌ Error: {str(e)[:30]}")
                return {
                    'symbol': symbol,
                    'company_name': company_name,
                    'status': f'Error: {str(e)[:30]}',
                    'file_type': 'N/A'
                }
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:40]}")
            return {
                'symbol': symbol,
                'company_name': company_name,
                'status': f'Error: {str(e)[:30]}',
                'file_type': 'N/A'
            }
    
    def download_all(self):
        """Main download function"""
        print("\n" + "="*70)
        print("🚀 NSE NIFTY 50 FINANCIAL RESULTS DOWNLOADER")
        print("="*70 + "\n")
        
        # Navigate directly to financial results page
        self.navigate_to_financial_results()
        
        # Get company list
        companies = self.get_nifty50_list()
        print(f"📋 Will process {len(companies)} Nifty 50 companies\n")
        
        results = []
        successful = 0
        failed = 0
        
        print("📊 Starting downloads (entering stock names one by one)...")
        print("-" * 70 + "\n")
        
        for i, company in enumerate(companies, 1):
            print(f"\n[{i}/{len(companies)}] {company['company_name']}")
            print(f"            Symbol: {company['symbol']}")
            
            result = self.search_and_download(company['symbol'], company['company_name'])
            
            if result:
                results.append(result)
                if result['status'] == 'Downloaded':
                    successful += 1
                else:
                    failed += 1
            else:
                failed += 1
            
            # Delay between searches
            time.sleep(3)
        
        print("\n" + "-" * 70)
        print(f"📈 Summary: {successful} downloaded, {failed} failed")
        print("-" * 70 + "\n")
        
        return results
    
    def save_summary_csv(self, results, filename='download_summary.csv'):
        """Save download summary to CSV"""
        if not results:
            print("❌ No results to save")
            return None
        
        df = pd.DataFrame(results)
        csv_path = os.path.join(self.download_folder, filename)
        df.to_csv(csv_path, index=False)
        
        print(f"✅ Summary saved to: {csv_path}")
        print(f"📁 XBRL files location: {self.download_folder}")
        print(f"📊 Total records: {len(results)}\n")
        
        return csv_path
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")

# Main execution
if __name__ == "__main__":
    downloader = None
    try:
        # Initialize downloader
        downloader = NSEFinancialDownloader(download_folder="nse_downloads")
        
        # Download all financial results
        results = downloader.download_all()
        
        # Save summary
        if results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nifty50_download_summary_{timestamp}.csv"
            downloader.save_summary_csv(results, filename)
        
        print("="*70)
        print("🏁 DOWNLOAD PROCESS COMPLETED")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("\n💡 TROUBLESHOOTING:")
        print("   1. Make sure you're connected to internet")
        print("   2. Download EdgeDriver from: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        print("   3. Add it to your PATH or place in same folder as script")
        print("   4. Try running the script again")
        
    finally:
        if downloader:
            time.sleep(2)
            downloader.close()