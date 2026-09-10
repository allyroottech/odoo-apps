// Lightweight markdown-to-HTML renderer used by the attachment preview iframe.
// No external dependencies. Loaded via <script src> in the preview page template.
(function () {
    'use strict';

    function esc(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    // Only allow schemes that can't run script when clicked. Anything else
    // (javascript:, data:, vbscript:, ...) is neutralized to '#'. A URL with
    // no scheme at all (relative path, anchor) is considered safe.
    function safeHref(url) {
        var stripped = url.trim().replace(/[\s\x00-\x1f]+/g, '');
        if (/^(https?:|mailto:)/i.test(stripped)) {
            return url;
        }
        return /^[a-z][a-z0-9+.-]*:/i.test(stripped) ? '#' : url;
    }

    // Format inline markdown: inline code, bold, italic, links.
    // Inline code is extracted first so its content is never altered by other rules.
    function inlineFmt(raw) {
        var saved = [];
        var s = raw.replace(/`([^`\n]+)`/g, function (_, c) {
            saved.push('<code>' + esc(c) + '</code>');
            return '\x01' + (saved.length - 1) + '\x01';
        });
        s = esc(s);
        s = s.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
        s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        s = s.replace(/__(.+?)__/g, '<strong>$1</strong>');
        s = s.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
        s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function (_, text, href) {
            return '<a href="' + safeHref(href) + '" target="_blank" rel="noopener">' + text + '</a>';
        });
        return s.replace(/\x01(\d+)\x01/g, function (_, i) { return saved[+i]; });
    }

    function splitTableRow(line) {
        var parts = line.split('|');
        if (parts[0].trim() === '') parts = parts.slice(1);
        if (parts.length && parts[parts.length - 1].trim() === '') parts = parts.slice(0, -1);
        return parts.map(function (c) { return c.trim(); });
    }

    function render(src) {
        var lines = src.split('\n');
        var out = [];
        var i = 0;

        while (i < lines.length) {
            var line = lines[i];

            // Fenced code block
            if (/^```/.test(line)) {
                i++;
                var cb = [];
                while (i < lines.length && !/^```/.test(lines[i])) {
                    cb.push(esc(lines[i++]));
                }
                out.push('<pre><code>' + cb.join('\n') + '</code></pre>');
                i++;
                continue;
            }

            // ATX header (#, ##, … ######)
            var hm = /^(#{1,6})\s+(.+)$/.exec(line);
            if (hm) {
                var lv = hm[1].length;
                out.push('<h' + lv + '>' + inlineFmt(hm[2]) + '</h' + lv + '>');
                i++;
                continue;
            }

            // Horizontal rule
            if (/^(---|\*\*\*|___)\s*$/.test(line)) {
                out.push('<hr>');
                i++;
                continue;
            }

            // Table: line has | and the next line is a separator (---|---)
            if (line.indexOf('|') !== -1 && i + 1 < lines.length && /^\|?[\s\-:|]+\|/.test(lines[i + 1])) {
                var hcols = splitTableRow(line);
                out.push('<table><thead><tr>' +
                    hcols.map(function (c) { return '<th>' + inlineFmt(c) + '</th>'; }).join('') +
                    '</tr></thead><tbody>');
                i += 2;
                while (i < lines.length && lines[i].indexOf('|') !== -1 && !/^\|?[\s\-:|]+\|/.test(lines[i])) {
                    var rcols = splitTableRow(lines[i]);
                    out.push('<tr>' + rcols.map(function (c) { return '<td>' + inlineFmt(c) + '</td>'; }).join('') + '</tr>');
                    i++;
                }
                out.push('</tbody></table>');
                continue;
            }

            // Ordered list
            if (/^\d+\.\s/.test(line)) {
                out.push('<ol>');
                while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
                    out.push('<li>' + inlineFmt(lines[i].replace(/^\d+\.\s+/, '')) + '</li>');
                    i++;
                }
                out.push('</ol>');
                continue;
            }

            // Unordered list
            if (/^[*\-+]\s/.test(line)) {
                out.push('<ul>');
                while (i < lines.length && /^[*\-+]\s/.test(lines[i])) {
                    out.push('<li>' + inlineFmt(lines[i].replace(/^[*\-+]\s+/, '')) + '</li>');
                    i++;
                }
                out.push('</ul>');
                continue;
            }

            // Blockquote
            if (/^>\s?/.test(line)) {
                var bq = [];
                while (i < lines.length && /^>\s?/.test(lines[i])) {
                    bq.push(lines[i++].replace(/^>\s?/, ''));
                }
                out.push('<blockquote>' + inlineFmt(bq.join(' ')) + '</blockquote>');
                continue;
            }

            // Blank line
            if (!line.trim()) {
                i++;
                continue;
            }

            // Paragraph: collect until blank line or a block-level marker
            var para = [];
            while (
                i < lines.length &&
                lines[i].trim() &&
                !/^(#{1,6}\s|```|>\s?|\d+\.\s|[*\-+]\s|---|\*\*\*|___)/.test(lines[i]) &&
                lines[i].indexOf('|') === -1
            ) {
                para.push(lines[i++]);
            }
            if (para.length) {
                out.push('<p>' + inlineFmt(para.join(' ')) + '</p>');
            }
        }

        return out.join('\n');
    }

    document.addEventListener('DOMContentLoaded', function () {
        var srcEl = document.getElementById('o-cap-md-src');
        var bodyEl = document.getElementById('o-cap-md-body');
        if (!srcEl || !bodyEl) return;
        try {
            var src = JSON.parse(srcEl.textContent || srcEl.innerText);
            bodyEl.innerHTML = render(src);
        } catch (e) {
            bodyEl.textContent = 'Error rendering preview: ' + e.message;
        }
    });
}());
