# Assistant Knowledge Fetcher

## Project Overview

**Assistant Knowledge Fetcher** is an intelligent web crawling application designed to automate the process of extracting, processing, and packaging web content for use in Retrieval-Augmented Generation (RAG) systems and AI knowledge bases. The tool provides a seamless way to convert web documentation, articles, and multi-page content into a structured, citation-ready format.

### Purpose

This application addresses the challenge of efficiently collecting and preparing web content for AI assistants and knowledge management systems. It automates the tedious process of manually saving web pages while ensuring proper metadata capture, image localization, and content structure preservation.

---

## Key Features & Capabilities

### 🌐 Intelligent Web Crawling

- **Two Crawling Modes:**
  - **Same Path Only (Subdirectory)**: Restricts crawling to pages under the initial URL path, preventing scope creep
  - **Entire Domain**: Crawls all pages within the same domain, useful for comprehensive documentation sites

- **Smart Link Discovery**: Automatically identifies and queues all valid links on each page
- **Duplicate Prevention**: Built-in visited URL tracking prevents redundant processing
- **Fragment & Hash Handling**: Normalizes URLs by removing fragments for cleaner processing

### 🔐 Authentication Support

- **Interactive Browser Session**: Launches a visible browser window for manual authentication
- **User-Controlled Login**: Pauses crawl to allow user login before proceeding
- **Session Persistence**: Maintains authentication state throughout the entire crawl

### 🖼️ Image Processing & Localization

- **Optional Image Download**: Toggle image downloading on/off based on requirements
- **Automatic Image Localization**: 
  - Downloads all images from crawled pages
  - Stores images in a dedicated `/images` folder
  - Rewrites `<img src>` attributes to relative local paths
  - Handles edge cases (data URIs, missing alt text, etc.)

- **Progress Tracking**: Real-time feedback on image processing status

### 📦 Package Generation

- **Smart Package Naming**: 
  - Uses page title for meaningful package names
  - Falls back to domain name if title unavailable
  - Sanitizes names for filesystem compatibility

- **Zip Archive Creation**: 
  - Bundles all HTML files and images into a single `.zip` file
  - Automatic cleanup of temporary folders
  - Ready for distribution or upload to knowledge bases

### 🎯 RAG-Optimized Output

- **Metadata Injection**: Each HTML file includes:
  ```html
  <meta name="source_url" content="[original_url]">
  <meta name="page_title" content="[page_title]">
  ```
  
- **Citation-Ready Format**: Metadata enables AI systems to properly cite sources
- **Preserved Structure**: Maintains original HTML structure and styling

### 🎛️ Advanced Control Features

- **Real-Time Monitoring**:
  - Live log viewer with timestamped entries
  - Status indicators (⚙️ INFO, ✅ SUCCESS, ❌ ERROR, ⏳ WAIT)
  - Progress bar showing completion percentage
  - Dynamic statistics (Pages Processed | Pages Queued)

- **Graceful Stop Mechanism**:
  - Emergency stop button allows user to halt crawl at any time
  - Completes current page processing before stopping
  - Removes partial/incomplete files
  - Still generates package with successfully processed pages

### 🖥️ User Experience

- **Modern UI**: Built with CustomTkinter for a polished, dark-themed interface
- **Intuitive Layout**: Clear input fields, radio buttons, and checkboxes
- **Responsive Design**: Smart window positioning and sizing
- **Error Handling**: User-friendly error messages and validation

---

## Technical Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.8+ | Primary programming language |
| **Web Automation** | Playwright | Latest | Headless/headed browser control |
| **UI Framework** | CustomTkinter | Latest | Modern GUI interface |
| **HTTP Client** | Requests | Latest | Image downloading |
| **Standard Library** | tkinter, threading, shutil, os | Built-in | UI, concurrency, file operations |

### Architecture Components

#### 1. **GUI Layer** (CustomTkinter)
- Handles user input and display
- Manages UI state and element visibility
- Provides real-time feedback through logs and progress bars

#### 2. **Crawl Engine** (Threading + Playwright)
- Runs in separate thread to prevent UI blocking
- Manages browser lifecycle (launch, navigate, close)
- Implements BFS (Breadth-First Search) crawl strategy

#### 3. **Content Processor**
- HTML parsing and metadata injection
- Image discovery and path rewriting
- URL normalization and validation

#### 4. **Storage Manager**
- File system operations (create directories, save files)
- Zip archive generation
- Temporary folder cleanup

### Design Patterns

- **MVC-like Architecture**: Separation of UI, business logic, and data handling
- **Observer Pattern**: Real-time log updates and status changes
- **Producer-Consumer**: URL queue management for crawling
- **State Machine**: Crawl states (idle → login → crawling → packaging → complete)

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection

### Installation Steps

1. **Clone or Download the Project**
   ```bash
   cd /path/to/project
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirement.txt
   ```

3. **Install Playwright Browsers**
   ```bash
   playwright install chromium
   ```

### Packaging as Executable (Optional)

To create a standalone executable:

```bash
pyinstaller --onefile --windowed --add-data "path/to/customtkinter:customtkinter" main.py
```

---

## Usage Guide

### Basic Workflow

1. **Launch Application**
   ```bash
   python main.py
   ```

2. **Configure Crawl Settings**
   - Enter the starting URL (parent page)
   - Select destination folder using "Browse" button
   - Choose crawl mode (Same Path or Entire Domain)
   - Toggle image downloading if needed

3. **Start Crawl**
   - Click "Start Processing"
   - Browser window opens automatically
   - Complete any required authentication
   - Click "Ready" to begin crawl

4. **Monitor Progress**
   - Watch real-time log updates
   - Check progress bar and statistics
   - Use "STOP PROCESS" if needed

5. **Retrieve Package**
   - Zip file created in selected folder
   - Named after page title or domain
   - Contains all HTML files and images

### Example Use Cases

#### Documentation Scraping
```
URL: https://docs.example.com/guide/
Mode: Same Path Only
Images: Enabled
Result: Complete guide documentation with all sub-pages
```

#### Company Knowledge Base
```
URL: https://internal.company.com/kb/
Mode: Entire Domain
Images: Disabled
Result: All KB articles in text-only format
```

---

## Configuration Options

### Crawl Modes

| Mode | Behavior | Best For |
|------|----------|----------|
| **Same Path Only** | Crawls only pages starting with the initial URL path | Specific documentation sections, targeted content |
| **Entire Domain** | Crawls all pages within the same domain | Complete site mirrors, broad knowledge capture |

### Image Handling

- **Enabled**: Downloads and localizes all images (increases package size)
- **Disabled**: Preserves original image URLs (smaller package, requires internet)

---

## Technical Implementation Details

### URL Normalization

```python
# Removes fragments and trailing slashes
normalized = url.split("#")[0].rstrip("/")
```

### Link Discovery Algorithm

1. Query all `<a>` tags with `href` attribute
2. Filter out non-relevant links (javascript:, mailto:, tel:, #anchors)
3. Convert relative URLs to absolute using `urljoin()`
4. Apply crawl mode filter
5. Check against visited set and queue
6. Add to queue if new

### Image Localization Process

1. **Discovery**: Find all `<img>` tags on page
2. **Download**: Fetch image using `requests` library
3. **Storage**: Save to `/images/` with sanitized filename
4. **Rewrite**: Update `src` attribute using Playwright's `page.evaluate()`
5. **Error Handling**: Silent failure for missing/broken images

### Metadata Injection

```python
meta = f'<meta name="source_url" content="{url}">'
      f'<meta name="page_title" content="{title}">'
html = html.replace("</head>", f"{meta}</head>")
```

### Threading Architecture

- **Main Thread**: UI event loop (CustomTkinter)
- **Worker Thread**: Crawl engine (daemon thread)
- **Communication**: Thread-safe log updates via queue-like pattern

---

## Error Handling & Edge Cases

### Robust Error Management

- **Network Timeouts**: 30-second timeout per page with graceful failure
- **Invalid URLs**: Pre-validation before crawl start
- **Authentication Failures**: User-controlled retry via browser
- **Partial Files**: Automatic cleanup of incomplete downloads
- **Browser Crashes**: Exception handling with user notification

### Edge Cases Handled

- Pages with no title → Uses domain name for package
- Pages with no links → Processes single page successfully
- Duplicate images → Hash-based naming prevents conflicts
- Dynamic content → 2-second wait after navigation
- Login redirects → User confirms when ready

---

## Performance Characteristics

### Processing Speed

- **Average**: 2-5 pages per minute (depends on page complexity)
- **Image Processing**: +1-2 seconds per page with images enabled
- **Network**: Bottleneck is typically remote server response time

### Resource Usage

- **Memory**: ~200-500 MB (browser + Python runtime)
- **CPU**: Low (<10% on modern systems)
- **Disk I/O**: Sequential writes, minimal impact

### Scalability

- **Tested**: Successfully crawled sites with 100+ pages
- **Limitation**: Single-threaded crawl (one page at a time)
- **Optimization**: Could be parallelized for larger deployments

---

## Future Enhancement Opportunities

- [ ] Multi-threaded crawling for speed improvements
- [ ] Support for JavaScript-heavy SPAs (wait strategies)
- [ ] Markdown conversion option for plain-text knowledge bases
- [ ] Crawl depth limiting (max pages, max depth)
- [ ] Robots.txt compliance checking
- [ ] Resume functionality for interrupted crawls
- [ ] Incremental updates (re-crawl only changed pages)
- [ ] Cloud storage integration (S3, Azure Blob)

---

## Troubleshooting

### Common Issues

**Browser doesn't open:**
- Ensure Playwright browsers are installed: `playwright install chromium`

**Login confirmation panel doesn't appear:**
- Check if browser window is visible
- Verify URL is accessible

**Images not downloading:**
- Check network connectivity
- Verify image URLs are publicly accessible
- Try disabling ad blockers in browser

**Zip file not created:**
- Ensure write permissions in destination folder
- Check disk space availability

---

## License & Credits

### Dependencies

- **Playwright**: Apache 2.0 License
- **CustomTkinter**: MIT License
- **Requests**: Apache 2.0 License

### Author

Developed as an internal tool for AI knowledge base management.

---

## Technical Support

For issues or feature requests, please contact the development team or file an issue in the project repository.

---

**Version**: 1.0  
**Last Updated**: 2024  
**Python Version**: 3.8+
