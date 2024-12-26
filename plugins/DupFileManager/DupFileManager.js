(function () {
	const isChrome = !!window.chrome;
	const PluginApi = window.PluginApi;
    const React = PluginApi.React;
	const { Component } = PluginApi.React;
    const GQL = PluginApi.GQL;
    const { Button } = PluginApi.libraries.Bootstrap;
    const { Link, NavLink } = PluginApi.libraries.ReactRouterDOM;
	class StashPlugin {
		#urlParams 	= new URLSearchParams(window.location.search);
		#apiKey		= "";
		#doApiLog	= true;
		constructor(PluginID, doApiLog = true, DataType = "json", Async = false) {
			this.#doApiLog 	= doApiLog;
			this.PluginID 	= PluginID;
			this.DataType 	= DataType;
			this.Async 		= Async;
			this.#apiKey = this.getParam("apiKey"); // For Stash installations with a password setup, populate this variable with the apiKey found in Stash->Settings->Security->[API Key];   	----- Or pass in the apiKey at the URL command line. Example: advance_options.html?apiKey=12345G4igiJdgssdgiwqInh5cCI6IkprewJ9hgdsfhgfdhd&GQL=http://localhost:9999/graphql
			this.GraphQl_URL = this.getParam("GQL", "http://localhost:9999/graphql");// For Stash installations with non-standard ports or URL's, populate this variable with actual URL;   	----- Or pass in the URL at the command line using GQL param. Example: advance_options.html?GQL=http://localhost:9900/graphql
			console.log("GQL = " + this.GraphQl_URL + "; apiKey = " + this.#apiKey + "; urlParams = " + this.#urlParams + "; Cookies = " + document.cookie);
		}
		getParam(ParamName, DefaultValue = ""){
			if (this.#urlParams.get(ParamName) != null && this.#urlParams.get(ParamName) !== "")
				return this.#urlParams.get(ParamName);
			return DefaultValue;
		}
		CallBackOnSuccess(result, Args, This){ // Only called on asynchronous calls
			console.log("Ajax success."); 
		}
		CallBackOnFail(textStatus, errorThrown, This){
			console.log("Ajax failed with Status: " + textStatus + "; Error: " + errorThrown); 
			alert("Error on StashPlugin Ajax call!!!\nReturn-Status: " + textStatus + "\nThrow-Error: " + errorThrown);
		}
		RunPluginOperation(Args = {}, OnSuccess = this.CallBackOnSuccess, OnFail = this.CallBackOnFail) {
			console.log("PluginID = " + this.PluginID + "; Args = " + Args + "; GQL = " + this.GraphQl_URL + "; DataType = " + this.DataType + "; Async = " + this.Async);
			if (this.#apiKey !== ""){
				if (this.#doApiLog) console.log("Using apiKey = " + this.#apiKey);
				const apiKey = this.#apiKey;
				$.ajaxSetup({beforeSend: function(xhr) {xhr.setRequestHeader('apiKey', apiKey);}});
			}
			const AjaxData = $.ajax({method: "POST", url: this.GraphQl_URL, contentType: "application/json", dataType: this.DataType, cache: this.Async, async: this.Async,
			data: JSON.stringify({
					query: `mutation RunPluginOperation($plugin_id:ID!,$args:Map!){runPluginOperation(plugin_id:$plugin_id,args:$args)}`,
					variables: {"plugin_id": this.PluginID, "args": Args},
				}), success: function(result){
					if (this.Async == true) OnSuccess(result, Args, this); 
				}, error: function(jqXHR, textStatus, errorThrown) { 
					OnFail(textStatus, errorThrown, this);
				}
			});
			if (this.Async == true) // Make sure to use callback functions for asynchronous calls.
				return;
			if (this.DataType == "text")
				return AjaxData.responseText;
			return AjaxData.responseJSON.data.runPluginOperation;
		}
	};
	class Plugin_DupFileManager extends StashPlugin{
		constructor() {
			super("DupFileManager", "json", true);
			this.IS_DOCKER = this.getParam("IS_DOCKER") === "True";
			this.PageNo = parseInt(this.getParam("PageNo", "0"));
		}
		MyCallBackOnSuccess(result, Args, This){ // Only called on asynchronous calls
			console.log("Ajax success."); 
			$( "#FileDiv" ).append( result );
		}
		GetFile(Mode = "getReport") {
			this.RunPluginOperation({ "Target" : this.PageNo, "mode":Mode}, this.MyCallBackOnSuccess);
			return;
			//const strResults = JSON.stringify(results);
			//if (strResults.indexOf("INF: 'Error: Nothing to do!!!") > -1){
			//	console.log("Ajax failed for function " + Mode +" and page " + this.PageNo + " with results = " + JSON.stringify(results)); 
			//	return "<p>Failed to get report do to ajax error!!!</p>";
			//}
			//var rootPath = window.location.href;
			//if (rootPath.indexOf("://localhost:") > 0){
			//	results = results.replaceAll("://127.0.0.1:", "://localhost:");
			//} else if (rootPath.indexOf("://127.0.0.1:") > 0){
			//	results = results.replaceAll("://localhost:", "//127.0.0.1:");
			//}
			//return results;
		}
	}
	var PluginDupFileManager = new Plugin_DupFileManager();
	var rootPath = window.location.href;
	var myArray = rootPath.split("/");
	rootPath = myArray[0] + "//" + myArray[2]
	console.log("rootPath = " + rootPath);
	function RunPluginDupFileManager(Mode, DataType = "text", Async = false, ActionID = 0) {
		const AjaxData = $.ajax({method: "POST", url: "/graphql", contentType: "application/json",  dataType: DataType, cache: Async, async: Async,
		data: JSON.stringify({
				query: `mutation RunPluginOperation($plugin_id:ID!,$args:Map!){runPluginOperation(plugin_id:$plugin_id,args:$args)}`,
				variables: {"plugin_id": "DupFileManager", "args": { "Target" : ActionID, "mode":Mode}},
			}), success: function(result){
				if (DataType == "text"){
					console.log("result=" + result);
					return result;
				}
				console.log("JSON result=" + JSON.stringify(result));
				return result;
			}
		});
		if (Async == true)
			return true;
		if (DataType == "text")
		{
			console.log(AjaxData.responseText);
			return AjaxData.responseText;
		}
		JsonStr = AjaxData.responseJSON.data.runPluginOperation.replaceAll("'", "\"");
		console.log("JSON runPluginOperation = " + JsonStr);
		return JSON.parse(JsonStr);
	}
	var LocalDupReportExist = false;
	var AdvanceMenuOptionUrl  = "";
	var apiKey  = "";
	var UrlParam = "";
	var IS_DOCKER = "";
	var remoteReportDirURL = "";
	function GetLocalDuplicateReportPath(){
		var LocalDuplicateReport = RunPluginDupFileManager("getLocalDupReportPath", "json");
		console.log("LocalDuplicateReport=" + JSON.stringify(LocalDuplicateReport));
		remoteReportDirURL = LocalDuplicateReport.remoteReportDirURL;
		apiKey = LocalDuplicateReport.apiKey;
		IS_DOCKER = LocalDuplicateReport.IS_DOCKER;
		UrlParam = "?GQL=" + rootPath + "/graphql&IS_DOCKER=" + IS_DOCKER + "&apiKey=" + apiKey;
		var LocalDuplicateReportPath = remoteReportDirURL + "file.html" + UrlParam; //"file://" + LocalDuplicateReport.Path;
		AdvanceMenuOptionUrl = LocalDuplicateReport.AdvMenuUrl + UrlParam;
		console.log("AdvanceMenuOptionUrl=" + AdvanceMenuOptionUrl);
		LocalDupReportExist = LocalDuplicateReport.LocalDupReportExist;
		return LocalDuplicateReportPath;
	}
	// ToolTip text
	const CreateReportButtonToolTip = "Tag duplicate files, and create a new duplicate file report listing all duplicate files and using existing DupFileManager plugin options selected.";
	const CreateReportNoTagButtonToolTip = "Create a new duplicate file report listing all duplicate files and using existing DupFileManager plugin options selected. Do NOT tag files.";
	const ToolsMenuToolTip = "Show DupFileManager advance menu, which list additional tools and utilities.";
	const ShowReportButtonToolTip 	= "Open link to the duplicate file (HTML) report created in local path.";
	const ShowReportChromeHeader  	= "The following is the link to the duplicate file report.";
	const ChromeNotice 				= "Note: By default, Chrome and Edge browsers do not support local file links from non-local links. There for in order to open the link(s), the user must copy and paste the listed URL's to the browser address field manually. If this is not a Chrome [based] browser, than click on the links. If this is a Chrome [based] browser, right click the link and select 'Copy link'. Then pasted it on the address field.";
	const ReportMenuButtonToolTip 	= "Main report menu for DupFileManager. Create and show duplicate files on an HTML report.";
	// Buttons
	const DupFileManagerReportMenuButton 	= React.createElement(Link, { to: "/DupFileManager", title: ReportMenuButtonToolTip }, React.createElement(Button, null, "DupFileManager Report Menu"));
	const ToolsMenuOptionButton 			= React.createElement(Link, { to: "/DupFileManager_ToolsAndUtilities", title: ToolsMenuToolTip }, React.createElement(Button, null, "DupFileManager Tools and Utilities"));
	function GetShowReportButton(LocalDuplicateReportPath, ButtonText)
	{
		if (isChrome)
			return React.createElement("div", null, 
					React.createElement("div", {style:{"background-color":"yellow", color:"red"}}, ChromeNotice),
					React.createElement("h5", null, ShowReportChromeHeader),
					React.createElement("a", {href: LocalDuplicateReportPath, style:{color:"pink"}, title: ShowReportButtonToolTip, target:"_blank"}, LocalDuplicateReportPath));
		return React.createElement("a", { href: LocalDuplicateReportPath, title: ShowReportButtonToolTip, target:"_blank"}, React.createElement(Button, null, ButtonText));
	}
	function GetAdvanceMenuButton()
	{
		return React.createElement("a", { href: remoteReportDirURL + "advance_options.html" + UrlParam, title: "Open link to the [Advance Duplicate File Menu].", target:"_blank"}, React.createElement(Button, null, "Advance Duplicate File Menu"));
		// The following does not work with Chrome, or with an apiKey, or with a non-standard Stash URL.
		//return React.createElement("a", { href: AdvanceMenuOptionUrl, title: "Open link to the [Advance Duplicate File Menu].", target:"_blank"}, React.createElement(Button, null, "Show [Advance Duplicate File Menu]"));
	}
	function GetCreateReportNoTagButton(ButtonText){return React.createElement(Link, { to: "/DupFileManager_CreateReportWithNoTagging", title: CreateReportNoTagButtonToolTip }, React.createElement(Button, null, ButtonText));}
	function GetCreateReportButton(ButtonText){return React.createElement(Link, { to: "/DupFileManager_CreateReport", title: CreateReportButtonToolTip }, React.createElement(Button, null, ButtonText));}
	
	const { LoadingIndicator, } = PluginApi.components;
    const HomePage = () => {
		var LocalDuplicateReportPath = GetLocalDuplicateReportPath();
		console.log(LocalDupReportExist);
		var MyHeader = React.createElement("h1", null, "DupFileManager Report Menu");
		if (LocalDupReportExist)
			return (React.createElement("center", null,
					MyHeader,
					GetShowReportButton(LocalDuplicateReportPath, "Show Duplicate-File Report"),
					React.createElement("p", null),
					GetAdvanceMenuButton(),
					React.createElement("p", null),
					GetCreateReportNoTagButton("Create New Report (NO Tagging)"),
					React.createElement("p", null),
					GetCreateReportButton("Create New Report with Tagging"),
					React.createElement("p", null),
					ToolsMenuOptionButton
				));
		return (React.createElement("center", null,
				MyHeader,
				GetCreateReportNoTagButton("Create Duplicate-File Report (NO Tagging)"),
				React.createElement("p", null),
				GetCreateReportButton("Create Duplicate-File Report with Tagging"),
				React.createElement("p", null),
				GetAdvanceMenuButton(),
				React.createElement("p", null),
				ToolsMenuOptionButton
			));
    };
    const CreateReport = () => {
		const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
		if (componentsLoading)
			return (React.createElement(LoadingIndicator, {message: "Running task to create report. This may take a while. Please standby."}));
		RunPluginDupFileManager("tag_duplicates_task");
		return (React.createElement("center", null,
			React.createElement("h1", null, "Report complete. Click [Show Report] to view report."),
			GetShowReportButton(GetLocalDuplicateReportPath(), "Show Report"),
			React.createElement("p", null),
			GetAdvanceMenuButton(),
			React.createElement("p", null), DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
			));
    };	
    const CreateReportWithNoTagging = () => {
		const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
		if (componentsLoading)
			return (React.createElement(LoadingIndicator, {message: "Running task to create report. Please standby."}));
		RunPluginDupFileManager("createDuplicateReportWithoutTagging");
		return (React.createElement("center", null,
			React.createElement("h1", null, "Created HTML report without tagging. Click [Show Report] to view report."),
			GetShowReportButton(GetLocalDuplicateReportPath(), "Show Report"),
			React.createElement("p", null),
			GetAdvanceMenuButton(),
			React.createElement("p", null), DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
			));
    };	
    const ToolsAndUtilities = () => {
		return (React.createElement("center", null,
			React.createElement("h1", null, "DupFileManager Tools and Utilities"),
			React.createElement("p", null),
			
			React.createElement("h3", {class:"submenu"}, "Report Options"),
			React.createElement("p", null),
			GetCreateReportNoTagButton("Create Report (NO Tagging)"),
			React.createElement("p", null),
			GetCreateReportButton("Create Report (Tagging)"),
			React.createElement("p", null),
			DupFileManagerReportMenuButton,
			React.createElement("p", null),
			GetShowReportButton(GetLocalDuplicateReportPath(), "Show Duplicate-File Report"),
			React.createElement("p", null),
			React.createElement(Link, { to: "/DupFileManager_deleteLocalDupReportHtmlFiles", title: "Delete local HTML duplicate file report." }, React.createElement(Button, null, "Delete Duplicate-File Report HTML Files")),
			React.createElement("hr", {class:"dotted"}),

			React.createElement("h3", {class:"submenu"}, "Tagged Duplicates Options"),
			React.createElement("p", null),
			GetAdvanceMenuButton(),
			React.createElement("p", null),
			React.createElement(Link, { to: "/DupFileManager_deleteTaggedDuplicatesTask", title: "Delete scenes previously given duplicate tag (_DuplicateMarkForDeletion)." }, React.createElement(Button, null, "Delete Tagged Duplicates")),
			React.createElement("p", null),
			React.createElement(Link, { to: "/DupFileManager_deleteBlackListTaggedDuplicatesTask", title: "Delete scenes only in blacklist which where previously given duplicate tag (_DuplicateMarkForDeletion)." }, React.createElement(Button, null, "Delete Tagged Duplicates in Blacklist Only")),
			React.createElement("p", null),
			React.createElement(Link, { to: "/DupFileManager_deleteTaggedDuplicatesLwrResOrLwrDuration", title: "Delete scenes previously given duplicate tag (_DuplicateMarkForDeletion) and lower resultion or duration compare to primary (ToKeep) duplicate." }, React.createElement(Button, null, "Delete Low Res/Dur Tagged Duplicates")),
			React.createElement("p", null),
			React.createElement(Link, { to: "/DupFileManager_deleteBlackListTaggedDuplicatesLwrResOrLwrDuration", title: "Delete scenes only in blacklist which where previously given duplicate tag (_DuplicateMarkForDeletion) and lower resultion or duration compare to primary (ToKeep) duplicate." }, React.createElement(Button, null, "Delete Low Res/Dur Tagged Duplicates in Blacklist Only")),
			React.createElement("p", null),
			React.createElement("hr", {class:"dotted"}),

			React.createElement("h3", {class:"submenu"}, "Tagged Management Options"),
			React.createElement("p", null),
			React.createElement(Link, { to: "/DupFileManager_ClearAllDuplicateTags", title: "Remove duplicate tag from all scenes. This task may take some time to complete." }, React.createElement(Button, null, "Clear All Duplicate Tags")),
			React.createElement("p", null),
			React.createElement(Link, { to: "/DupFileManager_deleteAllDupFileManagerTags", title: "Delete all DupFileManager tags from stash." }, React.createElement(Button, null, "Delete All DupFileManager Tags")),
			React.createElement("p", null),
			React.createElement(Link, { to: "/DupFileManager_tagGrayList", title: "Set tag _GraylistMarkForDeletion to scenes having DuplicateMarkForDeletion tag and that are in the Graylist." }, React.createElement(Button, null, "Tag Graylist")),
			React.createElement("hr", {class:"dotted"}),

			React.createElement("h3", {class:"submenu"}, "Miscellaneous Options"),
			React.createElement(Link, { to: "/DupFileManager_generatePHASH_Matching", title: "Generate PHASH (Perceptual hashes) matching. Used for file comparisons." }, React.createElement(Button, null, "Generate PHASH (Perceptual hashes) Matching")),
			React.createElement("p", null),
			React.createElement("p", null),
			React.createElement("p", null),
			React.createElement("p", null),
			));
    };	
    const ClearAllDuplicateTags = () => {
		const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
		if (componentsLoading)
			return (React.createElement(LoadingIndicator, {message: "Running clear duplicate tags in background. This may take a while. Please standby."}));
		RunPluginDupFileManager("clear_duplicate_tags_task");
		return (React.createElement("div", null,
			React.createElement("h1", null, "Removed duplicate tags from all scenes."),
			DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
			));
    };	
    const deleteLocalDupReportHtmlFiles = () => {
		const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
		if (componentsLoading)
			return (React.createElement(LoadingIndicator, {message: "Running task to delete HTML files. Please standby."}));
		RunPluginDupFileManager("deleteLocalDupReportHtmlFiles");
		return (React.createElement("div", null,
			React.createElement("h2", null, "Deleted the HTML duplicate file report from local files."),
			DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
			));
    };	
    const deleteAllDupFileManagerTags = () => {
		const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
		if (componentsLoading)
			return (React.createElement(LoadingIndicator, {message: "Running task to delete all DupFileManager tags in background. This may take a while. Please standby."}));
		RunPluginDupFileManager("deleteAllDupFileManagerTags");
		return (React.createElement("div", null,
			React.createElement("h1", null, "Deleted all DupFileManager tags."),
			DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
			));
    };	
    const generatePHASH_Matching = () => {
		const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
		if (componentsLoading)
			return (React.createElement(LoadingIndicator, {message: "Running task generate PHASH (Perceptual hashes) matching in background. This may take a while. Please standby."}));
		RunPluginDupFileManager("generate_phash_task");
		return (React.createElement("div", null,
			React.createElement("h1", null, "PHASH (Perceptual hashes) complete."),
			DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
			));
    };	
    const tagGrayList = () => {
		const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
		if (componentsLoading)
			return (React.createElement(LoadingIndicator, {message: "Running task to tag _GraylistMarkForDeletion to scenes having DuplicateMarkForDeletion tag and that are in the Graylist. This may take a while. Please standby."}));
		RunPluginDupFileManager("graylist_tag_task");
		return (React.createElement("div", null,
			React.createElement("h1", null, "Gray list tagging complete."),
			DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
			));
    };	
    const deleteTaggedDuplicatesTask = () => {
		let result = confirm("Are you sure you want to delete all scenes having _DuplicateMarkForDeletion tags? This will delete the files, and remove them from stash.");
		if (result)
		{
			const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
			if (componentsLoading)
				return (React.createElement(LoadingIndicator, {message: "Running task to delete all scenes with _DuplicateMarkForDeletion tag. This may take a while. Please standby."}));
			RunPluginDupFileManager("delete_tagged_duplicates_task");
			return (React.createElement("div", null,
				React.createElement("h1", null, "Scenes with dup tag deleted."),
				DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
				));
		}
		return ToolsAndUtilities(); 
    };	
    const deleteBlackListTaggedDuplicatesTask = () => {
		let result = confirm("Are you sure you want to delete all scenes in blacklist having _DuplicateMarkForDeletion tags? This will delete the files, and remove tem from stash.");
		if (result)
		{
			const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
			if (componentsLoading)
				return (React.createElement(LoadingIndicator, {message: "Running task to delete all scenes in blacklist with _DuplicateMarkForDeletion tag. This may take a while. Please standby."}));
			RunPluginDupFileManager("deleteBlackListTaggedDuplicatesTask");
			return (React.createElement("div", null,
				React.createElement("h1", null, "Blacklist scenes with dup tag deleted."),
				DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
				));
		}
		return ToolsAndUtilities(); 
    };	
    const deleteTaggedDuplicatesLwrResOrLwrDuration = () => {
		let result = confirm("Are you sure you want to delete scenes having _DuplicateMarkForDeletion tags and lower resultion or duration? This will delete the files, and remove them from stash.");
		if (result)
		{
			const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
			if (componentsLoading)
				return (React.createElement(LoadingIndicator, {message: "Running task to delete all scenes with _DuplicateMarkForDeletion tag and lower resultion or duration. This may take a while. Please standby."}));
			RunPluginDupFileManager("deleteTaggedDuplicatesLwrResOrLwrDuration");
			return (React.createElement("div", null,
				React.createElement("h1", null, "Scenes with dup tag and lower resultion or duration deleted."),
				DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
				));
		}
		return ToolsAndUtilities(); 
    };	
    const deleteBlackListTaggedDuplicatesLwrResOrLwrDuration = () => {
		let result = confirm("Are you sure you want to delete scenes in blacklist having _DuplicateMarkForDeletion tags and lower resultion or duration? This will delete the files, and remove tem from stash.");
		if (result)
		{
			const componentsLoading = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.SceneCard]);
			if (componentsLoading)
				return (React.createElement(LoadingIndicator, {message: "Running task to delete all scenes in blacklist with _DuplicateMarkForDeletion tag and lower resultion or duration. This may take a while. Please standby."}));
			RunPluginDupFileManager("deleteBlackListTaggedDuplicatesLwrResOrLwrDuration");
			return (React.createElement("div", null,
				React.createElement("h1", null, "Blacklist scenes with dup tag and lower resultion or duration deleted."),
				DupFileManagerReportMenuButton, React.createElement("p", null), ToolsMenuOptionButton
				));
		}
		return ToolsAndUtilities(); 
    };
	const HomePageBeta = () => {
		var LocalDuplicateReportPath = GetLocalDuplicateReportPath();
		console.log(LocalDupReportExist);
		var MyHeader = React.createElement("h1", null, "DupFileManager Report Menu");
		if (LocalDupReportExist)
			return (React.createElement("div", {id:"FileDiv"}, "FileDiv",
					React.createElement("center", null,
					MyHeader,
					GetShowReportButton(LocalDuplicateReportPath, "Show Duplicate-File Report"),
					React.createElement("p", null),
					React.createElement(Link, { to: "/DupFileManager_AdvanceMenu" }, React.createElement(Button, null, "Advance Menu")),
					React.createElement("p", null),
					ToolsMenuOptionButton)
				));
		return (React.createElement("center", null,
				MyHeader,
				ToolsMenuOptionButton
			));
    };
	const AdvanceMenu = () => {
		PluginDupFileManager.GetFile("getAdvanceMenu");
		//const html = PluginDupFileManager.GetFile("getAdvanceMenu");
		//console.log("Sending file to FileDiv; html=" + html.substring(0, 50));
		//$("body").append( html );
		return (React.createElement("div", {id:"FileDiv"}));
    };
    PluginApi.register.route("/DupFileManager", HomePage);
	PluginApi.register.route("/DupFileManager_CreateReport", CreateReport);
	PluginApi.register.route("/DupFileManager_CreateReportWithNoTagging", CreateReportWithNoTagging);
	PluginApi.register.route("/DupFileManager_ToolsAndUtilities", ToolsAndUtilities);
	// PluginApi.register.route("/DupFileManager_HomePageBeta", HomePageBeta);
	PluginApi.register.route("/DupFileManager_AdvanceMenu", AdvanceMenu);
	PluginApi.register.route("/DupFileManager_ClearAllDuplicateTags", ClearAllDuplicateTags);
	PluginApi.register.route("/DupFileManager_deleteLocalDupReportHtmlFiles", deleteLocalDupReportHtmlFiles);
	PluginApi.register.route("/DupFileManager_deleteAllDupFileManagerTags", deleteAllDupFileManagerTags);
	PluginApi.register.route("/DupFileManager_generatePHASH_Matching", generatePHASH_Matching);
	PluginApi.register.route("/DupFileManager_tagGrayList", tagGrayList);
	PluginApi.register.route("/DupFileManager_deleteTaggedDuplicatesTask", deleteTaggedDuplicatesTask);
	PluginApi.register.route("/DupFileManager_deleteBlackListTaggedDuplicatesTask", deleteBlackListTaggedDuplicatesTask);
	PluginApi.register.route("/DupFileManager_deleteTaggedDuplicatesLwrResOrLwrDuration", deleteTaggedDuplicatesLwrResOrLwrDuration);
	PluginApi.register.route("/DupFileManager_deleteBlackListTaggedDuplicatesLwrResOrLwrDuration", deleteBlackListTaggedDuplicatesLwrResOrLwrDuration);
    PluginApi.patch.before("SettingsToolsSection", function (props) {
        const { Setting, } = PluginApi.components;
        return [
            {
                children: (React.createElement(React.Fragment, null,
                    props.children,
                    React.createElement(Setting, { heading: React.createElement(Link, { to: "/DupFileManager", title: ReportMenuButtonToolTip }, React.createElement(Button, null, "Duplicate File Report (DupFileManager)"))}),
					React.createElement(Setting, { heading: React.createElement(Link, { to: "/DupFileManager_ToolsAndUtilities", title: ToolsMenuToolTip }, React.createElement(Button, null, "DupFileManager Tools and Utilities"))}),
					// React.createElement(Setting, { heading: React.createElement(Link, { to: "/DupFileManager_HomePageBeta", title: ReportMenuButtonToolTip }, React.createElement(Button, null, "Duplicate File Report [Beta]"))}),
							)),
            },
        ];
    });
	const { faFileVideo } = PluginApi.libraries.FontAwesomeSolid;
    PluginApi.patch.before("MainNavBar.UtilityItems", function (props) {
        const { Icon, } = PluginApi.components;
        return [
            {
                children: (React.createElement(React.Fragment, null,
                    props.children,
                    React.createElement(NavLink, { className: "nav-utility", exact: true, to: "/DupFileManager" },
                        React.createElement(Button, { className: "minimal d-flex align-items-center h-100", title: ReportMenuButtonToolTip },
                            React.createElement(Icon, { icon: faFileVideo }))))) // faFileVideo fa-FileImport
            }
        ];
    });
})();
