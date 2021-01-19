//-------------------- App start --------------------

/*
返回年月日时分秒
*/
function getCurrentTime()
{ 
	//创建对象  
	var date = new Date();  
	//获取年份  
	var y = date.getFullYear(); 
	//获取月份  返回0-11     
	var m =date.getMonth()+1; 
	// 获取日   
	var d = date.getDate();
	//获取星期几  返回0-6   (0=星期天)   
	var w = date.getDay();    
	//星期几
	var ww = ' 星期'+'日一二三四五六'.charAt(date.getDay()) ;
	//时
	var h = date.getHours();
	//分  
	var minute = date.getMinutes() 
	//秒 
	var s = date.getSeconds(); 
	//毫秒
	var sss = date.getMilliseconds() ;
	
	if(m<10){
	m = "0"+m;
	}
	if(d<10){
	d = "0"+d;
	}
	if(h<10){
	h = "0"+h;
	}
	if(minute<10){
	minute = "0"+minute;
	} 
	if(s<10){
	s = "0"+s;
	}
	
	if(sss<10){
	sss = "00"+sss;
	}else if(sss<100){
	sss = "0"+sss;
	}
	return "["+y+"-"+m+"-"+d+" "+h+":"+minute+":"+s + "]";  
}  

/*
写log到textarea
*/
function writeLog(data)
{
	var logArea = document.getElementById('logArea');
	if(logArea == null)
	{
		//console.log("请在页面添加一个id是logArea的textarea控件!");
	}
	else
	{
		var innerHTML = logArea.innerHTML;
		innerHTML = innerHTML + "\n" + getCurrentTime() + "\n" + data + "\n";
		logArea.innerHTML = innerHTML;
		logArea.scrollTop = logArea.scrollHeight;
	}
}

/*
清空log列表
*/
function clearLog()
{
	var logArea = document.getElementById('logArea');
	if(logArea == null)
	{
		console.log("请在页面添加一个id是logArea的textarea控件!");
	}
	else
	{
		logArea.innerHTML = "";
	}
}

var gCallback;

function setRespCallback(callback)
{
	gCallback = callback;
}

/*
设备端返回数据，回调
*/
function respCallback(strJsonResult)
{
	//console.log("respCallback - " + strJsonResult);
	writeLog(strJsonResult);
	if(gCallback)
	{
		gCallback(strJsonResult);
	}
}

/*
GET 方法请求
*/
function getToDev(protocol)
{
	console.log("GET - [protocol:" + protocol + "]");
	writeLog(protocol);
	var xhr;
	if (window.XMLHttpRequest)
	{// code for all new browsers
		xhr=new XMLHttpRequest();
	}
	else if (window.ActiveXObject)
	{// code for IE5 and IE6
		xhr=new ActiveXObject("Microsoft.XMLHTTP");
	}

	if (xhr == null)
	{
		alert("Your browser does not support XMLHTTP.");
	}
	else
	{
		var cmd_url = OSC_DEV_IP + protocol;
		xhr.open("GET", cmd_url, true);
		xhr.timeout = 2000;
		xhr.onreadystatechange = function(){
			//console.log("status:" + xhr.status + " readyState:" + xhr.readyState);
			if(xhr.readyState == 4)
			{
				respCallback(xhr.responseText);
			}
		}
		xhr.ontimeout = function(){
			alert("connect overtime!");
		};
		xhr.send(null);
	}
}

/*
发命令到设备端
*/
function postToDev(protocol, jsonParams)
{
	console.log("post - [protocol:" + protocol + "]" + "[jsonParams:" + jsonParams + "]");
	writeLog(protocol + "\n" + jsonParams);
	var xhr;
	if (window.XMLHttpRequest)
	{// code for all new browsers
		xhr=new XMLHttpRequest();
	}
	else if (window.ActiveXObject)
	{// code for IE5 and IE6
		xhr=new ActiveXObject("Microsoft.XMLHTTP");
	}

	if (xhr == null)
	{
		alert("Your browser does not support XMLHTTP.");
	}
	else
	{
		var cmd_url = OSC_DEV_IP + protocol;
		xhr.open("POST", cmd_url, true);
		// xhr.timeout = 2000;
		xhr.onreadystatechange = function(){
			//console.log("status:" + xhr.status + " readyState:" + xhr.readyState);
			if(xhr.readyState == 4)
			{
				respCallback(xhr.responseText);
			}
		}
		xhr.ontimeout = function(){
			alert("connect overtime!");
		};
		xhr.send(jsonParams);
	}
	
}


function captureAll(path, hdr)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_CAPTUREALL;
	paramObj.parameters = new Object();
    paramObj.parameters[OSC_JTAG_PATH] = path;
    paramObj.parameters[OSC_JTAG_HDR] = hdr;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function captureA(path, hdr)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_CAPTUREA;
	paramObj.parameters = new Object();
    paramObj.parameters[OSC_JTAG_PATH] = path;
    paramObj.parameters[OSC_JTAG_HDR] = hdr;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function captureB(path)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_CAPTUREB;
	paramObj.parameters = new Object();
	paramObj.parameters[OSC_JTAG_PATH] = path;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function captureSingle(path, nLens)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_CAPTURESINGLE;
	paramObj.parameters = new Object();
	paramObj.parameters[OSC_JTAG_PATH] = path;
	paramObj.parameters[OSC_JTAG_NLENS] = nLens;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function startRecord(path)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_STARTRECORD;
	paramObj.parameters = new Object();
	paramObj.parameters[OSC_JTAG_PATH] = path;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function stopRecord()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_STOPRECORD;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function listFiles(path)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_LISTFILES;
	paramObj.parameters = new Object();
	paramObj.parameters[OSC_JTAG_PATH] = path;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function listFiles(path, index, length)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_LISTFILES;
	paramObj.parameters = new Object();
	paramObj.parameters[OSC_JTAG_FL_PATH] = path;
	paramObj.parameters[OSC_JTAG_FL_INDEX] = index;
	paramObj.parameters[OSC_JTAG_FL_LENGTH] = length;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function deleteFile(path)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_DELETE;
	paramObj.parameters = new Object();
	paramObj.parameters[OSC_JTAG_PATH] = path;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function createDir(path)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_CREATEDIR;
	paramObj.parameters = new Object();
	paramObj.parameters[OSC_JTAG_PATH] = path;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function findFile(path)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_FINDFILE;
	paramObj.parameters = new Object();
	paramObj.parameters[OSC_JTAG_PATH] = path;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getAEParams()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETOPTIONS;
	paramObj.parameters = new Object();
	var aray = [];
	aray[0] = OSC_OPT_AEPARAMS;
	paramObj.parameters[OSC_JTAG_OPTIONNAMES] = aray;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getAEParamsSupport()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETOPTIONS;
	paramObj.parameters = new Object();
	var aray = [];
	aray[0] = OSC_OPT_AEPARAMSSUPPORT;
	paramObj.parameters[OSC_JTAG_OPTIONNAMES] = aray;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function setAEParams(manualMode, expMode, compensation, expTimeValue, iso, colorTempratureManualMode, colorTemprature)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SETOPTIONS;
	paramObj.parameters = new Object();
	paramObj.parameters.options = new Object();
	paramObj.parameters.options[OSC_OPT_AEPARAMS] = new Object();
	paramObj.parameters.options[OSC_OPT_AEPARAMS][OSC_JTAG_AE_MANUALMODE] = manualMode;
	paramObj.parameters.options[OSC_OPT_AEPARAMS][OSC_JTAG_AE_EXPMODE] = expMode;
	paramObj.parameters.options[OSC_OPT_AEPARAMS][OSC_JTAG_AE_COMPENSATION] = compensation;
	paramObj.parameters.options[OSC_OPT_AEPARAMS][OSC_JTAG_AE_EXPTIMEVALUE] = expTimeValue;
	paramObj.parameters.options[OSC_OPT_AEPARAMS][OSC_JTAG_AE_ISO] = iso;
	paramObj.parameters.options[OSC_OPT_AEPARAMS][OSC_JTAG_AE_COLORTEMPMANUALMODE] = colorTempratureManualMode;
	paramObj.parameters.options[OSC_OPT_AEPARAMS][OSC_JTAG_AE_COLORTEMPRATURE] = colorTemprature;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getDateTime()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETOPTIONS;
	paramObj.parameters = new Object();
	var aray = [];
	aray[0] = OSC_OPT_DATETIME;
	paramObj.parameters[OSC_JTAG_OPTIONNAMES] = aray;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function setDateTime(time)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SETOPTIONS;
	paramObj.parameters = new Object();
	paramObj.parameters.options = new Object();
	paramObj.parameters.options[OSC_OPT_DATETIME] = time;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function setTimeZoneValue(index)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SETOPTIONS;
	paramObj.parameters = new Object();
	paramObj.parameters.options = new Object();
	paramObj.parameters.options[OSC_OPT_TIMEZONE] = index;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getTimeZone()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETOPTIONS;
	paramObj.parameters = new Object();
	var aray = [];
	aray[0] = OSC_OPT_TIMEZONE;
	paramObj.parameters[OSC_JTAG_OPTIONNAMES] = aray;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getListAccessPoints()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_LISTACCESSPOINTS;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function setStaInfo(enable, ssid, password, mac, auth)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SETOPTIONS;
	paramObj.parameters = new Object();
	paramObj.parameters.options = new Object();
	paramObj.parameters.options[OSC_OPT_STAINFO] = new Object();

	paramObj.parameters.options[OSC_OPT_STAINFO][OSC_JTAG_WIFI_ENABLE] = enable;

	if(enable == 1)
	{
		paramObj.parameters.options[OSC_OPT_STAINFO][OSC_JTAG_WIFI_SSID]   = ssid;
		if(auth === 0)
		{
			paramObj.parameters.options[OSC_OPT_STAINFO][OSC_JTAG_WIFI_PWD] = "";
		}
		else
		{
			paramObj.parameters.options[OSC_OPT_STAINFO][OSC_JTAG_WIFI_PWD] = password;
		}
		paramObj.parameters.options[OSC_OPT_STAINFO][OSC_JTAG_WIFI_MAC]    = mac;
		paramObj.parameters.options[OSC_OPT_STAINFO][OSC_JTAG_WIFI_AUTH]   = auth;
	}
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getStaInfo()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETOPTIONS;
	paramObj.parameters = new Object();
	var aray = [];
	aray[0] = OSC_OPT_STAINFO;
	paramObj.parameters[OSC_JTAG_OPTIONNAMES] = aray;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getApInfo()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETOPTIONS;
	paramObj.parameters = new Object();
	var aray = [];
	aray[0] = OSC_OPT_APINFO;
	paramObj.parameters[OSC_JTAG_OPTIONNAMES] = aray;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function setApInfo(ssid, pwd)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SETOPTIONS;
	paramObj.parameters = new Object();
	paramObj.parameters.options = new Object();
	paramObj.parameters.options[OSC_OPT_APINFO] = new Object();
	paramObj.parameters.options[OSC_OPT_APINFO][OSC_JTAG_WIFI_SSID] = ssid;
	paramObj.parameters.options[OSC_OPT_APINFO][OSC_JTAG_WIFI_PWD]  = pwd;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getResolution()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETOPTIONS;
	paramObj.parameters = new Object();
	var aray = [];
	aray[0] = OSC_OPT_RESOLUTION;
	paramObj.parameters[OSC_JTAG_OPTIONNAMES] = aray;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function setResolution(resolution)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SETOPTIONS;
	paramObj.parameters = new Object();
	paramObj.parameters.options = new Object();
	paramObj.parameters.options[OSC_OPT_RESOLUTION] = resolution;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getLivePreviewUrl()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETLIVEPREVIEWURL;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function devShutdown()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SHUTDOWN;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function devReboot()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_REBOOT;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getIMUData()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETIMUDATA;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function setMesureLight()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SETMESURELIGHT;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function resetCamIndex()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_RESETCAMINDEX;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);	
}

function devKeepAlive()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_KEEPALIVE;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getStreamRate()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_STREAMRATE;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function devformat()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_FORMAT;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getCurLensIndex()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETOPTIONS;
	paramObj.parameters = new Object();
	var aray = [];
	aray[0] = OSC_OPT_CURLENSINDEX;
	paramObj.parameters[OSC_JTAG_OPTIONNAMES] = aray;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function setCurLensIndex(index)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SETOPTIONS;
	paramObj.parameters = new Object();
	paramObj.parameters[OSC_OPT_CURLENSINDEX] = index;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getOffDelay()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GETOPTIONS;
	paramObj.parameters = new Object();
	var aray = [];
	aray[0] = OSC_OPT_OFFDELAY;
	paramObj.parameters[OSC_JTAG_OPTIONNAMES] = aray;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function setOffDelay(time)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SETOPTIONS;
	paramObj.parameters = new Object();
	paramObj.parameters.options = new Object();
	paramObj.parameters.options[OSC_OPT_OFFDELAY] = time;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getDevInfo()
{
	getToDev(OSC_INFO);
}

function getDevState()
{
	postToDev(OSC_STATE, null);
}

function getDevStatus()
{
	postToDev(OSC_STATUS, null);
}

function goPOST()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_POST;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function setWifiBand(wifiBand)
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_SET_WIFIBAND;
	paramObj.parameters = new Object();
	paramObj.parameters[OSC_JTAG_WIFI_BAND] = wifiBand;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}

function getWifiBand()
{
	var paramObj = new Object();
	paramObj.name = OSC_CMD_GET_WIFIBAND;
	var jsonStr = JSON.stringify(paramObj);
	postToDev(OSC_EXECUTE, jsonStr);
}
