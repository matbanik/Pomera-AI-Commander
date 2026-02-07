# Data Extraction Tools

> Tools for extracting specific data patterns from text — emails, HTML content, regex patterns, URLs, and email headers.

---

## Data Extraction Tools Documentation

### Email Extraction Tool

**Category**: Data Extraction Tools  
**Availability**: Always Available  
**TextProcessor Method**: `extract_emails_advanced()`

#### Description

The Email Extraction Tool is an advanced email address extraction utility that identifies and extracts email addresses from any text content. It features sophisticated filtering options, duplicate handling, sorting capabilities, and domain-only extraction for comprehensive email data processing.

#### Key Features

- **Advanced Email Recognition**: Uses robust regex pattern for accurate email detection
- **Duplicate Handling**: Option to remove duplicate email addresses
- **Count Display**: Shows occurrence count for each email address
- **Alphabetical Sorting**: Sort extracted emails alphabetically
- **Domain-Only Mode**: Extract only domain names from email addresses
- **Flexible Output**: Customizable output format with various display options

#### Capabilities

##### Core Functionality
- **Email Pattern Recognition**: Detects email addresses using comprehensive regex pattern
- **Duplicate Management**: Remove or preserve duplicate email addresses
- **Occurrence Counting**: Track how many times each email appears
- **Domain Extraction**: Extract domain names only (e.g., "example.com" from "user@example.com")
- **Alphabetical Organization**: Sort results for better readability

##### Email Recognition Pattern
The tool uses the regex pattern: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`

This pattern recognizes:
- **Local Part**: Letters, numbers, dots, underscores, percent signs, plus signs, hyphens
- **Domain Part**: Letters, numbers, dots, hyphens
- **TLD**: At least 2 characters (supports international domains)

##### Input/Output Specifications
- **Input**: Any text content (emails, documents, web pages, logs, etc.)
- **Output**: List of extracted email addresses with optional counts and formatting
- **Performance**: Efficient processing for large text documents
- **Accuracy**: High precision email detection with minimal false positives

#### Configuration

##### Settings Panel Options
- **Omit Duplicates**: Remove duplicate email addresses from results
- **Hide Counts**: Hide occurrence count numbers in output
- **Sort Emails**: Sort extracted emails alphabetically
- **Only Domain**: Extract domain names only instead of full email addresses

##### Default Settings
```json
{
  "omit_duplicates": false,
  "hide_counts": true,
  "sort_emails": false,
  "only_domain": false
}
```

#### Usage Examples

##### Basic Email Extraction Example
**Input:**
```
Contact us at support@example.com or sales@example.com.
For technical issues, reach out to tech@example.com.
You can also email info@example.com for general inquiries.
```

**Configuration:**
- Omit duplicates: false
- Hide counts: true
- Sort emails: false
- Only domain: false

**Output:**
```
support@example.com
sales@example.com
tech@example.com
info@example.com
```

##### Duplicate Handling with Counts Example
**Input:**
```
Email john@company.com or mary@company.com.
For urgent matters, contact john@company.com immediately.
You can also reach mary@company.com during business hours.
Alternative contact: john@company.com
```

**Configuration:**
- Omit duplicates: false
- Hide counts: false
- Sort emails: false
- Only domain: false

**Output:**
```
john@company.com (3)
mary@company.com (2)
```

##### Sorted Unique Emails Example
**Input:**
```
Contact: zebra@test.com, alpha@test.com, beta@test.com
Also try: zebra@test.com, charlie@test.com, alpha@test.com
```

**Configuration:**
- Omit duplicates: true
- Hide counts: true
- Sort emails: true
- Only domain: false

**Output:**
```
alpha@test.com
beta@test.com
charlie@test.com
zebra@test.com
```

##### Domain-Only Extraction Example
**Input:**
```
We work with partners at user1@google.com, admin@microsoft.com,
support@apple.com, and contact@amazon.com.
```

**Configuration:**
- Omit duplicates: true
- Hide counts: true
- Sort emails: true
- Only domain: true

**Output:**
```
amazon.com
apple.com
google.com
microsoft.com
```

##### Complex Text Processing Example
**Input:**
```
From: sender@company.com
To: recipient1@client.com, recipient2@client.com
CC: manager@company.com, sender@company.com
BCC: archive@company.com

Please contact support@helpdesk.com for assistance.
Backup contact: support@helpdesk.com
```

**Configuration:**
- Omit duplicates: true
- Hide counts: false
- Sort emails: true
- Only domain: false

**Output:**
```
archive@company.com (1)
manager@company.com (1)
recipient1@client.com (1)
recipient2@client.com (1)
sender@company.com (1)
support@helpdesk.com (1)
```

#### Common Use Cases

1. **Contact List Building**: Extract contacts from documents, emails, or web content
2. **Data Mining**: Extract email addresses from large text datasets
3. **Lead Generation**: Find potential customer email addresses from various sources
4. **Email List Cleaning**: Process and deduplicate existing email lists
5. **Domain Analysis**: Analyze email domains for business intelligence
6. **Compliance Auditing**: Find email addresses in documents for privacy compliance
7. **Marketing Research**: Extract competitor or industry email addresses
8. **Log Analysis**: Extract email addresses from system logs or web logs

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def extract_emails_advanced(text, omit_duplicates, hide_counts, sort_emails, only_domain):
    """Advanced email extraction with options for deduplication, counting, sorting, and domain-only extraction."""
    # Extract all email addresses using improved regex pattern
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(pattern, text)
    
    if not emails:
        return "No email addresses found in the text."
    
    # Extract domains if only_domain is True
    if only_domain:
        emails = [email.split('@')[1] for email in emails]
    
    # Count occurrences
    from collections import Counter
    email_counts = Counter(emails)
    
    # Process based on options
    if omit_duplicates:
        unique_emails = list(email_counts.keys())
        if sort_emails:
            unique_emails.sort()
        
        if hide_counts:
            return '\n'.join(unique_emails)
        else:
            return '\n'.join([f"{email} (1)" for email in unique_emails])
    else:
        if sort_emails:
            emails.sort()
        
        if hide_counts:
            return '\n'.join(emails)
        else:
            result = []
            processed = set()
            for email in emails:
                if email not in processed:
                    result.append(f"{email} ({email_counts[email]})")
                    processed.add(email)
            
            if sort_emails:
                result.sort()
            
            return '\n'.join(result)
```

##### Algorithm Details
1. **Pattern Matching**: Uses regex to find all email addresses in text
2. **Domain Extraction**: Splits email at '@' symbol to get domain part
3. **Counting**: Uses Counter to track email occurrences
4. **Deduplication**: Removes duplicates while preserving order
5. **Sorting**: Alphabetical sorting of results
6. **Formatting**: Applies count display and formatting options

##### Dependencies
- **Required**: Python standard library (re, collections modules)
- **Optional**: None

##### Performance Considerations
- **Large Texts**: Efficient regex processing for large documents
- **Memory Usage**: Optimized for handling large email lists
- **Processing Speed**: Fast extraction and processing of email data

#### Best Practices

##### Recommended Usage
- **Data Validation**: Verify extracted emails are valid before use
- **Privacy Compliance**: Ensure compliance with data protection regulations
- **Duplicate Handling**: Use omit duplicates for clean contact lists
- **Domain Analysis**: Use domain-only mode for domain-based analysis

##### Performance Tips
- **Large Documents**: Tool handles large texts efficiently
- **Batch Processing**: Process multiple documents sequentially
- **Output Format**: Choose appropriate display options for your use case
- **Data Cleaning**: Combine with other tools for comprehensive data processing

##### Common Pitfalls
- **False Positives**: Some text patterns may be incorrectly identified as emails
- **International Domains**: Pattern supports international TLDs
- **Email Validation**: Extraction doesn't validate if emails are active/valid
- **Context Sensitivity**: Tool extracts all email-like patterns regardless of context

#### Error Handling

##### No Emails Found
**Input:**
```
This text contains no email addresses.
Only phone numbers: 555-123-4567
```

**Output:**
```
No email addresses found in the text.
```

##### Invalid Email Patterns
The tool is designed to minimize false positives, but may occasionally extract:
- Email-like patterns that aren't valid emails
- Formatted text that resembles email structure
- URLs or file paths with @ symbols

#### Data Privacy Considerations

- **Sensitive Data**: Be cautious when processing sensitive documents
- **GDPR Compliance**: Consider data protection regulations when extracting personal data
- **Data Storage**: Extracted emails may contain personal information
- **Usage Rights**: Ensure you have permission to extract and use email addresses

#### Integration with Other Tools

##### Workflow Examples
1. **Extract → Sort → Clean**:
   - Email Extraction Tool → Alphabetical Sorter → Find & Replace (for cleaning)

2. **Extract → Analyze → Export**:
   - Email Extraction Tool → Word Frequency Counter (for domain analysis)

3. **Extract → Deduplicate → Format**:
   - Email Extraction Tool (with omit duplicates) → Case Tool (for formatting)

#### Related Tools

- **Email Header Analyzer**: Analyze email headers for routing information
- **URL and Link Extractor**: Extract URLs and web links from text
- **Find & Replace Text**: Clean or modify extracted email data
- **Alphabetical Sorter**: Sort extracted emails alphabetically

#### See Also
- [Email Header Analyzer Documentation](#email-header-analyzer)
- [Data Extraction Tools Overview](#data-extraction-tools-5-tools)
- [Privacy and Compliance Guidelines](#data-privacy-considerations)###
 Email Header Analyzer

**Category**: Data Extraction Tools  
**Availability**: Always Available  
**TextProcessor Method**: `analyze_email_headers()`

#### Description

The Email Header Analyzer is a sophisticated email forensics tool that parses and analyzes raw email headers to extract comprehensive routing information, authentication results, delivery timing, and security assessments. It provides detailed insights into email delivery paths, server hops, authentication status, and potential security issues.

#### Key Features

- **Comprehensive Header Parsing**: Parses all standard email header fields
- **Routing Analysis**: Tracks email delivery path through server hops
- **Authentication Verification**: Analyzes SPF, DKIM, and DMARC authentication results
- **Delivery Timing**: Calculates delivery times and hop delays
- **Security Assessment**: Provides security status and recommendations
- **Spam Analysis**: Evaluates spam scores and filtering results
- **Clock Skew Detection**: Identifies timestamp inconsistencies between servers

#### Capabilities

##### Core Functionality
- **Header Parsing**: Intelligent parsing of multi-line email headers
- **Routing Reconstruction**: Maps complete email delivery path
- **Authentication Analysis**: Comprehensive email authentication verification
- **Timing Analysis**: Calculates delivery times and identifies delays
- **Security Evaluation**: Assesses email security and authenticity

##### Analyzed Header Fields

**Basic Information:**
- From, To, Subject, Date, Message-ID
- Delivered-To, Return-Path

**Routing Information:**
- Received headers (server hops)
- Server names and IP addresses
- Timestamps and delivery timing

**Authentication Results:**
- SPF (Sender Policy Framework)
- DKIM (DomainKeys Identified Mail)
- DMARC (Domain-based Message Authentication)

**Technical Details:**
- MIME-Version, Content-Type
- X-Spam-Status and spam scores
- Custom headers and extensions

##### Security Assessment Categories
- **SECURE**: All authentication checks passed
- **INSECURE**: One or more authentication failures
- **PARTIAL**: Mixed authentication results
- **UNKNOWN**: No authentication information found

#### Configuration

The Email Header Analyzer operates without configuration options - it automatically analyzes all available header information and provides a comprehensive report.

#### Usage Examples

##### Basic Email Header Analysis Example
**Input:**
```
Received: from mail.example.com (mail.example.com [192.168.1.100])
    by mx.recipient.com (Postfix) with ESMTP id 12345
    for <user@recipient.com>; Mon, 1 Jan 2024 12:00:00 +0000
From: sender@example.com
To: user@recipient.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000
Message-ID: <test@example.com>
Authentication-Results: mx.recipient.com;
    spf=pass smtp.mailfrom=example.com;
    dkim=pass header.d=example.com;
    dmarc=pass header.from=example.com
```

**Output:**
```
=== EMAIL HEADER ANALYSIS ===

--- Basic Information ---
From: sender@example.com
To: user@recipient.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000
Message-Id: <test@example.com>

--- Routing Information ---

--- Server Hops (1 total) ---
Hop 1: mail.example.com [192.168.1.100]
  Received: Mon, 1 Jan 2024 12:00:00 +0000

--- Authentication Results ---
SPF: PASS
DKIM: PASS
DMARC: PASS

--- Security Assessment ---
Authentication Status: SECURE (All checks passed)

--- Summary ---
Total Hops: 1
Authentication: All Passed
```

##### Complex Multi-Hop Analysis Example
**Input:**
```
Received: from mx2.recipient.com (mx2.recipient.com [10.0.0.2])
    by mail.recipient.com (Postfix) with ESMTP id 67890
    for <user@recipient.com>; Mon, 1 Jan 2024 12:00:05 +0000
Received: from relay.isp.com (relay.isp.com [203.0.113.50])
    by mx2.recipient.com (Postfix) with ESMTP id 54321
    for <user@recipient.com>; Mon, 1 Jan 2024 12:00:03 +0000
Received: from mail.sender.com (mail.sender.com [198.51.100.10])
    by relay.isp.com (Postfix) with ESMTP id 98765
    for <user@recipient.com>; Mon, 1 Jan 2024 12:00:01 +0000
From: sender@sender.com
To: user@recipient.com
Subject: Multi-hop Email
Authentication-Results: mx2.recipient.com;
    spf=pass smtp.mailfrom=sender.com;
    dkim=fail reason="signature verification failed";
    dmarc=fail policy.dmarc=quarantine
X-Spam-Status: No, score=2.1 required=5.0
```

**Output:**
```
=== EMAIL HEADER ANALYSIS ===

--- Basic Information ---
From: sender@sender.com
To: user@recipient.com
Subject: Multi-hop Email

--- Server Hops (3 total) ---
Hop 1: mx2.recipient.com [10.0.0.2]
  Received: Mon, 1 Jan 2024 12:00:05 +0000

Hop 2: relay.isp.com [203.0.113.50]
  Received: Mon, 1 Jan 2024 12:00:03 +0000
  Delay from previous: 2 seconds

Hop 3: mail.sender.com [198.51.100.10]
  Received: Mon, 1 Jan 2024 12:00:01 +0000
  Delay from previous: 2 seconds

--- Delivery Timeline ---
Total delivery time: 4 seconds
Average hop delay: 2 seconds

--- Authentication Results ---
SPF: PASS
DKIM: FAIL
DMARC: FAIL

--- Security Assessment ---
Authentication Status: INSECURE (Failed: DKIM, DMARC)
DMARC Policy: QUARANTINE

--- Technical Details ---
X-Spam-Status: No, score=2.1 required=5.0

--- Summary ---
Total Hops: 3
Total Delivery Time: 4 seconds
Spam Score: 2.1 (Not Spam)
Authentication: Mixed Results
```

##### Clock Skew Detection Example
**Input:**
```
Received: from server2.com (server2.com [192.168.1.2])
    by server3.com (Postfix) with ESMTP
    for <user@domain.com>; Mon, 1 Jan 2024 12:00:10 +0000
Received: from server1.com (server1.com [192.168.1.1])
    by server2.com (Postfix) with ESMTP
    for <user@domain.com>; Mon, 1 Jan 2024 12:00:15 +0000
```

**Output:**
```
--- Server Hops (2 total) ---
Hop 1: server2.com [192.168.1.2]
  Received: Mon, 1 Jan 2024 12:00:10 +0000

Hop 2: server1.com [192.168.1.1]
  Received: Mon, 1 Jan 2024 12:00:15 +0000
  WARNING: Clock skew detected (5 seconds)
```

#### Common Use Cases

1. **Email Forensics**: Investigate suspicious or fraudulent emails
2. **Delivery Troubleshooting**: Diagnose email delivery issues and delays
3. **Security Analysis**: Assess email authentication and security status
4. **Spam Investigation**: Analyze spam filtering and scoring results
5. **Compliance Auditing**: Verify email security compliance
6. **Network Diagnostics**: Identify routing issues and server problems
7. **Authentication Debugging**: Troubleshoot SPF, DKIM, and DMARC setup
8. **Performance Analysis**: Measure email delivery performance

#### Technical Implementation

##### Header Parsing Algorithm
```python
@staticmethod
def analyze_email_headers(text):
    """Analyzes raw email headers to extract routing information, authentication results, and delivery timing."""
    # Parse multi-line headers with continuation support
    headers = {}
    current_header = None
    current_value = ""
    
    for line in lines:
        if line.startswith(' ') or line.startswith('\t'):
            # Continuation of previous header
            if current_header:
                current_value += " " + line.strip()
        else:
            # Save previous header and start new one
            if current_header:
                if current_header not in headers:
                    headers[current_header] = []
                headers[current_header].append(current_value.strip())
            
            if ':' in line:
                current_header, current_value = line.split(':', 1)
                current_header = current_header.strip().lower()
                current_value = current_value.strip()
```

##### Authentication Analysis
The tool analyzes authentication results using regex patterns:
- **SPF**: `r'spf=([^;]+)'` - Sender Policy Framework results
- **DKIM**: `r'dkim=([^;]+)'` - DomainKeys Identified Mail results  
- **DMARC**: `r'dmarc=([^;]+)'` - Domain-based Message Authentication results

##### Timing Calculations
- **Hop Delays**: Calculates time differences between consecutive hops
- **Total Delivery Time**: Measures end-to-end delivery duration
- **Clock Skew Detection**: Identifies negative time differences indicating server clock issues

##### Dependencies
- **Required**: Python standard library (re, datetime modules)
- **Email Utils**: Uses `email.utils.parsedate_to_datetime` for timestamp parsing
- **Optional**: None

#### Analysis Sections

##### 1. Basic Information
- Standard email headers (From, To, Subject, Date, Message-ID)
- Essential routing information (Delivered-To, Return-Path)

##### 2. Routing Information  
- Complete server hop analysis
- Server names and IP addresses
- Timestamp tracking and delay calculations

##### 3. Authentication Results
- SPF, DKIM, and DMARC verification status
- Security assessment and recommendations
- DMARC policy information

##### 4. Technical Details
- MIME version and content type information
- Spam scoring and filtering results
- Custom headers and extensions

##### 5. Summary
- Key metrics and overall assessment
- Quick reference for important findings

#### Best Practices

##### Recommended Usage
- **Complete Headers**: Provide full email headers for comprehensive analysis
- **Raw Format**: Use raw header format without modifications
- **Security Focus**: Pay attention to authentication results for security assessment
- **Timing Analysis**: Use delivery timing to identify performance issues

##### Interpretation Guidelines
- **Authentication Status**: SECURE emails have passed all authentication checks
- **Delivery Timing**: Unusual delays may indicate server or network issues
- **Spam Scores**: Scores above 5.0 typically indicate spam
- **Clock Skew**: Negative delays suggest server synchronization issues

##### Common Pitfalls
- **Incomplete Headers**: Partial headers limit analysis capabilities
- **Modified Headers**: Edited headers may produce inaccurate results
- **Timezone Issues**: Be aware of timezone differences in timestamps
- **Header Formatting**: Malformed headers may not parse correctly

#### Security Implications

##### Authentication Assessment
- **SPF PASS**: Sender IP is authorized by domain
- **DKIM PASS**: Email signature is valid and verified
- **DMARC PASS**: Email passes domain authentication policy
- **Failed Authentication**: May indicate spoofing or misconfiguration

##### Red Flags
- Multiple authentication failures
- Unusual routing paths
- Excessive delivery delays
- High spam scores
- Clock skew warnings

#### Error Handling

##### No Headers Found
**Input:**
```
This is just plain text without email headers.
```

**Output:**
```
No email headers found.
```

##### Malformed Headers
The tool gracefully handles malformed headers and continues analysis with available information.

#### Related Tools

- **Email Extraction Tool**: Extract email addresses from header analysis results
- **Find & Replace Text**: Clean or modify header data before analysis
- **Diff Viewer**: Compare headers from different emails
- **Word Frequency Counter**: Analyze header patterns and frequencies

#### See Also
- [Email Extraction Tool Documentation](#email-extraction-tool)
- [Email Security Best Practices](#security-implications)
- [Data Extraction Tools Overview](#data-extraction-tools-5-tools)### UR
L and Link Extractor

**Category**: Data Extraction Tools  
**Availability**: Always Available  
**TextProcessor Method**: `extract_urls()`

#### Description

The URL and Link Extractor is a versatile link extraction tool that identifies and extracts URLs and links from various text formats. It supports multiple extraction modes including HTML href attributes, HTTP/HTTPS URLs, any protocol URLs, and Markdown links, with advanced filtering capabilities for targeted extraction.

#### Key Features

- **Multiple Extraction Modes**: Support for different URL formats and contexts
- **Protocol Flexibility**: Extract HTTP/HTTPS or any protocol URLs
- **HTML Support**: Extract URLs from HTML href attributes
- **Markdown Support**: Extract URLs from Markdown link syntax
- **Text Filtering**: Filter results by specific text patterns
- **Automatic Deduplication**: Removes duplicate URLs from results
- **Sorted Output**: Alphabetically sorted results for better organization

#### Capabilities

##### Core Functionality
- **HTML href Extraction**: Extract URLs from HTML `href=""` attributes
- **HTTP/HTTPS URLs**: Extract standard web URLs with http:// or https:// protocols
- **Any Protocol URLs**: Extract URLs with any protocol (ftp://, mailto:, file://, etc.)
- **Markdown Links**: Extract URLs from Markdown `[text](url)` syntax
- **Text Filtering**: Filter extracted URLs by containing specific text
- **Comprehensive Mode**: Extract all URL types when no specific mode is selected

##### Extraction Patterns

**HTML href Pattern:**
- `href=["']([^"']+)["']` - Extracts URLs from href attributes

**HTTP/HTTPS Pattern:**
- `https?://[^\s<>"{}|\\^`\[\]]+` - Matches HTTP and HTTPS URLs

**Any Protocol Pattern:**
- `\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>"{}|\\^`\[\]]+` - Matches any valid protocol

**Markdown Pattern:**
- `\[([^\]]+)\]\(([^)]+)\)` - Extracts URLs from Markdown link syntax

##### Input/Output Specifications
- **Input**: Any text content (HTML, Markdown, plain text, documents)
- **Output**: Sorted list of unique URLs matching selected criteria
- **Performance**: Efficient regex-based extraction for large documents
- **Accuracy**: Comprehensive pattern matching with minimal false positives

#### Configuration

##### Settings Panel Options
- **href=""**: Extract URLs from HTML href attributes
- **http(s)://**: Extract HTTP and HTTPS URLs only
- **any protocol ://**: Extract URLs with any protocol scheme
- **markdown []()**: Extract URLs from Markdown link syntax
- **Filter**: Text filter to include only URLs containing specific text

##### Default Settings
```json
{
  "extract_href": false,
  "extract_https": false,
  "extract_any_protocol": false,
  "extract_markdown": false,
  "filter_text": ""
}
```

##### Extraction Behavior
- **No Options Selected**: Extracts all URL types (href, any protocol, markdown)
- **Multiple Options**: Combines results from all selected extraction modes
- **Filter Applied**: Only returns URLs containing the filter text (case-insensitive)

#### Usage Examples

##### HTML href Extraction Example
**Input:**
```html
<a href="https://example.com">Example</a>
<a href="https://google.com">Google</a>
<link rel="stylesheet" href="/styles.css">
<img src="image.jpg" alt="Image">
```

**Configuration:**
- href="": ✓ (checked)
- All other options: unchecked
- Filter: (empty)

**Output:**
```
/styles.css
https://example.com
https://google.com
```

##### HTTP/HTTPS URLs Only Example
**Input:**
```
Visit https://example.com for more info.
Download from ftp://files.example.com/data.zip
Email us at mailto:contact@example.com
Check out https://github.com/project
```

**Configuration:**
- http(s)://: ✓ (checked)
- All other options: unchecked
- Filter: (empty)

**Output:**
```
https://example.com
https://github.com/project
```

##### Any Protocol URLs Example
**Input:**
```
Web: https://example.com
FTP: ftp://files.example.com
Email: mailto:contact@example.com
File: file:///C:/documents/file.txt
SSH: ssh://user@server.com
```

**Configuration:**
- any protocol ://: ✓ (checked)
- All other options: unchecked
- Filter: (empty)

**Output:**
```
file:///C:/documents/file.txt
ftp://files.example.com
https://example.com
mailto:contact@example.com
ssh://user@server.com
```

##### Markdown Links Extraction Example
**Input:**
```markdown
Check out [Google](https://google.com) for search.
Visit [GitHub](https://github.com) for code repositories.
Read the [documentation](https://docs.example.com/guide).
Download [file](ftp://files.example.com/data.zip).
```

**Configuration:**
- markdown [](): ✓ (checked)
- All other options: unchecked
- Filter: (empty)

**Output:**
```
ftp://files.example.com/data.zip
https://docs.example.com/guide
https://github.com
https://google.com
```

##### Filtered Extraction Example
**Input:**
```
https://example.com/page1
https://google.com/search
https://example.com/page2
https://github.com/project
https://example.com/api
```

**Configuration:**
- http(s)://: ✓ (checked)
- All other options: unchecked
- Filter: `example.com`

**Output:**
```
https://example.com/api
https://example.com/page1
https://example.com/page2
```

##### Combined Extraction Modes Example
**Input:**
```html
<a href="https://example.com">Example</a>
Visit https://google.com directly.
Check [GitHub](https://github.com) for code.
FTP: ftp://files.example.com
```

**Configuration:**
- href="": ✓ (checked)
- http(s)://: ✓ (checked)
- markdown [](): ✓ (checked)
- Filter: (empty)

**Output:**
```
ftp://files.example.com
https://example.com
https://github.com
https://google.com
```

#### Common Use Cases

1. **Web Scraping**: Extract links from HTML pages or web content
2. **Document Processing**: Find URLs in documents, emails, or reports
3. **Link Validation**: Collect links for validation or testing
4. **Content Analysis**: Analyze link patterns in content
5. **Migration Tasks**: Extract links during content migration
6. **SEO Analysis**: Collect links for SEO auditing
7. **Research**: Gather URLs from research documents or articles
8. **Quality Assurance**: Find and verify links in documentation

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def extract_urls(text, extract_href=False, extract_https=False, extract_any_protocol=False, extract_markdown=False, filter_text=""):
    """Extracts URLs and links from text based on selected options."""
    urls = set()
    
    # Extract from HTML href attributes
    if extract_href:
        href_pattern = r'href=["\']([^"\']+)["\']'
        urls.update(re.findall(href_pattern, text))
    
    # Extract http(s):// URLs
    if extract_https:
        https_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls.update(re.findall(https_pattern, text))
    
    # Extract any protocol:// URLs
    if extract_any_protocol:
        protocol_pattern = r'\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>"{}|\\^`\[\]]+'
        urls.update(re.findall(protocol_pattern, text))
    
    # Extract markdown links [text](url)
    if extract_markdown:
        markdown_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        markdown_urls = re.findall(markdown_pattern, text)
        urls.update([url for _, url in markdown_urls])
    
    # If no options selected, extract all types
    if not any([extract_href, extract_https, extract_any_protocol, extract_markdown]):
        # Extract all types by default
        # ... (combines all patterns)
    
    # Apply filter if provided
    if filter_text.strip():
        filter_lower = filter_text.lower()
        urls = {url for url in urls if filter_lower in url.lower()}
    
    return '\n'.join(sorted(urls)) if urls else "No URLs found."
```

##### Algorithm Details
1. **Pattern Matching**: Uses regex patterns to identify different URL formats
2. **Set Collection**: Uses set to automatically handle deduplication
3. **Conditional Extraction**: Applies only selected extraction modes
4. **Default Behavior**: Extracts all types when no specific mode is selected
5. **Filtering**: Case-insensitive text filtering on results
6. **Sorting**: Alphabetical sorting for consistent output

##### Dependencies
- **Required**: Python standard library (re module)
- **Optional**: None

##### Performance Considerations
- **Large Documents**: Efficient regex processing for large text files
- **Memory Usage**: Set-based deduplication for memory efficiency
- **Processing Speed**: Optimized pattern matching for fast extraction

#### Best Practices

##### Recommended Usage
- **Specific Modes**: Select specific extraction modes for targeted results
- **Filter Usage**: Use filters to narrow results to relevant URLs
- **Content Type**: Choose appropriate modes based on input content type
- **Validation**: Validate extracted URLs before use in applications

##### Performance Tips
- **Mode Selection**: Use specific modes rather than default "all" for better performance
- **Filter Early**: Apply filters to reduce result set size
- **Large Files**: Tool handles large documents efficiently
- **Batch Processing**: Process multiple documents sequentially

##### Common Pitfalls
- **Relative URLs**: Tool extracts relative URLs from href attributes
- **Malformed URLs**: May extract malformed or incomplete URLs
- **Context Sensitivity**: Extracts all matching patterns regardless of context
- **Protocol Validation**: Doesn't validate if protocols are actually valid

#### Error Handling

##### No URLs Found
**Input:**
```
This text contains no URLs or links.
Just plain text content here.
```

**Output:**
```
No URLs found.
```

##### Invalid Patterns
The tool is designed to be permissive and may extract:
- Malformed URLs that match the pattern
- Relative paths from href attributes
- URLs with unusual but valid protocols

#### URL Types Supported

##### Standard Protocols
- **HTTP/HTTPS**: Web URLs
- **FTP/FTPS**: File transfer URLs
- **MAILTO**: Email addresses as URLs
- **FILE**: Local file system URLs
- **SSH/SFTP**: Secure shell and file transfer URLs

##### Special Cases
- **Relative URLs**: From href attributes (e.g., `/path/page.html`)
- **Fragment URLs**: URLs with hash fragments (e.g., `#section`)
- **Query Parameters**: URLs with query strings (e.g., `?param=value`)
- **Port Numbers**: URLs with specific ports (e.g., `:8080`)

#### Integration with Other Tools

##### Workflow Examples
1. **Extract → Validate → Process**:
   - URL and Link Extractor → URL Parser → Find & Replace (for cleaning)

2. **Extract → Filter → Analyze**:
   - URL and Link Extractor → Word Frequency Counter (for domain analysis)

3. **Extract → Sort → Export**:
   - URL and Link Extractor → Alphabetical Sorter → Case Tool (for formatting)

#### Related Tools

- **URL Parser**: Parse and analyze extracted URL components
- **Email Extraction Tool**: Extract email addresses from text
- **Find & Replace Text**: Clean or modify extracted URLs
- **Alphabetical Sorter**: Sort extracted URLs alphabetically

#### See Also
- [URL Parser Documentation](#url-parser)
- [Data Extraction Tools Overview](#data-extraction-tools-5-tools)
- [Web Scraping Best Practices](#common-use-cases)

### Regex Extractor

**Category**: Data Extraction Tools  
**Availability**: Always Available  
**TextProcessor Method**: `regex_extractor.RegexExtractor.process_text()`

#### Description

The Regex Extractor is a flexible pattern extraction utility that uses regular expressions to extract matches from text. It supports custom regex patterns with various matching modes, duplicate handling, sorting, and counting options. The tool can extract all occurrences or limit to first match per line, making it ideal for parsing structured text, logs, data files, and custom formats.

#### Key Features

- **Custom Regex Patterns**: Use any valid regular expression pattern
- **Match Modes**: First match per line or all occurrences
- **Duplicate Handling**: Option to remove duplicate matches
- **Match Counting**: Show occurrence counts for each match
- **Sorting**: Alphabetically sort extracted results
- **Case Sensitivity**: Toggle case-sensitive matching
- **Group Support**: Handles regex groups and captures tuples

#### Capabilities

##### Core Functionality
- **Pattern Matching**: Extract text using custom regex patterns
- **Line-by-Line Processing**: Option to process each line individually
- **Global Matching**: Option to match across entire text
- **Duplicate Management**: Remove or preserve duplicate matches
- **Occurrence Tracking**: Count how many times each match appears
- **Result Organization**: Sort results alphabetically
- **Group Handling**: Properly handles regex capture groups

##### Match Modes

**First Match Per Line:**
- Processes text line by line
- Extracts only the first match from each line
- Useful for structured data where each line has one key value
- Maintains line-by-line structure in output

**All Occurrences:**
- Processes entire text as one block
- Extracts all matches regardless of line boundaries
- Useful for finding all instances of a pattern
- More comprehensive extraction

##### Input/Output Specifications
- **Input**: Any text content (logs, documents, code, structured data, etc.)
- **Output**: List of extracted matches (one per line) with optional counts
- **Performance**: Efficient regex processing with compiled patterns
- **Error Handling**: Clear error messages for invalid regex patterns

#### Configuration

##### Settings Panel Options

**Find Field:**
- Enter your regex pattern in the "Find:" field
- Supports full regex syntax including groups, quantifiers, character classes, etc.
- Examples: `\d+`, `[A-Z][a-z]+`, `(\w+)@(\w+\.\w+)`, etc.

**Match Mode:**
- **First match per line**: Extract only the first match from each line
- **All occurrences**: Extract all matches from the entire text (default)

**Options:**
- **Omit duplicates**: Remove duplicate matches from results
- **Hide counts**: Don't show occurrence counts (default: enabled)
- **Sort results**: Sort extracted matches alphabetically
- **Case sensitive**: Perform case-sensitive pattern matching

##### Default Settings
```json
{
  "pattern": "",
  "match_mode": "all_per_line",
  "omit_duplicates": false,
  "hide_counts": true,
  "sort_results": false,
  "case_sensitive": false
}
```

#### Usage Examples

##### Extracting Numbers (All Occurrences)
**Input:**
```
Order #1234 was processed
Order #5678 was completed
Order #9012 is pending
```

**Configuration:**
- Find: `\d+`
- Match mode: All occurrences
- Options: (default)

**Output:**
```
1234
5678
9012
```

##### Extracting First Match Per Line
**Input:**
```
User: john.doe@example.com Password: secret123
User: jane.smith@test.com Password: pass456
User: bob@company.com Password: qwerty789
```

**Configuration:**
- Find: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}`
- Match mode: First match per line
- Options: Omit duplicates (unchecked), Hide counts

**Output:**
```
john.doe@example.com
jane.smith@test.com
bob@company.com
```

##### Extracting with Groups
**Input:**
```
2024-01-15 10:30:00 ERROR: Database connection failed
2024-01-15 11:45:00 INFO: User logged in successfully
2024-01-15 12:00:00 ERROR: Cache miss detected
```

**Configuration:**
- Find: `(\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}) (ERROR|INFO): (.+)`
- Match mode: First match per line
- Options: Hide counts

**Output:**
```
2024-01-15 | 10:30:00 | ERROR | Database connection failed
2024-01-15 | 11:45:00 | INFO | User logged in successfully
2024-01-15 | 12:00:00 | ERROR | Cache miss detected
```

##### Extracting with Duplicate Handling and Sorting
**Input:**
```
Product: Apple, Category: Fruit
Product: Banana, Category: Fruit
Product: Carrot, Category: Vegetable
Product: Apple, Category: Fruit
Product: Broccoli, Category: Vegetable
```

**Configuration:**
- Find: `Category: (\w+)`
- Match mode: First match per line
- Options: Omit duplicates ✓, Sort results ✓, Hide counts

**Output:**
```
Fruit
Vegetable
```

##### Case-Sensitive Matching Example
**Input:**
```
The Quick Brown Fox
the quick brown fox
THE QUICK BROWN FOX
```

**Configuration:**
- Find: `[A-Z][a-z]+`
- Match mode: All occurrences
- Options: Case sensitive ✓

**Output:**
```
Quick
Brown
Fox
```

#### Common Use Cases

1. **Log File Parsing**: Extract timestamps, error codes, or specific log entries
2. **Data Extraction**: Extract values from structured text or CSV-like data
3. **Email/URL Extraction**: Use custom patterns to extract contact information
4. **Code Analysis**: Extract function names, class names, or code patterns
5. **Format Conversion**: Extract data from one format to prepare for another
6. **Data Cleaning**: Extract valid data matching specific patterns
7. **Report Generation**: Extract key metrics or values from reports
8. **Text Mining**: Extract specific patterns from large text corpora

#### Technical Implementation

##### TextProcessor Method
```python
@staticmethod
def extract_matches(text, pattern, match_mode="all_per_line", omit_duplicates=False, 
                   hide_counts=True, sort_results=False, case_sensitive=False):
    """
    Extract matches from text using a regex pattern.
    
    Args:
        text: Input text to search
        pattern: Regex pattern to search for
        match_mode: "first_per_line" or "all_per_line"
        omit_duplicates: If True, only return unique matches
        hide_counts: If True, don't show match counts
        sort_results: If True, sort the results
        case_sensitive: If True, perform case-sensitive matching
    
    Returns:
        String containing extracted matches or error message
    """
    # Compile regex pattern
    flags = 0 if case_sensitive else re.IGNORECASE
    regex = re.compile(pattern, flags)
    
    processed_matches = []
    
    # Process based on match mode
    if match_mode == "first_per_line":
        # Process line by line
        for line in text.split('\n'):
            matches = regex.findall(line)
            if matches:
                processed_matches.append(process_match(matches[0]))
    else:
        # Process entire text
        matches = regex.findall(text)
        for match in matches:
            processed_matches.append(process_match(match))
    
    # Apply duplicate removal, sorting, and formatting
    # ...
```

##### Algorithm Details
1. **Pattern Compilation**: Compiles regex pattern once for efficiency
2. **Mode-Based Processing**: Different logic for line-by-line vs. global matching
3. **Match Processing**: Handles both simple matches and tuple results from groups
4. **Duplicate Handling**: Uses Counter for efficient duplicate tracking
5. **Formatting**: Applies sorting and count display based on options

##### Dependencies
- **Required**: Python standard library (re, collections.Counter modules)
- **Optional**: None

##### Performance Considerations
- **Pattern Compilation**: Regex patterns are compiled for efficient matching
- **Large Texts**: Handles large text files efficiently
- **Memory Usage**: Processes matches incrementally to minimize memory use
- **Line Processing**: First-per-line mode processes one line at a time

#### Best Practices

##### Recommended Usage
- **Test Patterns**: Test regex patterns in Find & Replace tool first
- **Match Mode Selection**: Use "first per line" for structured data, "all occurrences" for comprehensive extraction
- **Pattern Testing**: Validate regex patterns before processing large files
- **Group Usage**: Use capture groups to extract specific parts of matches
- **Duplicate Handling**: Use "omit duplicates" when you only need unique values

##### Performance Tips
- **Specific Patterns**: More specific patterns are faster than broad patterns
- **Line Mode**: Use "first per line" mode for better performance on structured data
- **Large Files**: Tool handles large files efficiently with compiled patterns
- **Simple Patterns**: Simpler patterns are faster than complex nested groups

##### Common Pitfalls
- **Invalid Regex**: Invalid regex patterns will show error messages
- **Greedy Matching**: Use `*?` or `+?` for non-greedy matching when needed
- **Line Boundaries**: "First per line" mode respects line boundaries
- **Group Tuples**: Patterns with groups return tuples joined with ` | `
- **Case Sensitivity**: Remember to set case sensitivity for case-dependent patterns

#### Error Handling

##### No Pattern Entered
**Output:**
```
Please enter a regex pattern in the Find field.
```

##### Invalid Regex Pattern
**Output:**
```
Regex Error: [error message]

Please check your regex pattern syntax.
```

##### No Matches Found
**Output:**
```
No matches found for the regex pattern.
```

#### Regex Pattern Tips

##### Common Patterns
- **Numbers**: `\d+` (one or more digits)
- **Words**: `\w+` (word characters)
- **Email**: `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}`
- **URL**: `https?://[^\s<>"]+`
- **IP Address**: `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`
- **Date**: `\d{4}-\d{2}-\d{2}` (YYYY-MM-DD format)

##### Capture Groups
- Use parentheses `()` to create capture groups
- Multiple groups return tuples: `(\w+)@(\w+\.\w+)` → `('user', 'domain.com')`
- Groups are joined with ` | ` in output

##### Special Characters
- **Escape Special**: Use `\` to escape special regex characters
- **Character Classes**: `[A-Za-z]` for letters, `[0-9]` for digits
- **Quantifiers**: `*` (zero or more), `+` (one or more), `?` (zero or one)
- **Anchors**: `^` (start), `$` (end), `\b` (word boundary)

#### Integration with Other Tools

##### Workflow Examples
1. **Extract → Sort → Format**:
   - Regex Extractor → Alphabetical Sorter → Case Tool

2. **Extract → Deduplicate → Count**:
   - Regex Extractor (with omit duplicates) → Word Frequency Counter

3. **Extract → Replace → Format**:
   - Regex Extractor → Find & Replace Text → Case Tool

4. **Extract → Validate → Process**:
   - Regex Extractor → URL Parser → Find & Replace (for cleaning)

#### Related Tools

- **Find & Replace Text**: Test regex patterns and perform replacements
- **Email Extraction Tool**: Extract emails using predefined patterns
- **URL and Link Extractor**: Extract URLs using predefined patterns
- **Alphabetical Sorter**: Sort extracted results
- **Word Frequency Counter**: Analyze frequency of extracted patterns

#### See Also
- [Find & Replace Text Documentation](#find--replace-text)
- [Email Extraction Tool Documentation](#email-extraction-tool)
- [URL and Link Extractor Documentation](#url-and-link-extractor)
- [Data Extraction Tools Overview](#data-extraction-tools-5-tools)
- [Regex Pattern Library](core/regex_pattern_library.py)

### HTML Extraction Tool

**Category**: Data Extraction Tools  
**Availability**: Always Available  
**TextProcessor Method**: `html_tool.HTMLExtractionTool.process_text()`

#### Description

The HTML Extraction Tool is a comprehensive HTML processing utility that extracts and processes HTML content in multiple ways. It can extract visible text as it would appear in a browser, clean HTML by removing unnecessary elements, or extract specific HTML components like links, images, headings, tables, and forms. The tool is designed to handle complex HTML structures while providing clean, formatted output.

#### Key Features

- **Multiple Extraction Methods**: Seven different extraction modes for various use cases
- **Visible Text Extraction**: Extract text as it would appear in a browser
- **HTML Cleaning**: Remove scripts, styles, and unnecessary attributes
- **Element-Specific Extraction**: Extract links, images, headings, tables, and forms
- **Smart Formatting**: Preserve document structure with proper line breaks and spacing
- **Attribute Filtering**: Configurable extraction of HTML attributes
- **Error Handling**: Robust error handling for malformed HTML

#### Capabilities

##### Core Functionality
- **Visible Text Extraction**: Converts HTML to readable text with proper formatting
- **HTML Cleaning**: Removes scripts, styles, comments, and unwanted attributes
- **Link Extraction**: Extracts all anchor tags with URLs and link text
- **Image Extraction**: Extracts image sources with alt text and titles
- **Heading Extraction**: Extracts H1-H6 headings with level indicators
- **Table Extraction**: Converts HTML tables to structured text format
- **Form Extraction**: Analyzes form structure and input fields

##### Extraction Methods

1. **Visible Text**: Extract text as it appears in a browser
2. **Clean HTML**: Remove unnecessary tags and attributes
3. **Extract Links**: Find all anchor tags and URLs
4. **Extract Images**: Find all image tags and attributes
5. **Extract Headings**: Find all heading tags (H1-H6)
6. **Extract Tables**: Convert tables to structured text
7. **Extract Forms**: Analyze form structure and fields

##### HTML Processing Features
- **Script/Style Removal**: Removes `<script>`, `<style>`, `<noscript>`, and `<meta>` tags
- **Block Element Handling**: Adds proper line breaks for block-level elements
- **List Processing**: Converts `<li>` elements to bullet points
- **Table Processing**: Converts table cells to tab-separated values
- **Entity Decoding**: Converts HTML entities to readable characters
- **Whitespace Cleanup**: Removes excessive whitespace and empty lines

##### Input/Output Specifications
- **Input**: Any HTML content (web pages, HTML fragments, documents)
- **Output**: Formatted text, cleaned HTML, or extracted data based on method
- **Performance**: Efficient processing for large HTML documents
- **Encoding**: Full UTF-8 support with proper character handling

#### Configuration

##### Settings Panel Options

**Extraction Method Dropdown:**
- **Extract Visible Text**: Convert HTML to readable text
- **Clean HTML**: Remove unnecessary elements
- **Extract Links**: Find all links and URLs
- **Extract Images**: Find all images and attributes
- **Extract Headings**: Find all heading elements
- **Extract Tables**: Convert tables to text
- **Extract Forms**: Analyze form structure

**Method-Specific Settings:**

**Visible Text Options:**
- **Add link references**: Include footnote-style link references

**Clean HTML Options:**
- **Remove script and style tags**: Remove `<script>` and `<style>` elements
- **Remove HTML comments**: Remove `<!-- -->` comments
- **Remove style attributes**: Remove `style=""` attributes
- **Remove class attributes**: Remove `class=""` attributes
- **Remove ID attributes**: Remove `id=""` attributes
- **Remove empty tags**: Remove tags with no content

**Link Extraction Options:**
- **Include link text**: Show anchor text with URLs
- **Only absolute links**: Filter to http/https URLs only

**Image Extraction Options:**
- **Include alt text**: Show image alt attributes
- **Include title**: Show image title attributes

**Heading Extraction Options:**
- **Include heading level**: Show H1, H2, etc. indicators

**Table Extraction Options:**
- **Column separator**: Character to separate table columns (default: tab)

##### Default Settings
```json
{
  "extraction_method": "visible_text",
  "preserve_links": false,
  "remove_scripts": true,
  "remove_comments": true,
  "remove_style_attrs": true,
  "remove_class_attrs": false,
  "remove_id_attrs": false,
  "remove_empty_tags": true,
  "include_link_text": true,
  "absolute_links_only": false,
  "include_alt_text": true,
  "include_title": false,
  "include_heading_level": true,
  "column_separator": "\t"
}
```

#### Usage Examples

##### Visible Text Extraction Example
**Input:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Sample Page</title>
    <style>body { font-family: Arial; }</style>
</head>
<body>
    <h1>Welcome to Our Site</h1>
    <p>This is a <strong>sample</strong> paragraph with <a href="https://example.com">a link</a>.</p>
    <ul>
        <li>First item</li>
        <li>Second item</li>
    </ul>
    <script>console.log('hidden');</script>
</body>
</html>
```

**Configuration:**
- Extraction Method: Extract Visible Text
- Add link references: false

**Output:**
```
Welcome to Our Site

This is a sample paragraph with a link.

• First item
• Second item
```

##### Link Extraction Example
**Input:**
```html
<div>
    <p>Visit our <a href="https://example.com">main site</a> or check out our 
    <a href="/blog">blog</a> and <a href="mailto:contact@example.com">contact us</a>.</p>
    <footer>
        <a href="https://facebook.com/example">Facebook</a> |
        <a href="https://twitter.com/example">Twitter</a>
    </footer>
</div>
```

**Configuration:**
- Extraction Method: Extract Links
- Include link text: true
- Only absolute links: false

**Output:**
```
main site: https://example.com
blog: /blog
contact us: mailto:contact@example.com
Facebook: https://facebook.com/example
Twitter: https://twitter.com/example
```

##### Image Extraction Example
**Input:**
```html
<div class="gallery">
    <img src="photo1.jpg" alt="Beautiful sunset" title="Sunset at the beach">
    <img src="photo2.jpg" alt="Mountain view">
    <img src="photo3.jpg" title="City skyline">
    <img src="photo4.jpg">
</div>
```

**Configuration:**
- Extraction Method: Extract Images
- Include alt text: true
- Include title: true

**Output:**
```
photo1.jpg | Alt: Beautiful sunset | Title: Sunset at the beach
photo2.jpg | Alt: Mountain view
photo3.jpg | Title: City skyline
photo4.jpg
```

##### Heading Extraction Example
**Input:**
```html
<article>
    <h1>Main Article Title</h1>
    <h2>Introduction</h2>
    <p>Some content...</p>
    <h2>Main Content</h2>
    <h3>Subsection A</h3>
    <p>More content...</p>
    <h3>Subsection B</h3>
    <h2>Conclusion</h2>
</article>
```

**Configuration:**
- Extraction Method: Extract Headings
- Include heading level: true

**Output:**
```
H1: Main Article Title
H2: Introduction
H2: Main Content
H3: Subsection A
H3: Subsection B
H2: Conclusion
```

##### Table Extraction Example
**Input:**
```html
<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>City</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>John Doe</td>
            <td>30</td>
            <td>New York</td>
        </tr>
        <tr>
            <td>Jane Smith</td>
            <td>25</td>
            <td>Los Angeles</td>
        </tr>
    </tbody>
</table>
```

**Configuration:**
- Extraction Method: Extract Tables
- Column separator: "\t" (tab)

**Output:**
```
Name	Age	City
John Doe	30	New York
Jane Smith	25	Los Angeles
```

##### Form Extraction Example
**Input:**
```html
<form action="/submit" method="post">
    <input type="text" name="username" placeholder="Username">
    <input type="password" name="password">
    <input type="email" name="email">
    <textarea name="comments"></textarea>
    <select name="country">
        <option>USA</option>
        <option>Canada</option>
    </select>
    <input type="submit" value="Submit">
</form>
```

**Configuration:**
- Extraction Method: Extract Forms

**Output:**
```
--- Form 1 ---
Action: /submit
Method: post
Input Fields:
  - username (text)
  - password (password)
  - email (email)
  - unnamed (submit)
Textarea Fields:
  - comments
Select Fields:
  - country
```

##### HTML Cleaning Example
**Input:**
```html
<div class="container" style="margin: 10px;" id="main">
    <p style="color: red;">This is a paragraph.</p>
    <!-- This is a comment -->
    <script>alert('popup');</script>
    <span></span>
    <strong>Bold text</strong>
</div>
```

**Configuration:**
- Extraction Method: Clean HTML
- Remove script and style tags: true
- Remove HTML comments: true
- Remove style attributes: true
- Remove class attributes: false
- Remove ID attributes: false
- Remove empty tags: true

**Output:**
```html
<div class="container" id="main">
    <p>This is a paragraph.</p>
    <strong>Bold text</strong>
</div>
```

#### Common Use Cases

1. **Web Scraping**: Extract readable content from web pages
2. **Content Migration**: Convert HTML content to plain text for migration
3. **Data Analysis**: Extract specific elements for analysis
4. **Content Cleaning**: Remove unwanted HTML elements and attributes
5. **Link Harvesting**: Extract all links from web pages or documents
6. **Image Cataloging**: Create inventories of images with metadata
7. **Document Structure Analysis**: Analyze heading structure and hierarchy
8. **Form Analysis**: Understand form structure for automation
9. **Table Data Extraction**: Convert HTML tables to structured data
10. **SEO Analysis**: Extract headings and content structure

#### Technical Implementation

##### HTMLExtractionTool Class
```python
class HTMLExtractionTool:
    """HTML Extraction Tool for processing HTML content."""
    
    def process_text(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Process HTML content based on the selected extraction method."""
        
    def extract_visible_text(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract visible text from HTML as it would appear in a browser."""
        
    def clean_html(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Clean HTML by removing unnecessary tags and attributes."""
        
    def extract_links(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract all links from HTML content."""
        
    def extract_images(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract all images from HTML content."""
        
    def extract_headings(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract all headings from HTML content."""
        
    def extract_tables(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract table data from HTML content."""
        
    def extract_forms(self, html_content: str, settings: Dict[str, Any]) -> str:
        """Extract form information from HTML content."""
```

##### Tag Processing
- **Script/Style Tags**: `['script', 'style', 'noscript', 'meta', 'head', 'title']`
- **Block Tags**: `['div', 'p', 'br', 'hr', 'h1-h6', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'th']`
- **Inline Tags**: `['span', 'a', 'strong', 'b', 'em', 'i', 'u', 'code', 'kbd']`

##### Performance Considerations
- **Memory Efficient**: Processes HTML in chunks for large documents
- **Regex Optimization**: Uses compiled regex patterns for better performance
- **Error Recovery**: Graceful handling of malformed HTML
- **UTF-8 Support**: Full Unicode character support

#### Integration with Other Tools

##### Workflow Examples
1. **Extract → Clean → Analyze**:
   - HTML Extraction Tool (visible text) → Word Frequency Counter → Analysis

2. **Extract → Parse → Process**:
   - HTML Extraction Tool (links) → URL Parser → Find & Replace

3. **Extract → Sort → Export**:
   - HTML Extraction Tool (headings) → Alphabetical Sorter → Case Tool

#### Related Tools

- **URL and Link Extractor**: Alternative URL extraction from text
- **Find & Replace Text**: Clean or modify extracted content
- **Word Frequency Counter**: Analyze extracted text content
- **Case Tool**: Format extracted text content

#### See Also
- [Data Extraction Tools Overview](#data-extraction-tools-5-tools)
- [URL and Link Extractor Documentation](#url-and-link-extractor)
- [Web Content Processing Best Practices](#common-use-cases)

---



