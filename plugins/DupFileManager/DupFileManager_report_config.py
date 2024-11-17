# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link:
# https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager

# HTML Report Options **************************************************
report_config = {    
    # If enabled, create an HTML report when tagging duplicate files
    "createHtmlReport" : True,
    # If enabled, report displays stream instead of preview for video
    "streamOverPreview" : False, # This option works in Chrome, but does not work very well on firefox.
    # If enabled, report displays an image preview similar to sceneDuplicateChecker
    "htmlIncludeImagePreview" : False,
    "htmlImagePreviewPopupSize" : 600,
    # Name of the HTML file to create
    "htmlReportName" : "DuplicateTagScenes.html",
    # HTML report prefix, before table listing
    "htmlReportPrefix" : """<!DOCTYPE html>
<html>
<head>
<title>Stash Duplicate Report</title>
<style>
h2 {text-align: center;}
table, th, td {border:1px solid black;}
.inline {
  display: inline;
}
.scene-details{text-align: center;font-size: small;}
.reason-details{text-align: left;font-size: small;}
.link-items{text-align: center;font-size: small;}
.link-button {
  background: none;
  border: none;
  color: blue;
  text-decoration: underline;
  cursor: pointer;
  font-size: 1em;
  font-family: serif;
  text-align: center;
  font-size: small;
}
.link-button:focus {
  outline: none;
}
.link-button:active {
  color:red;
}
ul {
  display: flex;
}

li {
  list-style-type: none;
  padding: 10px;
  position: relative;
}
.large {
  position: absolute;
  left: -9999px;
}
li:hover .large {
  left: 20px;
  top: -150px;
}
.large-image {
  border-radius: 4px;
   box-shadow: 1px 1px 3px 3px rgba(127, 127, 127, 0.15);;
}
</style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script>
function RunPluginDupFileManager(Mode, ActionID, button) {
	chkBxRemoveValid = document.getElementById("RemoveValidatePrompt");
	if (Mode === "deleteScene"){
		chkBxDisableDeleteConfirm = document.getElementById("RemoveToKeepConfirm");
		if (!chkBxDisableDeleteConfirm.checked && !confirm("Are you sure you want to delete this file and remove scene from stash?")) {
				return;
	}
	else if (Mode === "newName"){
	    var myArray = ActionID.split(":");
	    var newName=prompt("Enter new name, or press escape to cancel.",myArray[1]);
	    if (newName === null)
	        return;
	    ActionID = myArray[0] + ":" + newName;
	    Mode = "renameFile";
    }
	$.ajax({method: "POST", url: "http://localhost:9999/graphql", contentType: "application/json", dataType: "text",
	data: JSON.stringify({
			query: `mutation RunPluginOperation($plugin_id:ID!,$args:Map!){runPluginOperation(plugin_id:$plugin_id,args:$args)}`,
			variables: {"plugin_id": "DupFileManager", "args": { "Target" : ActionID, "mode":Mode}},
		}), success: function(result){
			console.log(result);
			button.style.visibility = 'hidden';
			if (Mode === "deleteScene" || Mode === "removeScene")
			    $('.ID_' + ActionID).css('display','none');
			if (!chkBxRemoveValid.checked) alert("Action " + Mode + " for scene(s) ID# " + ActionID + " complete.");
	}});
}    
$(document).ready(function(){
  $("button").click(function(){
	if (this.id === "AdvanceMenu")
    {
		var newUrl = window.location.href;
		newUrl = newUrl.replace(/report\/DuplicateTagScenes[_0-9]*.html/g, "advance_options.html?GQL=http://localhost:9999/graphql");
		window.open(newUrl, "_blank");
    }
	else
		RunPluginDupFileManager(this.value, this.id, this)
  });
});
</script>
</head>
<body>
<center><table style="color:darkgreen;background-color:powderblue;">
<tr><th>Report Info</th><th>Report Options</th></tr>
<tr>
<td><table><tr>
<td>Found (QtyPlaceHolder) duplice sets</td>
<td>Date Created: (DateCreatedPlaceHolder)</td>
</tr></table></td>
<td><table><tr>
<td><input type="checkbox" id="RemoveValidatePrompt" name="RemoveValidatePrompt"><label for="RemoveValidatePrompt" title="Disable Validate Prompts (Popups)">Disable Task Prompt</label><br></td>
<td><input type="checkbox" id="RemoveToKeepConfirm" name="RemoveToKeepConfirm"><label for="RemoveToKeepConfirm" title="Disable confirmation prompts for delete scenes">Disable Delete Confirmation</label><br></td>
<td><button id="AdvanceMenu" title="View advance menu for tagged duplicates." name="AdvanceMenu">Advance Tag Menu</button></td>
</tr></table></td>
</tr></table></center>
<h2>Stash Duplicate Scenes Report (MatchTypePlaceHolder)</h2>\n""",
    # HTML report postfiox, after table listing
    "htmlReportPostfix" : "\n</body></html>",
    # HTML report table
    "htmlReportTable" : "<table style=\"width:100%\">",
    # HTML report table row
    "htmlReportTableRow" : "<tr>",
    # HTML report table header
    "htmlReportTableHeader" : "<th>",
    # HTML report table data
    "htmlReportTableData" : "<td>",
     # HTML report video preview
    "htmlReportVideoPreview" : "width='160' height='120' controls", # Alternative option "autoplay loop controls" or "autoplay controls"
    # The number off seconds in time difference for supper highlight on htmlReport
    "htmlHighlightTimeDiff" : 3,
    # Supper highlight for details with higher resolution or duration
    "htmlSupperHighlight" : "yellow",
    # Lower highlight for details with slightly higher duration
    "htmlLowerHighlight" : "nyanza",
    # Text color for details with different resolution, duration, size, bitrate,codec, or framerate
    "htmlDetailDiffTextColor" : "red",
    # Paginate HTML report. Maximum number of results to display on one page, before adding (paginating) an additional page.
    "htmlReportPaginate" : 100,
}