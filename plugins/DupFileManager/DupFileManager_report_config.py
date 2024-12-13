# Description: This is a Stash plugin which manages duplicate files.
# By David Maisonave (aka Axter) Jul-2024 (https://www.axter.com/)
# Get the latest developers version from following link:
# https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins/DupFileManager

# HTML Report Options **************************************************
report_config = {    
    # Paginate HTML report. Maximum number of results to display on one page, before adding (paginating) an additional page.
    "htmlReportPaginate" : 100,
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
ul {
  padding: 0;
}
li {
  list-style-type: none;
  padding: 1px;
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
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">

<link rel="stylesheet" type="text/css" href="https://axter.com/js/easyui/themes/black/easyui.css">
<link rel="stylesheet" type="text/css" href="https://axter.com/js/easyui/themes/icon.css">
<script type="text/javascript" src="https://axter.com/js/jquery-3.7.1.min.js"></script>
<script type="text/javascript" src="https://axter.com/js/easyui/jquery.easyui.min.js"></script>

<script src="https://www.axter.com/js/jquery.prompt.js"></script>
<link rel="stylesheet" href="https://www.axter.com/js/jquery.prompt.css"/>
<script>
var apiKey = "";
var GraphQl_URL = "http://localhost:9999/graphql";
var OrgPrevPage = null;
var OrgNextPage = null;
var OrgHomePage = null;
var RemoveToKeepConfirmValue = null;
var RemoveValidatePromptValue = null;
const StrRemoveToKeepConfirm = "RemoveToKeepConfirm=";
const StrRemoveValidatePrompt = "RemoveValidatePrompt=";
function SetPaginateButtonChange(){
    var chkBxRemoveValid = document.getElementById("RemoveValidatePrompt");
    var chkBxDisableDeleteConfirm = document.getElementById("RemoveToKeepConfirm");
    RemoveToKeepConfirmValue = StrRemoveToKeepConfirm + "false";
    RemoveValidatePromptValue = StrRemoveValidatePrompt + "false";
    if (chkBxRemoveValid.checked)
        RemoveToKeepConfirmValue = StrRemoveToKeepConfirm + "true";
    if (chkBxDisableDeleteConfirm.checked)
        RemoveValidatePromptValue = StrRemoveValidatePrompt + "true";
    document.cookie = RemoveToKeepConfirmValue + "&" + RemoveValidatePromptValue + ";";
    console.log("Cookies = " + document.cookie);
}
function trim(str, ch) {
    var start = 0, end = str.length;
    while(start < end && str[start] === ch) ++start;
    while(end > start && str[end - 1] === ch) --end;
    return (start > 0 || end < str.length) ? str.substring(start, end) : str;
}
function RunPluginOperation(Mode, ActionID, button, asyncAjax){ // Mode=Value and ActionID=id
	if (Mode == null || Mode === ""){
		console.log("Error: Mode is empty or null; ActionID = " + ActionID);
		return;
	}
	if (asyncAjax){
        $('html').addClass('wait');
        $("body").css("cursor", "progress");
    }
	var chkBxRemoveValid = document.getElementById("RemoveValidatePrompt");
    if (apiKey !== "")
        $.ajaxSetup({beforeSend: function(xhr) {xhr.setRequestHeader('apiKey', apiKey);}});    
    $.ajax({method: "POST", url: GraphQl_URL, contentType: "application/json", dataType: "text", cache: asyncAjax, async: asyncAjax,
	data: JSON.stringify({
			query: `mutation RunPluginOperation($plugin_id:ID!,$args:Map!){runPluginOperation(plugin_id:$plugin_id,args:$args)}`,
			variables: {"plugin_id": "DupFileManager", "args": { "Target" : ActionID, "mode":Mode}},
		}), success: function(result){
			console.log(result);
            if (asyncAjax){
                $('html').removeClass('wait');
                $("body").css("cursor", "default");
            }
            if (Mode.startsWith("copyScene") || Mode.startsWith("renameFile") || Mode === "clearAllSceneFlags" || Mode.startsWith("clearFlag") || Mode.startsWith("mergeScene") || Mode.startsWith("mergeTags") || (Mode !== "deleteScene" && Mode.startsWith("deleteScene")))
                window.location.reload();
			if (!chkBxRemoveValid.checked && Mode !== "flagScene") alert("Action " + Mode + " for scene(s) ID# " + ActionID + " complete.\\n\\nResults=" + result);
		}, error: function(XMLHttpRequest, textStatus, errorThrown) { 
			console.log("Ajax failed with Status: " + textStatus + "; Error: " + errorThrown); 
            if (asyncAjax){
                $('html').removeClass('wait');
                $("body").css("cursor", "default");
            }
		}  
	});
}
function GetStashTabUrl(Tab){
	var Url = GraphQl_URL;
	Url = Url.replace("graphql", "settings?tab=" + Tab);
	console.log("Url = " + Url);
	return Url;
}
function SetFlagOnScene(flagType, ActionID){
	if (flagType === "yellow highlight")
		$('.ID_' + ActionID).css('background','yellow');
	else if (flagType === "green highlight")
		$('.ID_' + ActionID).css('background','#00FF00');
	else if (flagType === "orange highlight")
		$('.ID_' + ActionID).css('background','orange');
	else if (flagType === "cyan highlight")
		$('.ID_' + ActionID).css('background','cyan');
	else if (flagType === "pink highlight")
		$('.ID_' + ActionID).css('background','pink');
	else if (flagType === "red highlight")
		$('.ID_' + ActionID).css('background','red');
	else if (flagType === "strike-through")
		$('.ID_' + ActionID).css('text-decoration', 'line-through');
	else if (flagType === "disable-scene")
		$('.ID_' + ActionID).css({ 'background' : 'gray', 'pointer-events' : 'none' });
	else if (flagType === "remove all flags")
		$('.ID_' + ActionID).removeAttr('style'); //.css({ 'background' : '', 'text-decoration' : '', 'pointer-events' : '' });
	else
		return false;
	return true;
}
function selectMarker(Mode, ActionID, button){
	$('<p>Select desire marker type <select><option>yellow highlight</option><option>green highlight</option><option>orange highlight</option><option>cyan highlight</option><option>pink highlight</option><option>red highlight</option><option>strike-through</option><option>disable-scene</option><option>remove all flags</option></select></p>').confirm(function(answer){
		if(answer.response){
            console.log("Selected " + $('select',this).val());
            var flagType = $('select',this).val();
            if (flagType == null){
                console.log("Invalid flagType");
                return;
            }
			if (!SetFlagOnScene(flagType, ActionID))
				return;
            ActionID = ActionID + ":" + flagType;
            console.log("ActionID = " + ActionID);
            RunPluginOperation(Mode, ActionID, button, false);
        }
        else console.log("Not valid response");
	});
}
$(document).ready(function(){
    OrgPrevPage = $("#PrevPage").attr('href');
    OrgNextPage = $("#NextPage").attr('href');
    OrgHomePage = $("#HomePage").attr('href');
    console.log("OrgNextPage = " + OrgNextPage);

    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    console.log("urlParams = " + urlParams);
    RemoveToKeepConfirmValue = StrRemoveToKeepConfirm + "false";
    RemoveValidatePromptValue = StrRemoveValidatePrompt + "false";
    var FetchCookies = true;
    if (urlParams.get('RemoveToKeepConfirm') != null && urlParams.get('RemoveToKeepConfirm') !== ""){
        FetchCookies = false;
        RemoveToKeepConfirmValue = StrRemoveToKeepConfirm + urlParams.get('RemoveToKeepConfirm');
        if (urlParams.get('RemoveToKeepConfirm') === "true")
            $( "#RemoveToKeepConfirm" ).prop("checked", true);
        else
            $( "#RemoveToKeepConfirm" ).prop("checked", false);
    }
    if (urlParams.get('RemoveValidatePrompt') != null && urlParams.get('RemoveValidatePrompt') !== ""){
        FetchCookies = false;
        RemoveValidatePromptValue = StrRemoveValidatePrompt + urlParams.get('RemoveValidatePrompt');
        console.log("RemoveValidatePromptValue = " + RemoveValidatePromptValue);
        if (urlParams.get('RemoveValidatePrompt') === "true")
            $( "#RemoveValidatePrompt" ).prop("checked", true);
        else
            $( "#RemoveValidatePrompt" ).prop("checked", false);
    }
    if (FetchCookies){
        console.log("Cookies = " + document.cookie);
        var cookies = document.cookie;
        if (cookies.indexOf(StrRemoveToKeepConfirm) > -1){
            var idx = cookies.indexOf(StrRemoveToKeepConfirm) + StrRemoveToKeepConfirm.length;
            var s = cookies.substring(idx);
            console.log("StrRemoveToKeepConfirm Cookie = " + s);
            if (s.startsWith("true"))
                $( "#RemoveToKeepConfirm" ).prop("checked", true);
            else
                $( "#RemoveToKeepConfirm" ).prop("checked", false);
        }
        if (cookies.indexOf(StrRemoveValidatePrompt) > -1){
            var idx = cookies.indexOf(StrRemoveValidatePrompt) + StrRemoveValidatePrompt.length;
            var s = cookies.substring(idx);
            console.log("StrRemoveValidatePrompt Cookie = " + s);
            if (s.startsWith("true"))
                $( "#RemoveValidatePrompt" ).prop("checked", true);
            else
                $( "#RemoveValidatePrompt" ).prop("checked", false);
        }
    }
    SetPaginateButtonChange();
    function ProcessClick(This_){
		if (This_ == null)
			return;
        const ID = This_.id;
		var Value = This_.getAttribute("value");
		if ((ID == null || ID === "") && (Value == null || Value === ""))
			return;
		if (Value == null) Value = "";		
        var Mode = Value;
        var ActionID = ID;
        console.log("Mode = " + Mode + "; ActionID =" + ActionID);
        if (Mode === "DoNothing")
            return;
        if (ActionID === "AdvanceMenu" || ActionID === "AdvanceMenu_")
        {
            var newUrl = window.location.href;
            newUrl = newUrl.replace(/report\/DuplicateTagScenes[_0-9]*.html/g, "advance_options.html?GQL=" + GraphQl_URL + "&apiKey=" + apiKey);
            window.open(newUrl, "_blank");
            return;
        }
        if (Mode.startsWith("deleteScene") || Mode === "removeScene"){
            var chkBxDisableDeleteConfirm = document.getElementById("RemoveToKeepConfirm");
            question = "Are you sure you want to delete this file and remove scene from stash?";
            if (Mode !== "deleteScene" && Mode.startsWith("deleteScene")) question = "Are you sure you want to delete all the flagged files and remove them from stash?";
            if (Mode === "removeScene") question = "Are you sure you want to remove scene from stash?";
            if (!chkBxDisableDeleteConfirm.checked && !confirm(question))
                return;
            if (Mode === "deleteScene" || Mode === "removeScene"){
                $('.ID_' + ActionID).css('background-color','gray');
                $('.ID_' + ActionID).css('pointer-events','none');
            }
        }
        else if (ID === "viewStashPlugin")
            window.open(GetStashTabUrl("plugins"), "_blank");
        else if (ID === "viewStashTools")
            window.open(GetStashTabUrl("tools"), "_blank");
        else if (Mode === "newName" || Mode === "renameFile"){
            var myArray = ActionID.split(":");
            var promptStr = "Enter new name for scene ID " + myArray[0] + ", or press escape to cancel.";
            if (Mode === "renameFile") 
                promptStr = "Press enter to rename scene ID " + myArray[0] + ", or press escape to cancel.";
            var newName=prompt(promptStr,trim(myArray[1], "'"));
            if (newName === null)
                return;
            ActionID = myArray[0] + ":" + newName;
            Mode = "renameFile";
        }
        else if (Mode === "flagScene"){
            selectMarker(Mode, ActionID, This_);
            return;
        }
        else if (Mode.startsWith("flagScene")){
            var flagType = Mode.substring(9);
            Mode = "flagScene";
            if (!SetFlagOnScene(flagType, ActionID))
                    return;
            ActionID = ActionID + ":" + flagType;
            console.log("ActionID = " + ActionID);
        }
        RunPluginOperation(Mode, ActionID, This_, true);
    }
    $("button").click(function(){
        ProcessClick(this);
    });
    $("a").click(function(){
        if (this.id.startsWith("btn_mnu"))
            return;
        if (this.id === "reload"){
			window.location.reload();
			return;
		}
        if (this.id === "PrevPage" || this.id === "NextPage" || this.id === "HomePage" || this.id === "PrevPage_Top" || this.id === "NextPage_Top" || this.id === "HomePage_Top"){
            return;
        }
        ProcessClick(this);
    });
    $("div").click(function(){
        if (this.id.startsWith("btn_mnu"))
            return;
        if (this.id === "reload"){
			window.location.reload();
			return;
		}
        ProcessClick(this);
    });
    $("#RemoveValidatePrompt").change(function() {
        console.log("checkbox clicked");
        SetPaginateButtonChange();
    });
    $("#RemoveToKeepConfirm").change(function() {
        SetPaginateButtonChange();
    });
});
</script>
</head>
<body>
<div  style="background-color:BackgroundColorPlaceHolder;color:TextColorPlaceHolder;">
<center><table style="color:darkgreen;background-color:powderblue;">
<tr><th>Report Info</th><th>Report Options</th></tr>
<tr>
<td><table><tr>
<td>Found (QtyPlaceHolder) duplice sets</td>
<td>Date Created: (DateCreatedPlaceHolder)</td>
</tr></table></td>
<td><table><tr>
<td>
	<div class="easyui-panel">
        <a id="btn_mnu" class="easyui-menubutton" menu="#btn_mnu1">Menu</a>
    </div>
    <div id="btn_mnu1">
        <div iconCls="icon-add" id="AdvanceMenu" title="Open [Advance Duplicate File Deletion Menu] on a new tab in the browser." name="AdvanceMenu">Advance Duplicate File Deletion Menu</div>
        <div iconCls="icon-reload" id="reload" title="Reload (refresh) this page." name="reload">Reload Page</div>
		<div iconCls="icon-menu1" id="viewStashPlugin" title="View Stash plugins menu.">Stash Plugins</div>
		<div iconCls="icon-menu-blue" id="viewStashTools" title="View Stash tools menu.">Stash Tools</div>
        <div iconCls="icon-more"><a href="https://github.com/David-Maisonave/Axter-Stash/tree/main/plugins" target="_blank" rel="noopener noreferrer">Axter-Stash Plugins</a></div>
        <div class="menu-sep"></div>
        <div iconCls="icon-merge" id="mergeMetadataForAll" value="mergeTags" title="Merge scene metadata from [Duplicate to Delete] to [Duplicate to Keep] for any [Duplicate to Keep] scene missing metadata that is in associated [Duplicate to Delete] scene. This action make take a few minutes to complete.">Merge Tags, Performers, and Galleries</button></div>
        <div iconCls="icon-no" id="clear_duplicate_tags_task" value="clear_duplicate_tags_task" title="Remove duplicate (_DuplicateMarkForDeletion_?) tag from all scenes. This action make take a few minutes to complete.">Clear Dup (_DuplicateMarkForDeletion_) Tags</button></div>
        <div class="menu-sep"></div>
        <div iconCls="icon-pink-x" id="fileNotExistToDelete" value="Tagged" title="Delete tagged duplicates for which file does NOT exist.">Delete Dup Tagged Files That do Not Exist</button></div>
        <div iconCls="icon-cancel" id="fileNotExistToDelete" value="Report" title="Delete duplicate candidate files in report for which file does NOT exist.">Delete Files That do Not Exist in Report</button></div>
        <div class="menu-sep"></div>
		<div iconCls="icon-cancel" title="Delete all [Duplicate to Delete] scenes flagged with selected flag.">
			<span>Delete Flagged Scenes</span>
			<div>
				<div iconCls="icon-cancel" title="Delete all [Duplicate to Delete] cyan flagged scenes in report." value="deleteSceneCyanFlag" id="cyan" style="background-color:cyan;color:black;"	        >Delete All Cyan Flagged Scenes</button></div>
                <div iconCls="icon-cancel" title="Delete all [Duplicate to Delete] green flagged scenes in report." value="deleteSceneGreenFlag" id="green" style="background-color:#00FF00;color:black;"   >Delete All Green Flagged Scenes</button></div>
				<div iconCls="icon-cancel" title="Delete all [Duplicate to Delete] orange flagged scenes in report." value="deleteSceneOrangeFlag" id="orange" style="background-color:orange;color:black;" >Delete All Orange Flagged Scenes</button></div>
				<div iconCls="icon-cancel" title="Delete all [Duplicate to Delete] yellow flagged scenes in report." value="deleteSceneYellowFlag" id="yellow" style="background-color:yellow;color:black;" >Delete All Yellow Flagged Scenes</button></div>
				<div iconCls="icon-cancel" title="Delete all [Duplicate to Delete] pink flagged scenes in report." value="deleteScenePinkFlag" id="pink" style="background-color:pink;color:black;"		    >Delete All Pink Flagged Scenes</button></div>
				<div iconCls="icon-cancel" title="Delete all [Duplicate to Delete] red flagged scenes in report." value="deleteSceneRedFlag" id="red" style="background-color:red;color:white;"			    >Delete All Red Flagged Scenes</button></div>
			</div>
		</div>
		<div iconCls="icon-copy" title="Copy the file from [Duplicate to Delete] to [Duplicate to Keep] for all [Duplicate to Delete] flagged scenes.">
			<span>Copy Flagged Scenes</span>
			<div>
				<div iconCls="icon-copy-clear" title="Copy all cyan flagged scenes in report." value="copySceneCyanFlag" id="cyan" style="background-color:cyan;color:black;"				>Copy All Cyan Flagged Scenes</button></div>
				<div iconCls="icon-copy-clear" title="Copy all green flagged scenes in report." value="copySceneGreenFlag" id="green" style="background-color:#00FF00;color:black;"		    >Copy All Green Flagged Scenes</button></div>
				<div iconCls="icon-copy-clear" title="Copy all orange flagged scenes in report." value="copySceneOrangeFlag" id="orange" style="background-color:orange;color:black;"		>Copy All Orange Flagged Scenes</button></div>
				<div iconCls="icon-copy-clear" title="Copy all yellow flagged scenes in report." value="copySceneYellowFlag" id="yellow" style="background-color:yellow;color:black;"		>Copy All Yellow Flagged Scenes</button></div>
				<div iconCls="icon-copy-clear" title="Copy all pink flagged scenes in report." value="copyScenePinkFlag" id="pink" style="background-color:pink;color:black;"				>Copy All Pink Flagged Scenes</button></div>
				<div iconCls="icon-copy-clear" title="Copy all red flagged scenes in report." value="copySceneRedFlag" id="red" style="background-color:red;color:white;"					>Copy All Red Flagged Scenes</button></div>
			</div>
		</div>
		<div iconCls="icon-documents" title="Copy the file and metadata (Tags, Performers, & Galleries) from [Duplicate to Delete] to [Duplicate to Keep] for all [Duplicate to Delete] flagged scenes.">
			<span>Move Flagged Scenes</span>
			<div>
				<div iconCls="icon-documents" title="Move all cyan flagged scenes in report." value="moveSceneCyanFlag" id="cyan" style="background-color:cyan;color:black;"				>Move All Cyan Flagged Scenes</button></div>
				<div iconCls="icon-documents" title="Move all green flagged scenes in report." value="moveSceneGreenFlag" id="green" style="background-color:#00FF00;color:black;"		    >Move All Green Flagged Scenes</button></div>
				<div iconCls="icon-documents" title="Move all orange flagged scenes in report." value="moveSceneOrangeFlag" id="orange" style="background-color:orange;color:black;"		>Move All Orange Flagged Scenes</button></div>
				<div iconCls="icon-documents" title="Move all yellow flagged scenes in report." value="moveSceneYellowFlag" id="yellow" style="background-color:yellow;color:black;"		>Move All Yellow Flagged Scenes</button></div>
				<div iconCls="icon-documents" title="Move all pink flagged scenes in report." value="moveScenePinkFlag" id="pink" style="background-color:pink;color:black;"				>Move All Pink Flagged Scenes</button></div>
				<div iconCls="icon-documents" title="Move all red flagged scenes in report." value="moveSceneRedFlag" id="red" style="background-color:red;color:white;"					>Move All Red Flagged Scenes</button></div>
			</div>
		</div>
		<div iconCls="icon-merge" title="Merge scene metadata from [Duplicate to Delete] to [Duplicate to Keep] for all [Duplicate to Delete] flagged scenes. This action make take a few minutes to complete.">
			<span>Merge (Tags, Performers, & Galleries) Flagged Scenes</span>
			<div>
				<div iconCls="icon-merge" title="Merge all cyan flagged scenes in report." value="mergeSceneCyanFlag" id="cyan" style="background-color:cyan;color:black;"				>Merge All Cyan Flagged Scenes</button></div>
				<div iconCls="icon-merge" title="Merge all green flagged scenes in report." value="mergeSceneGreenFlag" id="green" style="background-color:#00FF00;color:black;"		>Merge All Green Flagged Scenes</button></div>
				<div iconCls="icon-merge" title="Merge all orange flagged scenes in report." value="mergeSceneOrangeFlag" id="orange" style="background-color:orange;color:black;"		>Merge All Orange Flagged Scenes</button></div>
				<div iconCls="icon-merge" title="Merge all yellow flagged scenes in report." value="mergeSceneYellowFlag" id="yellow" style="background-color:yellow;color:black;"		>Merge All Yellow Flagged Scenes</button></div>
				<div iconCls="icon-merge" title="Merge all pink flagged scenes in report." value="mergeScenePinkFlag" id="pink" style="background-color:pink;color:black;"				>Merge All Pink Flagged Scenes</button></div>
				<div iconCls="icon-merge" title="Merge all red flagged scenes in report." value="mergeSceneRedFlag" id="red" style="background-color:red;color:white;"					>Merge All Red Flagged Scenes</button></div>
			</div>
		</div>
		<div iconCls="icon-lock" title="Add special tag [_ExcludeDuplicateMarkForDeletion] for [Duplicate to Delete] scenes flagged with selected flag.">
			<span>Add Exclude TAG to Flagged Scenes</span>
			<div>
				<div iconCls="icon-lock" title="Add Exclude TAG to all [Duplicate to Delete] cyan flagged scenes in report." value="addExcludeTagCyanFlag" id="cyan" style="background-color:cyan;color:black;"				>Add Exclude TAG to Cyan Flagged Scenes</button></div>
				<div iconCls="icon-lock" title="Add Exclude TAG to all [Duplicate to Delete] green flagged scenes in report." value="addExcludeTagGreenFlag" id="green" style="background-color:#00FF00;color:black;"		>Add Exclude TAG to Green Flagged Scenes</button></div>
				<div iconCls="icon-lock" title="Add Exclude TAG to all [Duplicate to Delete] orange flagged scenes in report." value="addExcludeTagOrangeFlag" id="orange" style="background-color:orange;color:black;"		>Add Exclude TAG to Orange Flagged Scenes</button></div>
				<div iconCls="icon-lock" title="Add Exclude TAG to all [Duplicate to Delete] yellow flagged scenes in report." value="addExcludeTagYellowFlag" id="yellow" style="background-color:yellow;color:black;"		>Add Exclude TAG to Yellow Flagged Scenes</button></div>
				<div iconCls="icon-lock" title="Add Exclude TAG to all [Duplicate to Delete] pink flagged scenes in report." value="addExcludeTagPinkFlag" id="pink" style="background-color:pink;color:black;"				>Add Exclude TAG to Pink Flagged Scenes</button></div>
				<div iconCls="icon-lock" title="Add Exclude TAG to all [Duplicate to Delete] red flagged scenes in report." value="addExcludeTagRedFlag" id="red" style="background-color:red;color:white;"					>Add Exclude TAG to Red Flagged Scenes</button></div>
			</div>
		</div>
        <div class="menu-sep"></div>
		<div iconCls="icon-eraser-minus" id="clearAllSceneFlags" value="clearAllSceneFlags" title="Remove all flags from report for all scenes, except for deletion flag.">Clear All Flags from All Scenes</button></div>
		<div iconCls="icon-eraser-minus" class="easyui-tooltip" title="Clear specific flag from all scenes.">
			<span>Clear Flag from All Scenes</span>
			<div>
				<div iconCls="icon-eraser-minus" title="Clear flag cyan from all scenes." value="clearFlagCyanFlag" id="cyan" style="background-color:cyan;color:black;"				>Clear Cyan</button></div>
				<div iconCls="icon-eraser-minus" title="Clear flag green from all scenes." value="clearFlagGreenFlag" id="green" style="background-color:#00FF00;color:black;"		    >Clear Green</button></div>
				<div iconCls="icon-eraser-minus" title="Clear flag orange from all scenes." value="clearFlagOrangeFlag" id="orange" style="background-color:orange;color:black;"		>Clear Orange</button></div>
				<div iconCls="icon-eraser-minus" title="Clear flag yellow from all scenes." value="clearFlagYellowFlag" id="yellow" style="background-color:yellow;color:black;"		>Clear Yellow</button></div>
				<div iconCls="icon-eraser-minus" title="Clear flag pink from all scenes." value="clearFlagPinkFlag" id="pink" style="background-color:pink;color:black;"				>Clear Pink</button></div>
				<div iconCls="icon-eraser-minus" title="Clear flag red from all scenes." value="clearFlagRedFlag" id="red" style="background-color:red;color:white;"					>Clear Red</button></div>
			</div>
		</div>
    </div>
</td>
<td><input type="checkbox" id="RemoveValidatePrompt" name="RemoveValidatePrompt"><label for="RemoveValidatePrompt" title="Disable notice for task completion (Popup).">Disable Complete Confirmation</label><br></td>
<td><input type="checkbox" id="RemoveToKeepConfirm" name="RemoveToKeepConfirm"><label for="RemoveToKeepConfirm" title="Disable confirmation prompts for delete scenes">Disable Delete Confirmation</label><br></td>

</tr></table></td>
</tr></table></center>
<h2>Stash Duplicate Scenes Report (MatchTypePlaceHolder)</h2>\n""",
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
    # If enabled, create an HTML report when tagging duplicate files
    "createHtmlReport" : True,
}
