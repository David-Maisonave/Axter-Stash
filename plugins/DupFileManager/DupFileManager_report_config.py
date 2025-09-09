# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link:
# https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager

# HTML Report Options **************************************************
report_config = {    
    # Paginate HTML report. Maximum number of results to display on one page, before adding (paginating) an additional page.
    "htmlReportPaginate" : 100,
    # If enabled, report displays the scene cover as a preview image
    "htmlIncludeCoverImage" : False,
    # If enabled, report displays Webp as a preview image
    "htmlIncludeWebpPreview" : False,
    # If enabled, report displays an image preview similar to sceneDuplicateChecker
    "htmlIncludeImagePreview" : False,
    "htmlImagePreviewSize" : 140,
    "htmlImagePreviewPopupSize" : 600,
    # If enabled, report displays a video preview
    "htmlIncludeVideoPreview" : True,
    "htmlVideoPreviewWidth" : 160,
    "htmlVideoPreviewHeight" : 120,
    # The number of seconds in time difference for supper highlight on htmlReport
    "htmlHighlightTimeDiff" : 3,
    # If enabled, report displays stream instead of preview for video
    "streamOverPreview" : False, # This option works in Chrome, but does not work very well on firefox.
    # Supper highlight for details with higher resolution or duration
    "htmlSupperHighlight" : "yellow",
    # Text color for details with different resolution, duration, size, bitrate,codec, or framerate
    "htmlDetailDiffTextColor" : "violet", # Candid colors Magenta Tomato Violet
    # Lower highlight for details with slightly higher duration
    "htmlLowerHighlight" : "nyanza",
    # The report background color
    "htmlReportBackgroundColor" : "#f0f5f5",
    # The report text color
    "htmlReportTextColor" : "black",
    # HTML report postfiox, after table listing
    "htmlReportPostfix" : "\n</div></body></html>",
    # HTML report table
    "htmlReportTable" : "<table style=\"width:100%\">",
    # HTML report table row
    "htmlReportTableRow" : "<tr>",
    # HTML report table header
    "htmlReportTableHeader" : "<th>",
    # HTML report table data
    "htmlReportTableData" : "<td>",
     # HTML report video preview
    "htmlReportVideoPreview" : "controls", # Alternative option "autoplay loop controls" or "autoplay controls"
    # Name of the HTML file to create
    "htmlReportName" : "DuplicateTagScenes.html",
    # Includes scene dropdown menu
    "htmlIncludeDropdownMenu" : True,
    # If enabled, create an HTML report when tagging duplicate files
    "createHtmlReport" : True,
    # To use a private or an alternate site to access report and advance menu
    "remoteReportDirURL" : "https://stash.axter.com/1.1/",
    # To use a private or an alternate site to access jquery, easyui, and jquery.prompt
    "js_DirURL" : "https://www.axter.com/js/",
    # Alternative JQuery UI interface option.
    "htmlJQueryUI" : "easyui", # Only easyui and easyuiPrim is currently supported.
    # Alternative JQuery UI stylesheet and script
    "htmlJQueryUiLinks" : {
        # http://www.jeasyui.com/demo/main/index.php?plugin=SplitButton&theme=material-teal&dir=ltr&pitem=&sort=asc
        "easyui"    : ['<link rel="stylesheet" type="text/css" href="[js_DirURL]easyui/themes/icon.css">',
                    '<link rel="stylesheet" type="text/css" href="[js_DirURL]easyui/themes/black/easyui.css">',
                    '<script type="text/javascript" src="[js_DirURL]easyui/jquery.easyui.min.js"></script>'],
        # https://getbootstrap.com/docs/5.3/components/dropdowns/
        "bootstrap" : ['<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">',
                    '<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>',
                    '<link rel="stylesheet" type="text/css" href="https://axter.com/js/jqueryui/jquery-ui.min.css">',
                    '<script type="text/javascript" src="https://axter.com/js/jqueryui/jquery-ui.min.js"></script>'],
        # https://www.primefaces.org/primeui/index.html#splitbutton
        "primeui" : ['<link rel="stylesheet" type="text/css" href="[js_DirURL]primeui/primeui-all.min.css">',
                    '<script type="text/javascript" src="[js_DirURL]primeui/primeui-all.min.js"></script>'],
        # https://docs.webix.com/desktop__menu.html
        "webix"     : ['<link rel="stylesheet" type="text/css" href="[js_DirURL]webix/codebase/webix.css">',
                    '<script type="text/javascript" src="[js_DirURL]webix/codebase/webix.js"></script>'],
        # https://primereact.org/splitbutton/
        "primereact": ['<link rel="stylesheet" type="text/css" href="">',
                    '<script type="text/javascript" src=""></script>'],
        # https://jqueryui.com/resources/demos/controlgroup/splitbutton.html
        "jeasyui": ['<link rel="stylesheet" type="text/css" href="https://axter.com/js/jqueryui/jquery-ui.min.css">',
                    '<script type="text/javascript" src="https://axter.com/js/jqueryui/jquery-ui.min.js"></script>',
                    '<link rel="stylesheet" type="text/css" href="https://axter.com/js/jqueryui/jquery-ui.theme.min.css">',
                    '<link rel="stylesheet" type="text/css" href="https://axter.com/js/jqueryui/jquery-ui.structure.min.css">'],
        # The following is to test mixing UI's
        # primeui seems to work well with easyui
        "easyuiPrim": ['<link rel="stylesheet" type="text/css" href="[js_DirURL]easyui/themes/icon.css">',
                    '<link rel="stylesheet" type="text/css" href="[js_DirURL]easyui/themes/black/easyui.css">',
                    '<script type="text/javascript" src="[js_DirURL]easyui/jquery.easyui.min.js"></script>',
                    '<link rel="stylesheet" type="text/css" href="[js_DirURL]primeui/primeui-all.min.css">',
                    '<script type="text/javascript" src="[js_DirURL]primeui/primeui-all.min.js"></script>'],
        # bootstrap does NOT work well with easyui
        "easyuiBoot": ['<link rel="stylesheet" type="text/css" href="[js_DirURL]easyui/themes/icon.css">',
                    '<link rel="stylesheet" type="text/css" href="[js_DirURL]easyui/themes/black/easyui.css">',
                    '<script type="text/javascript" src="[js_DirURL]easyui/jquery.easyui.min.js"></script>',
                    '<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">',
                    '<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>'],
    },
}
