var OrgPrevPage = null;
var OrgNextPage = null;
var OrgHomePage = null;
var RemoveToKeepConfirmValue = null;
var RemoveValidatePromptValue = null;
let thisUrl = "" + window.location;
const isAxterCom = (thisUrl.search("axter.com") > -1);
console.log("Cookies = " + document.cookie);
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
    document.cookie = RemoveToKeepConfirmValue + "&" + RemoveValidatePromptValue + "; SameSite=None; Secure";
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
			else if (!chkBxRemoveValid.checked && Mode !== "flagScene") alert("Action " + Mode + " for scene(s) ID# " + ActionID + " complete.\\n\\nResults=" + result);
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
			if (isAxterCom)
				newUrl = newUrl.replace("/file.html", "/advance_options.html");
			else
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
