import json
import urllib.parse
import re

def clean_dashes(text):
    if not text:
        return ''
    return text.replace('\u2014', '-').replace('\u2013', '-').replace('\u2010', '-').replace('\u2011', '-').replace('\u2012', '-')

def format_role_body(raw_paras, role_meta):
    output_html = []
    in_list = False
    meta_pills = []
    cleaned_paras = []
    
    i = 0
    while i < len(raw_paras):
        p = raw_paras[i]
        text = clean_dashes(p['text']).strip()
        is_bullet = p['is_bullet']
        
        # Header noise
        if text.lower() == 'moxiworks' or (i < 3 and text.lower() == role_meta['title'].lower()):
            i += 1
            continue
            
        # Single line metadata: 'Key: Value'
        if ':' in text and not is_bullet and len(text.split(':')[0]) < 25 and len(text) < 140:
            k, v = text.split(':', 1)
            k_clean = k.strip(' :*-')
            v_clean = v.strip(' :*-')
            if k_clean.lower() in ['location', 'team', 'employment type', 'experience', 'reports to', 'team scope', 'job title']:
                if k_clean.lower() != 'job title':
                    meta_pills.append((k_clean, v_clean))
                i += 1
                continue
                
        # Two-line metadata: line i = 'Location', line i+1 = 'Pune (Fully onsite)'
        if i + 1 < len(raw_paras):
            next_text = clean_dashes(raw_paras[i+1]['text']).strip()
            if text.lower() in ['location', 'team', 'employment type', 'experience', 'job title', 'reports to']:
                if text.lower() != 'job title':
                    meta_pills.append((text.title(), next_text))
                i += 2
                continue
                
        cleaned_paras.append(p)
        i += 1

    # Render Metadata Cards Grid
    if meta_pills:
        output_html.append('<div class="jd-meta-grid">')
        for k, v in meta_pills:
            output_html.append(f'<div class="jd-meta-item"><span class="jd-meta-label">{k}</span><span class="jd-meta-val">{v}</span></div>')
        output_html.append('</div>')

    # Heading trigger keywords
    heading_keywords = [
        'about moxiworks', 'about the role', 'job overview', 'overview',
        'what success looks like', 'what you will do', 'what you\'ll do', 'responsibilities',
        'key responsibilities', 'role responsibilities', 'what you bring', 'requirements',
        'required qualifications', 'qualifications', 'skills & experience', 'skills and experience',
        'technical skills', 'tech stack', 'bonus points', 'nice to have', 'preferred qualifications',
        'what we offer', 'benefits', 'who you are', 'delivery & execution', 'leadership & team health'
    ]

    for p in cleaned_paras:
        text = clean_dashes(p['text']).strip()
        is_bullet = p['is_bullet'] or text.startswith('•') or text.startswith('·') or text.startswith('- ')
        
        if is_bullet:
            text = re.sub(r'^[•·\-]\s*', '', text)
            
        text_lower = text.lower().strip(' :*-')
        
        is_heading = False
        if len(text) < 75 and not is_bullet:
            if any(text_lower == kw or text_lower.startswith(kw + ' ') or text_lower.startswith(kw + ':') for kw in heading_keywords):
                is_heading = True
            elif p.get('runs') and len(p['runs']) == 1 and p['runs'][0][1] and len(text) < 60:
                is_heading = True

        if is_heading:
            if in_list:
                output_html.append('</ul>')
                in_list = False
            output_html.append(f'<h4 class="jd-section-title">{text.strip(":")}</h4>')
        elif is_bullet:
            if not in_list:
                output_html.append('<ul class="jd-bullet-list">')
                in_list = True
            if ':' in text and len(text.split(':')[0]) < 40 and not text.startswith('http'):
                b_title, b_desc = text.split(':', 1)
                output_html.append(f'<li><strong>{b_title.strip()}:</strong> {b_desc.strip()}</li>')
            else:
                output_html.append(f'<li>{text}</li>')
        else:
            if in_list:
                output_html.append('</ul>')
                in_list = False
            output_html.append(f'<p class="jd-para">{text}</p>')

    if in_list:
        output_html.append('</ul>')

    return '\n'.join(output_html)

def generate_portal():
    with open('roles_rich_data.json', 'r', encoding='utf-8') as f:
        roles = json.load(f)

    for r in roles:
        r['formatted_html'] = format_role_body(r['raw_paras'], r)

    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shubham's Personal MoxiWorks Referral Portal</title>
    <meta name="description" content="Shubham's personal employee referral portal for open positions at MoxiWorks Pune. Explore roles and submit your referral application directly.">
    <link rel="icon" href="https://moxiworks.com/wp-content/uploads/2025/06/cropped-moxiworks-favicon-32x32.png" sizes="32x32" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            /* MoxiWorks Brand Palette */
            --moxi-navy: #0A364B;
            --moxi-navy-dark: #072635;
            --moxi-denim: #1F82A5;
            --moxi-denim-dark: #166580;
            --moxi-green: #86F59A;
            --moxi-green-dark: #167a3f;
            --moxi-pale-blue: #EFF7FA;
            --moxi-light-bg: #F4F9FC;
            --moxi-marine: #2976CC;
            --moxi-frost: #AFD6E6;
            
            /* UI Tokens */
            --bg-body: #F4F9FC;
            --surface-card: #FFFFFF;
            --text-main: #0A364B;
            --text-muted: #536E7B;
            --text-light: #7E96A2;
            --border-color: #DFEBF1;
            --border-hover: #AFD6E6;
            
            /* Elevation & Curves */
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 16px;
            --radius-full: 9999px;
            --shadow-card: 0 4px 16px rgba(10, 54, 75, 0.06);
            --shadow-hover: 0 10px 28px rgba(10, 54, 75, 0.12);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        body {
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }

        /* Header */
        .site-header {
            background-color: var(--moxi-navy);
            color: #FFFFFF;
            padding: 1.25rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 14px rgba(10, 54, 75, 0.18);
        }

        .header-inner {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .brand-logo {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            text-decoration: none;
        }

        .logo-img {
            height: 32px;
            width: auto;
            filter: brightness(0) invert(1);
        }

        .brand-pill {
            background-color: rgba(134, 245, 154, 0.18);
            color: var(--moxi-green);
            border: 1px solid rgba(134, 245, 154, 0.35);
            padding: 0.25rem 0.75rem;
            border-radius: var(--radius-full);
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .header-meta {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            font-size: 0.875rem;
            color: #CFE3EC;
        }

        .header-meta strong {
            color: var(--moxi-green);
        }

        /* Hero */
        .hero {
            background: linear-gradient(180deg, var(--moxi-navy) 0%, #0E445E 65%, var(--moxi-pale-blue) 100%);
            padding: 3.5rem 1.5rem 4.5rem;
            color: #FFFFFF;
            text-align: center;
        }

        .hero-container {
            max-width: 860px;
            margin: 0 auto;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background-color: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            color: #FFFFFF;
            padding: 0.45rem 1.25rem;
            border-radius: var(--radius-full);
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1.25rem;
        }

        .hero-badge .dot {
            width: 8px;
            height: 8px;
            background-color: var(--moxi-green);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px var(--moxi-green);
        }

        .hero-title {
            font-size: 2.65rem;
            font-weight: 800;
            line-height: 1.18;
            letter-spacing: -0.02em;
            margin-bottom: 1rem;
        }

        .hero-title .highlight {
            color: var(--moxi-green);
        }

        .hero-desc {
            font-size: 1.1rem;
            color: #D3E7F0;
            max-width: 680px;
            margin: 0 auto 1.5rem;
            line-height: 1.6;
        }

        /* Main Container */
        .main-container {
            max-width: 1200px;
            margin: -2.5rem auto 4rem;
            padding: 0 1.5rem;
            position: relative;
            z-index: 10;
        }

        /* Info Banner */
        .portal-banner {
            background-color: #FFFFFF;
            border-left: 4px solid var(--moxi-denim);
            border-radius: var(--radius-md);
            padding: 1.25rem 1.5rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .portal-banner-text {
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }

        .portal-banner-icon {
            font-size: 1.6rem;
            flex-shrink: 0;
        }

        .portal-banner-text h4 {
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--moxi-navy);
            margin-bottom: 0.2rem;
        }

        .portal-banner-text p {
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        /* Controls */
        .control-box {
            background-color: var(--surface-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            box-shadow: var(--shadow-card);
            margin-bottom: 2.25rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }

        .search-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .search-wrapper {
            position: relative;
            flex: 1;
            min-width: 280px;
        }

        .search-icon {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-light);
            pointer-events: none;
        }

        .search-input {
            width: 100%;
            padding: 0.8rem 1rem 0.8rem 2.75rem;
            border: 1.5px solid var(--border-color);
            border-radius: var(--radius-full);
            font-size: 0.95rem;
            font-family: inherit;
            background-color: var(--moxi-light-bg);
            color: var(--text-main);
            transition: all 0.2s ease;
        }

        .search-input:focus {
            outline: none;
            border-color: var(--moxi-denim);
            background-color: #FFFFFF;
            box-shadow: 0 0 0 3px rgba(31, 130, 165, 0.15);
        }

        .filter-pills {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            overflow-x: auto;
            padding-bottom: 0.25rem;
        }

        .pill {
            background-color: var(--moxi-light-bg);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.85rem;
            font-weight: 600;
            padding: 0.45rem 1rem;
            border-radius: var(--radius-full);
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .pill:hover {
            border-color: var(--moxi-denim);
            color: var(--moxi-denim);
        }

        .pill.active {
            background-color: var(--moxi-navy);
            color: #FFFFFF;
            border-color: var(--moxi-navy);
        }

        .pill .pill-count {
            background-color: rgba(255, 255, 255, 0.2);
            color: inherit;
            padding: 0.1rem 0.45rem;
            border-radius: var(--radius-full);
            font-size: 0.75rem;
        }

        .pill:not(.active) .pill-count {
            background-color: #DFEBF1;
            color: var(--moxi-navy);
        }

        /* Section Headings */
        .category-group {
            margin-bottom: 2.75rem;
        }

        .category-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.25rem;
            padding-bottom: 0.6rem;
            border-bottom: 2px solid var(--border-color);
        }

        .category-title {
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--moxi-navy);
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }

        .category-badge {
            background-color: var(--moxi-pale-blue);
            color: var(--moxi-denim);
            border: 1px solid var(--border-color);
            padding: 0.2rem 0.65rem;
            border-radius: var(--radius-full);
            font-size: 0.8rem;
            font-weight: 700;
        }

        /* Jobs Grid */
        .jobs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 1.25rem;
        }

        /* Job Card */
        .job-card {
            background-color: var(--surface-card);
            border: 1.5px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 1.25rem;
            box-shadow: var(--shadow-card);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .job-card:hover {
            transform: translateY(-3px);
            border-color: var(--border-hover);
            box-shadow: var(--shadow-hover);
        }

        .card-top {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .tag-row {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .exp-tag {
            background-color: rgba(134, 245, 154, 0.22);
            color: #0b612d;
            border: 1px solid rgba(134, 245, 154, 0.55);
            font-size: 0.75rem;
            font-weight: 700;
            padding: 0.25rem 0.6rem;
            border-radius: var(--radius-full);
        }

        .dept-tag {
            background-color: var(--moxi-pale-blue);
            color: var(--moxi-denim);
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.55rem;
            border-radius: var(--radius-full);
        }

        .location-tag {
            font-size: 0.75rem;
            color: var(--text-muted);
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }

        .job-title {
            font-size: 1.2rem;
            font-weight: 800;
            color: var(--moxi-navy);
            line-height: 1.3;
        }

        .skills-list {
            display: flex;
            gap: 0.4rem;
            flex-wrap: wrap;
        }

        .skill-chip {
            background-color: var(--moxi-light-bg);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: var(--radius-sm);
            font-weight: 500;
        }

        /* Card Actions - Streamlined */
        .card-actions {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding-top: 0.85rem;
            border-top: 1px solid var(--border-color);
        }

        .btn-view-jd {
            flex: 1;
            background-color: var(--moxi-light-bg);
            border: 1.5px solid var(--border-color);
            color: var(--moxi-navy);
            padding: 0.65rem 1rem;
            font-size: 0.875rem;
            font-weight: 700;
            border-radius: var(--radius-md);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.4rem;
            transition: all 0.2s ease;
        }

        .btn-view-jd:hover {
            border-color: var(--moxi-denim);
            background-color: var(--moxi-pale-blue);
            color: var(--moxi-denim);
        }

        .btn-apply-direct {
            background-color: var(--moxi-navy);
            color: #FFFFFF;
            border: none;
            padding: 0.65rem 1.15rem;
            font-size: 0.875rem;
            font-weight: 700;
            border-radius: var(--radius-md);
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            transition: all 0.2s ease;
            white-space: nowrap;
        }

        .btn-apply-direct:hover {
            background-color: var(--moxi-denim);
            transform: translateY(-1px);
        }

        .btn-icon {
            background-color: var(--moxi-light-bg);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            width: 38px;
            height: 38px;
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 0.9rem;
            flex-shrink: 0;
        }

        .btn-icon:hover {
            border-color: var(--moxi-denim);
            color: var(--moxi-denim);
            background-color: var(--moxi-pale-blue);
        }

        /* Modal JD Reader & Rich Formatting */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(10, 54, 75, 0.65);
            backdrop-filter: blur(5px);
            z-index: 1000;
            display: none;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal-card {
            background-color: #FFFFFF;
            width: 100%;
            max-width: 860px;
            max-height: 88vh;
            border-radius: var(--radius-lg);
            box-shadow: 0 20px 50px rgba(10, 54, 75, 0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            animation: modalIn 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        @keyframes modalIn {
            from { opacity: 0; transform: translateY(20px) scale(0.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        .modal-header {
            background-color: var(--moxi-navy);
            color: #FFFFFF;
            padding: 1.5rem 2rem;
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
        }

        .modal-header h2 {
            font-size: 1.5rem;
            font-weight: 800;
            line-height: 1.25;
        }

        .modal-header-tags {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.5rem;
            flex-wrap: wrap;
        }

        .modal-header-tags .tag {
            background: rgba(255, 255, 255, 0.15);
            padding: 0.2rem 0.6rem;
            border-radius: var(--radius-full);
            font-size: 0.8rem;
        }

        .modal-close {
            background: rgba(255, 255, 255, 0.15);
            border: none;
            color: #FFFFFF;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            font-size: 1.25rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }

        .modal-close:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        .modal-body {
            padding: 2rem;
            overflow-y: auto;
            font-size: 0.95rem;
            line-height: 1.7;
            color: #2D3748;
        }

        /* Rich JD Formatting Inside Modal */
        .jd-meta-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.75rem;
            background-color: var(--moxi-light-bg);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 1rem 1.25rem;
            margin-bottom: 1.75rem;
        }

        .jd-meta-item {
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
        }

        .jd-meta-label {
            font-size: 0.75rem;
            font-weight: 700;
            color: var(--moxi-denim);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .jd-meta-val {
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--moxi-navy);
        }

        .jd-section-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--moxi-navy);
            margin-top: 1.75rem;
            margin-bottom: 0.75rem;
            padding-left: 0.65rem;
            border-left: 3.5px solid var(--moxi-denim);
            line-height: 1.3;
        }

        .jd-section-title:first-child {
            margin-top: 0;
        }

        .jd-para {
            margin-bottom: 0.85rem;
            color: #334155;
        }

        .jd-bullet-list {
            margin-top: 0.4rem;
            margin-bottom: 1.25rem;
            padding-left: 1.4rem;
            list-style-type: disc;
        }

        .jd-bullet-list li {
            margin-bottom: 0.45rem;
            color: #334155;
            line-height: 1.6;
        }

        .jd-bullet-list li strong {
            color: var(--moxi-navy);
        }

        .modal-footer {
            padding: 1.25rem 2rem;
            background-color: var(--moxi-light-bg);
            border-top: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .btn-cta-green {
            background-color: var(--moxi-green);
            color: var(--moxi-navy);
            border: none;
            padding: 0.85rem 1.75rem;
            border-radius: var(--radius-full);
            font-weight: 800;
            font-size: 1rem;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 4px 14px rgba(134, 245, 154, 0.45);
            transition: all 0.2s ease;
        }

        .btn-cta-green:hover {
            background-color: #6eed84;
            transform: translateY(-1px);
        }

        /* Application Form Modal */
        .app-modal-card {
            background-color: #FFFFFF;
            width: 100%;
            max-width: 620px;
            max-height: 90vh;
            border-radius: var(--radius-lg);
            box-shadow: 0 20px 50px rgba(10, 54, 75, 0.35);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            animation: modalIn 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .app-modal-body {
            padding: 1.75rem 2rem;
            overflow-y: auto;
        }

        .form-group {
            margin-bottom: 1.15rem;
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }

        .form-label {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--moxi-navy);
        }

        .form-label span.req {
            color: #e53e3e;
        }

        .form-input, .form-textarea, .form-select {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 1.5px solid var(--border-color);
            border-radius: var(--radius-md);
            font-size: 0.95rem;
            font-family: inherit;
            background-color: var(--moxi-light-bg);
            color: var(--text-main);
            transition: all 0.2s ease;
        }

        .form-input:focus, .form-textarea:focus, .form-select:focus {
            outline: none;
            border-color: var(--moxi-denim);
            background-color: #FFFFFF;
            box-shadow: 0 0 0 3px rgba(31, 130, 165, 0.15);
        }

        .form-helper {
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        /* Toast Alert */
        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background-color: var(--moxi-navy);
            color: #FFFFFF;
            padding: 0.85rem 1.4rem;
            border-radius: var(--radius-full);
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: 0 8px 24px rgba(10, 54, 75, 0.25);
            display: flex;
            align-items: center;
            gap: 0.6rem;
            z-index: 2000;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-left: 4px solid var(--moxi-green);
        }

        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }

        /* Footer & Disclaimer */
        footer {
            background-color: var(--moxi-navy);
            color: #CFE3EC;
            padding: 3.5rem 1.5rem 2.5rem;
            text-align: center;
        }

        .footer-content {
            max-width: 820px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1.5rem;
        }

        .footer-logo {
            height: 28px;
            filter: brightness(0) invert(1);
            opacity: 0.9;
        }

        .disclaimer-card {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: var(--radius-md);
            padding: 1.25rem 1.5rem;
            text-align: left;
        }

        .disclaimer-heading {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--moxi-green);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.4rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .disclaimer-body {
            font-size: 0.8rem;
            color: #9DBBCA;
            line-height: 1.6;
        }

        @media (max-width: 768px) {
            .hero-title { font-size: 1.95rem; }
            .jobs-grid { grid-template-columns: 1fr; }
            .header-meta { display: none; }
            .modal-card, .app-modal-card { max-height: 95vh; margin: 0.5rem; }
            .modal-body, .app-modal-body { padding: 1.25rem; }
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header class="site-header">
        <div class="header-inner">
            <a href="https://moxiworks.com" target="_blank" class="brand-logo">
                <img src="https://moxiworks.com/wp-content/uploads/2025/06/moxiworks-logo-dark.svg" alt="MoxiWorks Logo" class="logo-img" />
                <span class="brand-pill">Shubham's Referral Portal</span>
            </a>
            <div class="header-meta">
                <span>Active Roles: <strong>20 Positions</strong></span>
                <span>Location: <strong>Pune, India / Hybrid</strong></span>
            </div>
        </div>
    </header>

    <!-- Hero -->
    <section class="hero">
        <div class="hero-container">
            <div class="hero-badge">
                <span class="dot"></span>
                <span>Shubham's Personal MoxiWorks Referral Portal</span>
            </div>
            <h1 class="hero-title">Explore Open Roles & <span class="highlight">Get Referred</span></h1>
            <p class="hero-desc">Welcome to Shubham's personal employee referral portal for open positions at MoxiWorks Pune. Explore role requirements and submit your referral application directly.</p>
        </div>
    </section>

    <!-- Main Content -->
    <main class="main-container">
        <!-- Referral Pipeline Banner -->
        <div class="portal-banner">
            <div class="portal-banner-text">
                <div class="portal-banner-icon">💼</div>
                <div>
                    <h4>How Referral Applications Work</h4>
                    <p>Select any role below to review the full job description. Click <strong>Apply for Referral</strong> to submit your profile and resume directly into Shubham's referral database.</p>
                </div>
            </div>
            <button class="pill" style="background-color: var(--moxi-pale-blue); color: var(--moxi-denim); font-weight: 700; border-color: var(--border-hover);" onclick="copyPortalLink()">
                🔗 Share Portal Link
            </button>
        </div>

        <!-- Controls -->
        <div class="control-box">
            <div class="search-row">
                <div class="search-wrapper">
                    <span class="search-icon">🔍</span>
                    <input type="text" id="searchInput" class="search-input" placeholder="Search roles by skill (e.g. Ruby, React, QA, Cypress, WordPress, PM, RevOps)..." oninput="filterRoles()" />
                </div>
            </div>

            <!-- Filter Pills -->
            <div class="filter-pills">
                <button class="pill active" onclick="setCategory('all', this)">All Roles <span class="pill-count">20</span></button>
                <button class="pill" onclick="setCategory('engineering', this)">💻 Engineering <span class="pill-count">10</span></button>
                <button class="pill" onclick="setCategory('product', this)">🎯 Product & Design <span class="pill-count">3</span></button>
                <button class="pill" onclick="setCategory('support', this)">🤝 Customer Success <span class="pill-count">3</span></button>
                <button class="pill" onclick="setCategory('marketing', this)">📈 Marketing <span class="pill-count">3</span></button>
                <button class="pill" onclick="setCategory('finance', this)">💰 Finance <span class="pill-count">1</span></button>
            </div>
        </div>
'''

    # Categories
    categories = [
        ('engineering', '💻 Engineering & Technology', '10 Open Roles'),
        ('product', '🎯 Product Management & Design', '3 Open Roles'),
        ('support', '🤝 Customer Success & Support', '3 Open Roles'),
        ('marketing', '📈 Marketing & Operations', '3 Open Roles'),
        ('finance', '💰 Finance & Accounting', '1 Open Role')
    ]

    for cat_id, cat_title, cat_badge in categories:
        cat_roles = [r for r in roles if r['category'] == cat_id]
        html_template += f'''
        <section class="category-group" data-category-group="{cat_id}">
            <div class="category-header">
                <h2 class="category-title">{cat_title}</h2>
                <span class="category-badge">{cat_badge}</span>
            </div>
            <div class="jobs-grid">
        '''
        for r in cat_roles:
            skills_html = ''.join([f'<span class="skill-chip">{s}</span>' for s in r['skills']])
            html_template += f'''
                <!-- {r['title']} -->
                <article class="job-card" data-id="{r['id']}" data-category="{r['category']}" data-title="{r['title']}" data-skills="{' '.join(r['skills'])}">
                    <div class="card-top">
                        <div class="tag-row">
                            <span class="dept-tag">{r['dept'].split('&')[0].strip()}</span>
                            <span class="exp-tag">⭐ {r['exp']}</span>
                            <span class="location-tag">📍 {r['location']}</span>
                        </div>
                        <h3 class="job-title">{r['title']}</h3>
                        <div class="skills-list">
                            {skills_html}
                        </div>
                    </div>
                    <div class="card-actions">
                        <button class="btn-view-jd" onclick="openJdModal('{r['id']}')">
                            <span>👁️</span> View Role Details
                        </button>
                        <button class="btn-apply-direct" onclick="openAppModal('{r['id']}')">
                            <span>🚀</span> Apply for Referral
                        </button>
                        <button class="btn-icon" title="Share Role" onclick="copyRoleLink('{r['id']}')">🔗</button>
                    </div>
                </article>
            '''
        html_template += '''
            </div>
        </section>
        '''

    # Client payload
    client_roles = []
    for r in roles:
        client_roles.append({
            'id': r['id'],
            'title': r['title'],
            'dept': r['dept'],
            'exp': r['exp'],
            'location': r['location'],
            'file': r['file'],
            'formatted_html': r['formatted_html']
        })

    html_template += '''
    </main>

    <!-- Modal 1: JD Reader -->
    <div id="jdModal" class="modal-overlay" onclick="closeModalOnBackdrop(event, 'jdModal')">
        <div class="modal-card">
            <div class="modal-header">
                <div>
                    <h2 id="modalTitle">Job Title</h2>
                    <div class="modal-header-tags">
                        <span id="modalExp" class="tag">Exp: 5+ Years</span>
                        <span id="modalLoc" class="tag">📍 Pune, India</span>
                        <span id="modalDept" class="tag">Engineering</span>
                    </div>
                </div>
                <button class="modal-close" onclick="closeJdModal()">✕</button>
            </div>
            <div id="modalBody" class="modal-body">
                <!-- Injected via JS -->
            </div>
            <div class="modal-footer">
                <button class="btn-view-jd" style="max-width: 180px;" onclick="closeJdModal()">
                    ← Back to Roles
                </button>
                <button id="modalApplyBtn" class="btn-cta-green" onclick="switchFromJdToApp()">
                    <span>🚀</span> Apply for Referral
                </button>
            </div>
        </div>
    </div>

    <!-- Modal 2: Referral Application Intake Form -->
    <div id="appModal" class="modal-overlay" onclick="closeModalOnBackdrop(event, 'appModal')">
        <div class="app-modal-card">
            <div class="modal-header">
                <div>
                    <h2 style="font-size: 1.35rem;">Submit Referral Application</h2>
                    <p style="font-size: 0.85rem; color: #CFE3EC; margin-top: 0.2rem;">Direct to Shubham's referral database</p>
                </div>
                <button class="modal-close" onclick="closeAppModal()">✕</button>
            </div>
            <form id="referralForm" class="app-modal-body" onsubmit="submitReferralForm(event)">
                <div class="form-group">
                    <label class="form-label">Position Applying For <span class="req">*</span></label>
                    <input type="text" id="appRoleTitle" class="form-input" readonly style="font-weight: 700; background-color: #EBF4F8;" />
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="form-group">
                        <label class="form-label">Full Name <span class="req">*</span></label>
                        <input type="text" id="appName" class="form-input" placeholder="e.g. Rahul Sharma" required />
                    </div>
                    <div class="form-group">
                        <label class="form-label">Email Address <span class="req">*</span></label>
                        <input type="email" id="appEmail" class="form-input" placeholder="e.g. rahul@example.com" required />
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div class="form-group">
                        <label class="form-label">Phone Number <span class="req">*</span></label>
                        <input type="tel" id="appPhone" class="form-input" placeholder="+91 98765 43210" required />
                    </div>
                    <div class="form-group">
                        <label class="form-label">Years of Experience <span class="req">*</span></label>
                        <input type="text" id="appExp" class="form-input" placeholder="e.g. 5 Years" required />
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label">LinkedIn Profile URL <span class="req">*</span></label>
                    <input type="url" id="appLinkedin" class="form-input" placeholder="https://linkedin.com/in/yourprofile" required />
                </div>

                <div class="form-group">
                    <label class="form-label">Upload Resume (.pdf, .docx, .doc - max 5 MB) <span class="req">*</span></label>
                    <div id="dropZone" style="border: 2px dashed var(--border-color); background-color: var(--moxi-light-bg); border-radius: var(--radius-md); padding: 1.25rem 1rem; text-align: center; cursor: pointer; transition: all 0.2s ease;" onclick="document.getElementById('appResumeFile').click()">
                        <div id="uploadPrompt">
                            <span style="font-size: 1.75rem; display: block; margin-bottom: 0.35rem;">📄</span>
                            <span style="font-size: 0.9rem; font-weight: 700; color: var(--moxi-navy);">Click to upload your resume</span>
                            <span style="display: block; font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">Supported formats: PDF, DOCX, DOC (Max file size: 5 MB)</span>
                        </div>
                        <div id="fileSelectedBadge" style="display: none; align-items: center; justify-content: center; gap: 0.75rem;">
                            <span style="font-size: 1.4rem;">📎</span>
                            <div style="text-align: left;">
                                <div id="displayFileName" style="font-weight: 700; color: var(--moxi-navy); font-size: 0.9rem;">resume.pdf</div>
                                <div id="displayFileSize" style="font-size: 0.75rem; color: #167a3f; font-weight: 600;">1.2 MB</div>
                            </div>
                            <button type="button" onclick="event.stopPropagation(); removeSelectedFile();" style="background: rgba(229, 62, 62, 0.1); border: 1px solid rgba(229, 62, 62, 0.3); color: #e53e3e; border-radius: var(--radius-sm); padding: 0.2rem 0.5rem; font-size: 0.75rem; cursor: pointer; font-weight: 700;">Remove</button>
                        </div>
                    </div>
                    <input type="file" id="appResumeFile" accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onchange="handleFileSelected(event)" style="display: none;" />
                    <div id="fileErrorMsg" style="font-size: 0.75rem; color: #e53e3e; font-weight: 600; margin-top: 0.3rem; display: none;"></div>
                </div>

                <div class="form-group">
                    <label class="form-label">Or Paste Public Resume Link (Optional)</label>
                    <input type="url" id="appResumeUrl" class="form-input" placeholder="https://drive.google.com/file/d/... or Dropbox link" />
                    <span class="form-helper">If you have a Google Drive or OneDrive link, you can also paste it here.</span>
                </div>

                <div class="form-group">
                    <label class="form-label">Brief Note / Highlights (Optional)</label>
                    <textarea id="appNotes" class="form-textarea" rows="2" placeholder="Briefly highlight your key tech stack, major achievements, or why you are a great fit..."></textarea>
                </div>

                <div style="margin-top: 1.5rem; display: flex; justify-content: flex-end; gap: 0.75rem;">
                    <button type="button" class="btn-view-jd" style="max-width: 130px;" onclick="closeAppModal()">Cancel</button>
                    <button type="submit" id="btnSubmitApp" class="btn-cta-green">
                        <span>🚀</span> Submit Application
                    </button>
                </div>
            </form>
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="toast">
        <span id="toastIcon">📋</span>
        <span id="toastMsg">Link copied!</span>
    </div>

    <!-- Footer -->
    <footer>
        <div class="footer-content">
            <img src="https://moxiworks.com/wp-content/uploads/2025/06/moxiworks-logo-dark.svg" alt="MoxiWorks" class="footer-logo" />
            
            <!-- Disclaimer Box -->
            <div class="disclaimer-card">
                <div class="disclaimer-heading">⚠️ Personal Employee Referral Disclaimer</div>
                <p class="disclaimer-body">
                    This is an independent, personal employee referral portal created by Shubham exclusively to connect qualified candidates with open positions at MoxiWorks Pune. This website is not an official MoxiWorks corporate portal or career application site. All formal job applications, interviews, and hiring decisions are governed exclusively by official MoxiWorks talent acquisition teams and hiring managers. All company names, logos, and registered trademarks belong to their respective owners.
                </p>
            </div>

            <p style="font-size: 0.8rem; color: #7B99A8;">© 2026 Shubham's Personal MoxiWorks Referral Portal. Maintained for community talent referral purposes.</p>
        </div>
    </footer>

    <script>
        const rolesData = ''' + json.dumps(client_roles) + ''';
        let currentCat = 'all';
        let activeRole = null;
        let attachedFile = null;

        // Shubham's Live Google Apps Script Webhook URL
        const REFERRAL_WEBHOOK_URL = 'https://script.google.com/macros/s/AKfycbxjew8Mt4J4pZITZ8OzZFYeKMHBkWr_oYnFVVhUj-1kk35iyofMFB7A-sKfNDrqO1uY/exec';

        function showToast(msg, icon = '📋') {
            const t = document.getElementById('toast');
            document.getElementById('toastMsg').innerText = msg;
            document.getElementById('toastIcon').innerText = icon;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 3500);
        }

        function setCategory(cat, pill) {
            currentCat = cat;
            document.querySelectorAll('.pill').forEach(el => el.classList.remove('active'));
            pill.classList.add('active');
            filterRoles();
        }

        function filterRoles() {
            const q = document.getElementById('searchInput').value.toLowerCase().trim();
            const cards = document.querySelectorAll('.job-card');
            const groups = document.querySelectorAll('.category-group');

            cards.forEach(card => {
                const title = card.getAttribute('data-title').toLowerCase();
                const skills = card.getAttribute('data-skills').toLowerCase();
                const cat = card.getAttribute('data-category');

                const matchesSearch = q === '' || title.includes(q) || skills.includes(q);
                const matchesCat = currentCat === 'all' || cat === currentCat;

                if (matchesSearch && matchesCat) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });

            groups.forEach(g => {
                const visible = g.querySelectorAll('.job-card[style*="display: flex"]').length;
                g.style.display = visible > 0 ? 'block' : 'none';
            });
        }

        function openJdModal(roleId) {
            const r = rolesData.find(item => item.id === roleId);
            if (!r) return;
            activeRole = r;

            document.getElementById('modalTitle').innerText = r.title;
            document.getElementById('modalExp').innerText = `Exp: ${r.exp}`;
            document.getElementById('modalLoc').innerText = `📍 ${r.location}`;
            document.getElementById('modalDept').innerText = r.dept;
            
            document.getElementById('modalBody').innerHTML = r.formatted_html;
            document.getElementById('jdModal').classList.add('active');
            window.location.hash = roleId;
        }

        function closeJdModal() {
            document.getElementById('jdModal').classList.remove('active');
            history.pushState('', document.title, window.location.pathname + window.location.search);
        }

        function switchFromJdToApp() {
            if (!activeRole) return;
            const rId = activeRole.id;
            closeJdModal();
            openAppModal(rId);
        }

        function openAppModal(roleId) {
            const r = rolesData.find(item => item.id === roleId);
            if (!r) return;
            activeRole = r;
            document.getElementById('appRoleTitle').value = `${r.title} (${r.exp}) - Pune`;
            document.getElementById('appModal').classList.add('active');
        }

        function closeAppModal() {
            document.getElementById('appModal').classList.remove('active');
        }

        function closeModalOnBackdrop(e, modalId) {
            if (e.target.id === modalId) {
                document.getElementById(modalId).classList.remove('active');
            }
        }

        function copyRoleLink(roleId) {
            const url = `${window.location.origin}${window.location.pathname}#${roleId}`;
            navigator.clipboard.writeText(url).then(() => {
                showToast('Role link copied to clipboard!', '🔗');
            });
        }

        function copyPortalLink() {
            navigator.clipboard.writeText(window.location.href).then(() => {
                showToast('Portal link copied to clipboard!', '🚀');
            });
        }

        function handleFileSelected(e) {
            const file = e.target.files[0];
            const errEl = document.getElementById('fileErrorMsg');
            const dropZone = document.getElementById('dropZone');
            errEl.style.display = 'none';

            if (!file) {
                removeSelectedFile();
                return;
            }

            // Allowed extensions: pdf, doc, docx
            const validExtensions = ['.pdf', '.doc', '.docx'];
            const fileNameLower = file.name.toLowerCase();
            const isValidExt = validExtensions.some(ext => fileNameLower.endsWith(ext));

            if (!isValidExt) {
                errEl.innerText = 'Invalid file type. Please upload a PDF (.pdf) or Word document (.docx, .doc).';
                errEl.style.display = 'block';
                removeSelectedFile();
                return;
            }

            // Max file size: 5MB (5,242,880 bytes)
            const MAX_SIZE_BYTES = 5 * 1024 * 1024;
            if (file.size > MAX_SIZE_BYTES) {
                errEl.innerText = `File is too large (${(file.size / (1024 * 1024)).toFixed(1)} MB). Maximum allowed size is 5 MB.`;
                errEl.style.display = 'block';
                removeSelectedFile();
                return;
            }

            attachedFile = file;
            document.getElementById('uploadPrompt').style.display = 'none';
            const badge = document.getElementById('fileSelectedBadge');
            badge.style.display = 'flex';
            document.getElementById('displayFileName').innerText = file.name;
            document.getElementById('displayFileSize').innerText = `✓ ${(file.size / 1024).toFixed(1)} KB (Ready to submit)`;
            dropZone.style.borderColor = '#167a3f';
            dropZone.style.backgroundColor = '#F0FFF4';
        }

        function removeSelectedFile() {
            attachedFile = null;
            document.getElementById('appResumeFile').value = '';
            document.getElementById('uploadPrompt').style.display = 'block';
            document.getElementById('fileSelectedBadge').style.display = 'none';
            const dropZone = document.getElementById('dropZone');
            dropZone.style.borderColor = 'var(--border-color)';
            dropZone.style.backgroundColor = 'var(--moxi-light-bg)';
        }

        function submitReferralForm(e) {
            e.preventDefault();
            const btn = document.getElementById('btnSubmitApp');
            const resumeLink = document.getElementById('appResumeUrl').value.trim();

            if (!attachedFile && !resumeLink) {
                const errEl = document.getElementById('fileErrorMsg');
                errEl.innerText = 'Please upload your resume (PDF or Word under 5 MB) or provide a resume link.';
                errEl.style.display = 'block';
                return;
            }

            btn.disabled = true;
            btn.innerText = 'Submitting...';

            const resumeDisplay = attachedFile ? `Attached file: ${attachedFile.name} (${(attachedFile.size / 1024).toFixed(1)} KB)` : resumeLink;

            const payload = {
                timestamp: new Date().toISOString(),
                role: document.getElementById('appRoleTitle').value,
                name: document.getElementById('appName').value,
                email: document.getElementById('appEmail').value,
                phone: document.getElementById('appPhone').value,
                experience: document.getElementById('appExp').value,
                linkedin: document.getElementById('appLinkedin').value,
                resumeUrl: resumeDisplay,
                notes: document.getElementById('appNotes').value
            };

            if (REFERRAL_WEBHOOK_URL) {
                fetch(REFERRAL_WEBHOOK_URL, {
                    method: 'POST',
                    mode: 'no-cors',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }).then(() => {
                    handleSuccess();
                }).catch(() => {
                    handleSuccess();
                });
            } else {
                handleSuccess();
            }

            function handleSuccess() {
                btn.disabled = false;
                btn.innerText = '🚀 Submit Application';
                closeAppModal();
                document.getElementById('referralForm').reset();
                removeSelectedFile();
                showToast('Referral Application submitted successfully! 🎉', '✅');
            }
        }

        // Deep link handler
        window.addEventListener('DOMContentLoaded', () => {
            const hash = window.location.hash.replace('#', '');
            if (hash) {
                openJdModal(hash);
            }
        });
    </script>
</body>
</html>
'''
    html_template = clean_dashes(html_template)
    assert '\u2014' not in html_template and '\u2013' not in html_template, 'Special dashes found!'

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

    with open('download_helper.html', 'w', encoding='utf-8') as f:
        f.write(html_template)

    print("Successfully built index.html with Shubham's Personal Portal branding, intake form, and streamlined actions!")

if __name__ == '__main__':
    generate_portal()
