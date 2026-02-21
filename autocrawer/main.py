import os, shutil, threading, time, requests, sys
from urllib.parse import urljoin, urlparse
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from playwright.sync_api import sync_playwright

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RAGIngestionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Assistant Knowledge Fetcher")
        
        # Determine screen size for smart window placement
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"550x800+50+50")
        
        self.visited = set()
        self.queue = []
        self.is_running = False
        self.should_stop = False
        self.login_confirmed = False
        self.current_file = None  # Track current file being saved

        # --- UI LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)  # Log view gets all extra space

        self.header = ctk.CTkLabel(self, text="Assistant Knowledge Fetcher", font=("Arial", 22, "bold"))
        self.header.grid(row=0, column=0, pady=(20, 15))
        
        
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Parent URL (e.g. https://example.com/page)", width=580, height=40)
        self.url_entry.grid(row=1, column=0, pady=8, padx=20)

        self.path_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.path_frame.grid(row=2, column=0, pady=8, padx=20, sticky="ew")
        self.path_entry = ctk.CTkEntry(self.path_frame, placeholder_text="Save to folder...", width=350)
        self.path_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.browse_btn = ctk.CTkButton(self.path_frame, text="Browse", width=100, command=self.browse)
        self.browse_btn.pack(side="left")

        # Add crawl mode selector
        self.mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frame.grid(row=3, column=0, pady=8, padx=20, sticky="ew")
        self.mode_label = ctk.CTkLabel(self.mode_frame, text="Crawl Mode:")
        self.mode_label.pack(side="left", padx=(0, 10))
        self.mode_var = tk.StringVar(value="subdirectory")
        self.mode_sub = ctk.CTkRadioButton(self.mode_frame, text="Same Path Only", variable=self.mode_var, value="subdirectory")
        self.mode_sub.pack(side="left", padx=5)
        self.mode_domain = ctk.CTkRadioButton(self.mode_frame, text="Entire Domain", variable=self.mode_var, value="domain")
        self.mode_domain.pack(side="left", padx=5)

        # Add image download toggle
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.grid(row=4, column=0, pady=8, padx=20, sticky="ew")
        self.images_var = tk.BooleanVar(value=True)
        self.images_check = ctk.CTkCheckBox(self.options_frame, text="Download & Localize Images", variable=self.images_var)
        self.images_check.pack(side="left", padx=10)

        # Stats frame (hidden initially)
        self.stats_frame = ctk.CTkFrame(self)
        self.lbl_stats = ctk.CTkLabel(self.stats_frame, text="Ready | Pages: 0 | Queued: 0", font=("Arial", 13))
        self.lbl_stats.pack(pady=8)

        # Progress bar (hidden initially)
        self.prog = ctk.CTkProgressBar(self)
        self.prog.set(0)

        # Log view - larger by default
        self.log_view = ctk.CTkTextbox(self, font=("Consolas", 11), height=400)
        self.log_view.grid(row=5, column=0, padx=20, pady=(10, 10), sticky="nsew")

        # Login confirmation panel (created but not added to grid initially)
        self.login_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", border_width=2, border_color="#1f6aa5")
        
        self.login_label = ctk.CTkLabel(self.login_frame, text="Complete login in browser, then click 'Ready' below", 
                                        font=("Arial", 13, "bold"), text_color="#e8e5e0")
        self.login_label.pack(pady=8)
        
        self.login_btn_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        self.login_btn_frame.pack(pady=(0, 8), padx=20)
        self.cancel_btn = ctk.CTkButton(self.login_btn_frame, text="Cancel", 
                                        command=self.cancel_login, fg_color="red", hover_color="darkred", width=100, height=60)
        self.cancel_btn.pack(side="left", padx=5)
        self.ready_btn = ctk.CTkButton(self.login_btn_frame, text="Ready", 
                                       command=self.confirm_login, fg_color="green", hover_color="darkgreen", width=180, height=60)
        self.ready_btn.pack(side="left", padx=5)
        

        # Button frame for start/stop
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.btn_frame.grid_columnconfigure(0, weight=1)
        
        self.start_btn = ctk.CTkButton(self.btn_frame, text="Start Processing", height=50, 
                                       font=("Arial", 14, "bold"), command=self.start_thread)
        self.start_btn.grid(row=0, column=0, sticky="ew")
        
        self.stop_btn = ctk.CTkButton(self.btn_frame, text="⏹ STOP PROCESS", height=50, 
                                      font=("Arial", 14, "bold"), command=self.stop_crawl,
                                      fg_color="red", hover_color="darkred")
        # Stop button not added to grid initially

    def browse(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder)

    def log(self, msg, status="INFO"):
        icon = {"INFO": "⚙️", "SUCCESS": "✅", "ERROR": "❌", "WAIT": "⏳"}.get(status, "⚙️")
        self.log_view.insert("end", f"[{time.strftime('%H:%M:%S')}] {icon} {msg}\n")
        self.log_view.see("end")

    def update_last_log(self, msg, status="INFO"):
        """Update the last line in the log instead of creating a new one"""
        icon = {"INFO": "⚙️", "SUCCESS": "✅", "ERROR": "❌", "WAIT": "⏳"}.get(status, "⚙️")
        # Delete the last line
        self.log_view.delete("end-2c linestart", "end-1c")
        # Insert updated line
        self.log_view.insert("end-1c", f"[{time.strftime('%H:%M:%S')}] {icon} {msg}\n")
        self.log_view.see("end")

    def confirm_login(self):
        self.login_confirmed = True
        self.login_frame.grid_forget()
        
        # Show stats and progress when crawl starts - insert between options and log
        self.stats_frame.grid(row=5, column=0, padx=20, pady=(5, 5), sticky="ew")
        self.prog.grid(row=6, column=0, padx=20, pady=(0, 8), sticky="ew")
        self.log_view.grid(row=7, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.btn_frame.grid(row=8, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        # Update grid weight for log view
        self.grid_rowconfigure(7, weight=1)
        
        self.log("Login confirmed - starting crawl", "SUCCESS")

    def cancel_login(self):
        self.should_stop = True
        self.login_frame.grid_forget()
        self.log_view.grid(row=5, column=0, padx=20, pady=(10, 10), sticky="nsew")
        self.btn_frame.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.log("Crawl cancelled by user", "ERROR")

    def stop_crawl(self):
        self.should_stop = True
        self.log("Stop requested - finishing current page...", "WAIT")
        self.stop_btn.configure(state="disabled")

    def start_thread(self):
        if not self.is_running:
            self.is_running = True
            self.should_stop = False
            self.login_confirmed = False
            self.start_btn.configure(state="disabled")
            threading.Thread(target=self.run_engine, daemon=True).start()

    def run_engine(self):
        base_url = self.url_entry.get().strip()
        save_path = self.path_entry.get().strip()
        crawl_mode = self.mode_var.get()
        download_images = self.images_var.get()
        
        if not base_url.startswith("http"): 
            messagebox.showerror("Error", "Enter a valid URL")
            self.is_running = False
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            return
        
        if not save_path:
            messagebox.showerror("Error", "Select a save folder")
            self.is_running = False
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            return

        # Parse base URL for domain/path comparison
        parsed_base = urlparse(base_url)
        base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
        base_path = parsed_base.path.rstrip('/')

        try:
            with sync_playwright() as p:
                # Position browser next to UI
                browser = p.chromium.launch(headless=False, args=["--window-position=600,50", "--window-size=1000,1000"])
                context = browser.new_context()
                page = context.new_page()
                
                self.log(f"Opening browser... Please login if required.")
                page.goto(base_url, wait_until="domcontentloaded", timeout=60000)
                
                # Show login confirmation panel - insert it between options and log
                self.login_frame.grid(row=5, column=0, padx=20, pady=(5, 8), sticky="ew")
                self.log_view.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="nsew")
                self.btn_frame.grid(row=7, column=0, padx=20, pady=(10, 20), sticky="ew")
                
                # Update grid weight
                self.grid_rowconfigure(6, weight=1)
                
                # Wait for user confirmation
                while not self.login_confirmed and not self.should_stop:
                    time.sleep(0.1)
                
                if self.should_stop:
                    browser.close()
                    # Reset UI
                    self.login_frame.grid_forget()
                    self.log_view.grid(row=5, column=0, padx=20, pady=(10, 10), sticky="nsew")
                    self.btn_frame.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")
                    self.grid_rowconfigure(5, weight=1)
                    self.is_running = False
                    self.start_btn.configure(state="normal")
                    return

                # Stats and progress already shown by confirm_login()
                
                # Replace start button with stop button
                self.start_btn.grid_forget()
                self.stop_btn.grid(row=0, column=0, sticky="ew")
                self.stop_btn.configure(state="normal")

                self.log("Starting crawl...", "WAIT")
                self.lbl_stats.configure(text="Initializing | Pages: 0 | Queued: 0")
                
                # Get current URL after user navigation and capture title for package name
                current_url = page.url.split("#")[0].rstrip("/")
                page_title = page.title() or ""
                
                # Create package name from title or domain
                if page_title:
                    # Clean title for filename (remove invalid chars)
                    package_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in page_title)
                    package_name = package_name.strip().replace(' ', '_')[:50]  # Limit length
                else:
                    # Use domain name if no title
                    package_name = urlparse(current_url).netloc.replace('.', '_')
                
                if not package_name:
                    package_name = "Knowledge_Package"
                
                self.log(f"Package name: {package_name}.zip", "INFO")
                
                # Use the same name for the folder
                dump_dir = os.path.join(save_path, package_name)
                img_dir = os.path.join(dump_dir, "images")
                if download_images:
                    os.makedirs(img_dir, exist_ok=True)
                else:
                    os.makedirs(dump_dir, exist_ok=True)
                
                self.queue = [current_url]
                self.visited = set()

                while self.queue and not self.should_stop:
                    url = self.queue.pop(0).split("#")[0].rstrip("/")
                    if url in self.visited: continue
                    
                    # Check if URL should be crawled based on mode
                    parsed_url = urlparse(url)
                    if crawl_mode == "subdirectory":
                        if not url.startswith(base_url.split("#")[0].rstrip("/")):
                            continue
                    else:  # domain mode
                        if f"{parsed_url.scheme}://{parsed_url.netloc}" != base_domain:
                            continue
                    
                    # Check stop flag before processing
                    if self.should_stop:
                        self.log(f"Skipping: {url.split('/')[-1] or urlparse(url).netloc}", "WAIT")
                        break
                    
                    self.visited.add(url)

                    try:
                        self.log(f"Processing: {url.split('/')[-1] or urlparse(url).netloc}")
                        
                        # Check stop flag before navigation
                        if self.should_stop:
                            self.visited.remove(url)  # Remove from visited since not processed
                            break
                        
                        page.goto(url, wait_until="networkidle", timeout=30000)
                        
                        # Check stop flag after navigation
                        if self.should_stop:
                            self.visited.remove(url)
                            break
                        
                        # Wait for dynamic content
                        time.sleep(2)
                        
                        # Check stop flag before link discovery
                        if self.should_stop:
                            self.visited.remove(url)
                            break
                        
                        # 1. Discover ALL links on the page FIRST (before image processing)
                        links = page.query_selector_all('a[href]')
                        new_links = 0
                        for a in links:
                            href = a.get_attribute("href")
                            if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                                full = urljoin(url, href).split("#")[0].rstrip("/")
                                
                                # Apply crawl mode filter
                                parsed_full = urlparse(full)
                                should_add = False
                                
                                if crawl_mode == "subdirectory":
                                    should_add = full.startswith(base_url.split("#")[0].rstrip("/"))
                                else:  # domain mode
                                    should_add = f"{parsed_full.scheme}://{parsed_full.netloc}" == base_domain
                                
                                if should_add and full not in self.visited and full not in self.queue:
                                    self.queue.append(full)
                                    new_links += 1
                        
                        if new_links > 0:
                            self.log(f"Found {new_links} new links", "INFO")
                        
                        # Update stats immediately after finding links
                        self.lbl_stats.configure(text=f"Crawling | Pages: {len(self.visited)} | Queued: {len(self.queue)}")
                        total = len(self.visited) + len(self.queue)
                        self.prog.set(len(self.visited) / total if total > 0 else 1)
                        
                        # Check stop flag before image processing
                        if self.should_stop:
                            self.visited.remove(url)
                            break
                        
                        # 2. Image Localization (only if enabled)
                        if download_images:
                            images = page.query_selector_all("img")
                            if len(images) > 0:
                                self.log(f"Processing {len(images)} images", "INFO")
                                processed_count = 0
                                for img in images:
                                    if self.should_stop:
                                        self.visited.remove(url)
                                        break
                                    
                                    src = img.get_attribute("src")
                                    if src and not src.startswith("data:"):
                                        abs_src = urljoin(url, src)
                                        img_name = os.path.basename(urlparse(abs_src).path) or f"asset_{hash(abs_src)}.png"
                                        img_path = os.path.join(img_dir, img_name)
                                        try:
                                            r = requests.get(abs_src, timeout=5)
                                            r.raise_for_status()
                                            with open(img_path, 'wb') as f: 
                                                f.write(r.content)
                                            page.evaluate(f'(img) => img.src = "images/{img_name}"', img)
                                            processed_count += 1
                                            # Update log with progress
                                            self.update_last_log(f"Processing {len(images)} images [{processed_count}/{len(images)}]", "INFO")
                                        except Exception as e:
                                            pass  # Silent fail for images
                            
                            if self.should_stop:
                                break

                        # 3. Metadata Injection (For RAG Citations)
                        html = page.content()
                        title = page.title() or "Untitled"
                        meta = f'<meta name="source_url" content="{url}"><meta name="page_title" content="{title}">'
                        html = html.replace("</head>", f"{meta}</head>") if "</head>" in html else meta + html

                        # 4. Save File
                        fname = urlparse(url).path.replace("/", "_").strip("_") or "index"
                        # Limit filename length
                        if len(fname) > 200:
                            fname = fname[:200]
                        
                        file_path = os.path.join(dump_dir, f"{fname}.html")
                        self.current_file = file_path  # Track current file
                        
                        # Check stop flag before saving
                        if self.should_stop:
                            self.visited.remove(url)
                            self.current_file = None
                            break
                        
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(html)
                        
                        self.current_file = None  # Clear after successful save

                        self.log(f"Saved {fname}.html", "SUCCESS")
                    except Exception as e:
                        self.log(f"Failed {url}: {str(e)}", "ERROR")
                        # Remove from visited if failed
                        if url in self.visited:
                            self.visited.remove(url)

                    # Update stats at end of each page
                    self.lbl_stats.configure(text=f"Crawling | Pages: {len(self.visited)} | Queued: {len(self.queue)}")
                    total = len(self.visited) + len(self.queue)
                    self.prog.set(len(self.visited) / total if total > 0 else 1)

                browser.close()
                
                # Delete partial file if stopped during save
                if self.should_stop and self.current_file and os.path.exists(self.current_file):
                    try:
                        os.remove(self.current_file)
                        self.log(f"Deleted partial file: {os.path.basename(self.current_file)}", "INFO")
                    except:
                        pass
                
                # Create zip package regardless of whether stopped or completed
                if len(self.visited) > 0:  # Only create zip if at least one page was saved
                    self.lbl_stats.configure(text=f"Packaging | Pages: {len(self.visited)} | Queued: 0")
                    self.log("Creating zip package...", "WAIT")
                    zip_path = os.path.join(save_path, package_name)
                    shutil.make_archive(zip_path, 'zip', dump_dir)
                    
                    # Remove the source folder after creating zip
                    try:
                        shutil.rmtree(dump_dir)
                        self.log(f"Cleaned up temporary folder", "INFO")
                    except Exception as e:
                        self.log(f"Failed to remove temp folder: {str(e)}", "ERROR")
                    
                    if self.should_stop:
                        self.lbl_stats.configure(text=f"Stopped | Pages: {len(self.visited)} | Queued: 0")
                        self.log(f"Crawl stopped. Processed {len(self.visited)} pages.", "SUCCESS")
                        messagebox.showinfo("Stopped", f"Crawl stopped.\nPackage Created: {package_name}.zip\nProcessed: {len(self.visited)} pages\nSkipped: {len(self.queue)} queued pages")
                    else:
                        self.lbl_stats.configure(text=f"Complete | Pages: {len(self.visited)} | Queued: 0")
                        self.log(f"Crawled {len(self.visited)} pages successfully!", "SUCCESS")
                        messagebox.showinfo("Done", f"Package Created: {package_name}.zip\nTotal Pages: {len(self.visited)}")
                else:
                    if self.should_stop:
                        self.lbl_stats.configure(text=f"Stopped | Pages: 0 | Queued: 0")
                        self.log("Crawl stopped. No pages were saved.", "WAIT")
                        messagebox.showinfo("Stopped", "Crawl stopped before any pages were saved.")
                
        except Exception as e:
            self.log(f"Fatal error: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            # Clean up partial file if exists
            if self.current_file and os.path.exists(self.current_file):
                try:
                    os.remove(self.current_file)
                except:
                    pass
            
            self.current_file = None
            
            # Restore UI to initial state
            self.stop_btn.grid_forget()
            self.start_btn.grid(row=0, column=0, sticky="ew")
            self.start_btn.configure(state="normal")
            
            # Hide stats and progress after completion
            self.stats_frame.grid_forget()
            self.prog.grid_forget()
            self.log_view.grid(row=5, column=0, padx=20, pady=(10, 10), sticky="nsew")
            self.btn_frame.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="ew")
            
            # Reset grid weight
            self.grid_rowconfigure(5, weight=1)
            
            # Reset stats
            self.lbl_stats.configure(text="Ready | Pages: 0 | Queued: 0")
            self.prog.set(0)
            
            self.is_running = False
            self.should_stop = False

if __name__ == "__main__":
    app = RAGIngestionApp()
    app.mainloop()