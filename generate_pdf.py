#!/usr/bin/env python3
"""
Enhanced WeasyPrint PDF generator for ZD12 Rulebook
Run this locally to generate PDFs from your HTML with customizable options.

PRESETS:
    --preset booklet       5.5x8.5" booklet (statement size) with mirrored headers
    --preset screen        Letter size, screen media type
    --preset print         Letter size, print media type (default)

Usage:
    python generate_pdf.py [html_file] [pdf_output] [options]

Examples:
    python generate_pdf.py
    python generate_pdf.py --preset booklet
    python generate_pdf.py --preset booklet --margin 0.25
    python generate_pdf.py --preset booklet --dpi 300 --margin-left 0.3
"""

import weasyprint
import sys
from pathlib import Path
import argparse
from typing import Dict, Any

# Page size presets (width, height in inches)
PAGE_PRESETS = {
    'letter': ('8.5in', '11in'),
    'a4': ('210mm', '297mm'),
    'a5': ('148mm', '210mm'),
    'booklet': ('5.5in', '8.5in'),  # Letter folded in half
    'halflet': ('5.5in', '8.5in'),  # Same as booklet
    'statement': ('5.5in', '8.5in'),  # Same as booklet
}

# Output presets with default settings
OUTPUT_PRESETS = {
    'booklet': {
        'page_size': 'booklet',
        'page_width': '5.5in',
        'page_height': '8.5in',
        'margin_top': '0.15in',
        'margin_right': '0.15in',
        'margin_bottom': '0.15in',
        'margin_left': '0.15in',
        'mirrored_margins': True,
        'mirrored_headers': True,
        'outer_page_numbers': True,
        'running_headers': True,
        'media_type': 'print',
        'dpi': 150,
    },
    'screen': {
        'page_size': 'letter',
        'margin_top': '0.5in',
        'margin_right': '0.5in',
        'margin_bottom': '0.5in',
        'margin_left': '0.5in',
        'media_type': 'screen',
        'dpi': 96,
    },
    'print': {
        'page_size': 'letter',
        'margin_top': '0.75in',
        'margin_right': '0.5in',
        'margin_bottom': '0.75in',
        'margin_left': '0.75in',
        'media_type': 'print',
        'dpi': 96,
    }
}

def generate_booklet_css(margin_top: str = '0.15in', margin_bottom: str = '0.15in',
                        margin_left: str = '0.15in', margin_right: str = '0.15in',
                        running_headers: bool = True) -> str:
    """
    Generate CSS for booklet layout with mirrored headers/footers and outer page numbers.
    
    Args:
        margin_top: Top margin
        margin_bottom: Bottom margin
        margin_left: Left margin (will be mirrored on right-hand pages)
        margin_right: Right margin (will be mirrored on left-hand pages)
        running_headers: Include auto-generated running headers based on h1/h2
    
    Returns:
        CSS string to inject into the HTML
    """
    
    css = f"""
    /* ========================================
       BOOKLET LAYOUT - AUTO-GENERATED
       ======================================== */
    
    @font-face {{
      font-family: 'Playwrite DE Grund';
      src: url('fonts/Playwrite DE Grund Guides.ttf') format('truetype');
      font-weight: normal;
      font-style: normal;
      font-display: swap;
    }}
    
    @font-face {{
      font-family: 'Instrument Serif';
      src: url('fonts/Instrument_Serif.ttf') format('truetype');
      font-weight: normal;
      font-style: normal;
      font-display: swap;
    }}
    
    @page {{
        size: 5.5in 8.5in;
        margin: {margin_top} {margin_right} {margin_bottom} {margin_left};
    }}
    
    /* Ensure headings use the correct font - explicit and with fallbacks */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Playwrite DE Grund', cursive !important;
        font-kerning: auto;
        text-rendering: geometricPrecision;
        -webkit-font-smoothing: antialiased;
    }}
    
    /* Left-hand (even) pages - page number on left, running header on right */
    @page :left {{
        margin: {margin_top} {margin_left} {margin_bottom} {margin_right};
        
        @bottom-left {{
            content: counter(page);
            font-family: 'Instrument Serif', serif;
            font-size: 8pt;
            color: #999;
            text-align: left;
        }}
        
        @bottom-right {{
            content: '';
        }}
        
        @top-left {{
            content: '';
        }}
        
        @top-right {{
            content: string(chapter-header);
            font-family: 'Instrument Serif', serif;
            font-size: 8pt;
            color: #999;
            text-align: right;
        }}
    }}
    
    /* Right-hand (odd) pages - running header on left, page number on right */
    @page :right {{
        margin: {margin_top} {margin_right} {margin_bottom} {margin_left};
        
        @bottom-left {{
            content: '';
        }}
        
        @bottom-right {{
            content: counter(page);
            font-family: 'Instrument Serif', serif;
            font-size: 8pt;
            color: #999;
            text-align: right;
        }}
        
        @top-left {{
            content: string(chapter-header);
            font-family: 'Instrument Serif', serif;
            font-size: 8pt;
            color: #999;
            text-align: left;
        }}
        
        @top-right {{
            content: '';
        }}
    }}
    
    /* First page - no headers or footers */
    @page :first {{
        @top-left {{ content: none; }}
        @top-right {{ content: none; }}
        @bottom-left {{ content: none; }}
        @bottom-right {{ content: none; }}
    }}
    
    /* Set running headers from h1 elements (chapter titles) */
    h1 {{
        string-set: chapter-header content(text);
        page-break-before: always;
    }}
    
    h1:first-of-type {{
        page-break-before: avoid;
    }}
    
    /* Also capture h2 for subsection headers if desired */
    h2 {{
        string-set: chapter-header content(text);
    }}
    """
    
    return css

def get_unique_filename(output_file):
    """
    If output_file already exists, append an incrementing number to the filename.
    
    Args:
        output_file: The desired output filename
    
    Returns:
        A unique filename that doesn't exist yet
    """
    output_path = Path(output_file)
    
    # If file doesn't exist, return as-is
    if not output_path.exists():
        return output_file
    
    # File exists, so find a unique name by appending a number
    stem = output_path.stem  # filename without extension
    suffix = output_path.suffix  # extension like .pdf
    parent = output_path.parent  # directory
    
    counter = 1
    while True:
        new_filename = f"{stem}_{counter}{suffix}"
        new_path = parent / new_filename
        if not new_path.exists():
            return str(new_path)
        counter += 1

def generate_pdf(html_file, output_file, **options):
    """Convert HTML file to PDF with customizable options"""
    # Check if output file exists and get unique name if needed
    output_file = get_unique_filename(output_file)
    
    print(f"Converting {html_file} to {output_file}...")
    print(f"Options: {options}\n")

    try:
        # Load HTML with explicit UTF-8 encoding
        html_content = Path(html_file).read_text(encoding='utf-8')
        
        # Ensure proper charset declaration in HTML
        if '<meta charset' not in html_content.lower():
            html_content = html_content.replace(
                '<head>',
                '<head>\n    <meta charset="UTF-8">'
            )
        
        # If booklet mode with running headers, inject CSS
        if options.get('running_headers') and options.get('mirrored_headers'):
            booklet_css = generate_booklet_css(
                margin_top=options.get('margin_top', '0.15in'),
                margin_bottom=options.get('margin_bottom', '0.15in'),
                margin_left=options.get('margin_left', '0.15in'),
                margin_right=options.get('margin_right', '0.15in'),
                running_headers=True
            )
            
            # Inject the booklet CSS into the head
            if '</head>' in html_content:
                html_content = html_content.replace(
                    '</head>',
                    f'<style>{booklet_css}</style>\n</head>'
                )
        
        # Convert to absolute path for base_url
        html_file_path = str(Path(html_file).resolve())
        html = weasyprint.HTML(string=html_content, base_url=html_file_path)
        
        # Build kwargs for write_pdf()
        write_kwargs = {}
        
        # Resolution/DPI
        if options.get('dpi'):
            write_kwargs['resolution'] = options['dpi']
            print(f"  📐 DPI: {options['dpi']}")
        
        # Uncompressed PDF (useful for debugging/inspection)
        if options.get('uncompressed'):
            write_kwargs['uncompressed_pdf'] = True
            print(f"  📦 Uncompressed PDF: Enabled")
        
        # PDF version optimization
        if options.get('pdf_version'):
            write_kwargs['pdf_version'] = options['pdf_version']
            print(f"  📄 PDF Version: {options['pdf_version']}")
        
        # CSS media type (print or screen)
        if options.get('media_type'):
            write_kwargs['media_type'] = options['media_type']
            print(f"  🎨 Media Type: {options['media_type']}")
        
        # Booklet-specific output
        if options.get('mirrored_headers'):
            print(f"  📖 Booklet mode: Mirrored headers/footers")
            if options.get('outer_page_numbers'):
                print(f"     ✓ Page numbers in outer corners")
            if options.get('running_headers'):
                print(f"     ✓ Running headers from h1/h2 (auto-generated)")
        
        if options.get('margin_top'):
            print(f"  ⬆️  Top margin: {options['margin_top']}")
            print(f"  ⬇️  Bottom margin: {options['margin_bottom']}")
            print(f"  ⬅️  Left margin: {options['margin_left']}")
            print(f"  ➡️  Right margin: {options['margin_right']}")
        
        # Write PDF with collected options
        html.write_pdf(output_file, **write_kwargs)
        
        # Calculate file size
        file_size = Path(output_file).stat().st_size / 1024  # KB
        print(f"\n✓ PDF created: {output_file}")
        print(f"✓ File size: {file_size:.1f} KB")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Generate ZD12 Rulebook PDF with customizable options & booklet support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
PRESETS:
  --preset booklet       5.5x8.5" booklet (statement size) with mirrored headers
                         and outer page numbers. 0.15" margins. Perfect for half-
                         fold letter booklets. Running headers auto-generated from h1/h2.
  --preset screen        Letter size, screen media type (96 DPI)
  --preset print         Letter size, print media type (default, 96 DPI)

PRACTICAL CONTROLS:
  --dpi DPI              Set resolution in dots per inch (default: 96)
  --page-size SIZE       Page size: letter, a4, a5, booklet (default: letter)
  --landscape            Use landscape orientation instead of portrait
  --media-type TYPE      CSS media type: print or screen (default: print)

MARGIN CONTROLS:
  --margin SIZE          Set all margins at once (e.g., --margin 0.25)
  --margin-top SIZE      Top margin (default: 0.75in)
  --margin-bottom SIZE   Bottom margin (default: 0.75in)
  --margin-left SIZE     Left margin (default: 0.5in)
  --margin-right SIZE    Right margin (default: 0.5in)

BOOKLET OPTIONS:
  --mirrored-headers     Enable mirrored headers/footers (alternating left/right)
  --running-headers      Auto-generate headers from h1/h2 (booklet mode)
  --outer-page-numbers   Put page numbers on outer edges of spread (booklet mode)

DISCOVERY KNOBS (Experimental):
  --uncompressed         Generate uncompressed PDF (larger, debuggable)
  --pdf-version VERSION  PDF version: 1.4, 1.7, 2.0 (default: auto)

EXAMPLES:
  # Quick booklet (5.5x8.5, 0.15" margins, auto headers & outer page numbers)
  python generate_pdf.py --preset booklet
  
  # Adjust booklet margins for binding gutter
  python generate_pdf.py --preset booklet --margin-left 0.25 --margin-right 0.15
  
  # High quality booklet for print shop
  python generate_pdf.py --preset booklet --dpi 300
  
  # Letter size, screen media type
  python generate_pdf.py --preset screen
  
  # Custom margins, 5.5x8.5
  python generate_pdf.py --page-size booklet --margin-left 0.3 --margin-right 0.2
        """
    )
    
    # Positional arguments
    parser.add_argument('html_input', nargs='?', default='index.html',
                        help='Input HTML file (default: index.html)')
    parser.add_argument('pdf_output', nargs='?', default='build/zd12-rulebook.pdf',
                        help='Output PDF file (default: build/zd12-rulebook.pdf)')
    
    # Preset
    parser.add_argument('--preset', choices=['booklet', 'screen', 'print'],
                        help='Use a preset configuration')
    
    # Practical controls
    parser.add_argument('--dpi', type=int,
                        help='Resolution in DPI')
    parser.add_argument('--page-size', default='letter',
                        help='Page size: letter, a4, a5, booklet (default: letter)')
    parser.add_argument('--landscape', action='store_true',
                        help='Use landscape orientation')
    parser.add_argument('--media-type', choices=['print', 'screen'],
                        help='CSS media type')
    
    # Margin controls
    parser.add_argument('--margin', type=str,
                        help='Set all margins at once')
    parser.add_argument('--margin-top', type=str,
                        help='Top margin')
    parser.add_argument('--margin-bottom', type=str,
                        help='Bottom margin')
    parser.add_argument('--margin-left', type=str,
                        help='Left margin')
    parser.add_argument('--margin-right', type=str,
                        help='Right margin')
    
    # Booklet options
    parser.add_argument('--mirrored-headers', action='store_true',
                        help='Enable mirrored headers/footers')
    parser.add_argument('--running-headers', action='store_true',
                        help='Auto-generate running headers from h1/h2')
    parser.add_argument('--outer-page-numbers', action='store_true',
                        help='Put page numbers on outer edges')
    
    # Discovery knobs
    parser.add_argument('--uncompressed', action='store_true',
                        help='Generate uncompressed PDF (larger, debuggable)')
    parser.add_argument('--pdf-version', choices=['1.4', '1.7', '2.0'],
                        help='Target PDF version')
    
    args = parser.parse_args()
    
    # Start with preset if specified
    options = {}
    if args.preset:
        if args.preset in OUTPUT_PRESETS:
            options = OUTPUT_PRESETS[args.preset].copy()
            print(f"📋 Using preset: {args.preset}\n")
    
    # Override with command-line arguments
    if args.dpi:
        options['dpi'] = args.dpi
    if args.page_size:
        options['page_size'] = args.page_size
    if args.landscape:
        options['landscape'] = args.landscape
    if args.media_type:
        options['media_type'] = args.media_type
    if args.uncompressed:
        options['uncompressed'] = args.uncompressed
    if args.pdf_version:
        options['pdf_version'] = args.pdf_version
    
    # Handle margins
    if args.margin:
        options['margin_top'] = args.margin
        options['margin_bottom'] = args.margin
        options['margin_left'] = args.margin
        options['margin_right'] = args.margin
    if args.margin_top:
        options['margin_top'] = args.margin_top
    if args.margin_bottom:
        options['margin_bottom'] = args.margin_bottom
    if args.margin_left:
        options['margin_left'] = args.margin_left
    if args.margin_right:
        options['margin_right'] = args.margin_right
    
    # Handle booklet options
    if args.mirrored_headers:
        options['mirrored_headers'] = True
    if args.running_headers:
        options['running_headers'] = True
    if args.outer_page_numbers:
        options['outer_page_numbers'] = True
    
    # Set defaults if not specified
    options.setdefault('dpi', 96)
    options.setdefault('media_type', 'print')
    
    # Generate PDF
    generate_pdf(args.html_input, args.pdf_output, **options)

if __name__ == "__main__":
    main()
