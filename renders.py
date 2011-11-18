#!/usr/bin/env python

def javascript_insert (base_path, filename_list):
    """Adds JavaScript files into an html page. Files that should be loaded into every page can be added to the "SCRIPTS" list."""
    html = "<!-- SCRIPTS -->\n"
    SCRIPTS = [
            ("ext", "https://ajax.googleapis.com/ajax/libs/jquery/1.6.4.jquery.min.js"), #jQuery
            (base_path, "ajax_forms.js"),                                                #for ajaxSuxmit()
            ("ext", "http://www.turnleftllc.com/api/tl_forms.js"),                       #TL Forms
            (base_path, "globals.js"),
            (base_path, "userMenu.js"),
            (base_path, "overlay.js"),
            ]
    
    inclusions = []

    for script in SCRIPTS:
        if script[0] != "ext":
            path= script[0]+script[1]
        else:
            path = script[1]
        inclusions.append(path)

    for filename in filename_list:
        full_path = base_path + filename + ".js"
        inclusions.append(full_path)

    for script in inclusions:
        html += "<script type='text/javascript' src='%s'></script>\n" % (script)

    return html
