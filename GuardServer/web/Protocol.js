/**
 *   OSC Protocol defines
 *   Created by 4DAGE-iMac2 on 2020/5/20.
 *   Copyright © 2020 4DAGE. All rights reserved.
 */

var OSC_DEV_IP = "http://192.168.10.1:80";
var OSC_JTAG_INFO_MANUFACTURER = "manufacturer";
var OSC_JTAG_INFO_MODEL = "model";
var OSC_JTAG_INFO_SERIALNUMBER = "serialNumber";
var OSC_JTAG_INFO_FIRMWAREVERSION = "firmwareVersion";
var OSC_JTAG_INFO_HARDWAREVERSION = "hardwareVersion";

/*
	协议:获取机器信息
	<REQ> - GET
	[URL]:http://${IP}:${PORT}/osc/info
	[PARAMS]:NULL

	<RESP>
	[SUCCESS]:
	{

		"manufacturer"    : string, 
		"model"           : string, 
		"serialNumber"    : string,
		"firmwareVersion" : string,
		"hardwareVersion" : string

	}

	① manufacturer, 设备制造商, e.g. "4DAGE";
	② model, 设备型号, e.g. "4DKK PRO";
	③ serialNumber, 设备SN码, e.g. "4DKKPRO_020296BA9";
	④ firwareVersion, e.g. "V1.0.0";
	⑤ hardwareVersion, e.g. "V1.0.0";

	[ERR]:NULL
*/
var OSC_INFO = "/osc/info";

var OSC_JTAG_STATE_BATTERYLEVEL = "batteryLevel";
var OSC_JTAG_STATE_BATTERYSTATE = "_batteryState";
var OSC_JTAG_STATE_STORAGEURI = "storageUri";

/*
	协议:获取机器状态信息
	<REQ> - POST
	[URL]:http://${IP}:${PORT}/osc/state
	[PARAMS]:NULL

	<RESP>
	[SUCCESS]:
	{
		"batteryLevel"    : number, 
		"_batteryState"   : number,(暂时没有) 
		"_apInfo"         : obj,
		"_staInfo"        : obj,
		"storageUri"      : string
	}

	① batteryLevel, 当前电量, e.g. 80;
	② (暂时没有)_batteryState, 插上充电器, e.g. 0没上电, 1上电;
	③ _apInfo, 热点信息, 详见"_apInfo";
	④ _staInfo, 外网信息, 详见"_staInfo";
	⑤ storageUri, 用户目录, e.g. "/mnt/DCIM";

	[ERR]:NULL
*/
var OSC_STATE = "/osc/state";

var OSC_JTAG_PARAMS = "parameters";
var OSC_JTAG_OPTIONNAMES = "optionNames";
var OSC_JTAG_OPTIONS = "options";
var OSC_JTAG_RESULTS = "results";
var OSC_JTAG_NAME = "name";
var OSC_JTAG_ERR = "error";
var OSC_JTAG_ERR_CODE = "code";
var OSC_JTAG_ERR_MESSAGE = "message";
var OSC_JTAG_STATE = "state";
var OSC_JTAG_STATE_DONE = "done";
var OSC_JTAG_STATE_INPROGRESS = "inprogress";
var OSC_JTAG_STATE_ERROR = "error";

var OSC_JTAG_SUPPORTS = "supports";
var OSC_JTAG_CMDS = "cmds";
var OSC_JTAG_INITS = "inits";

/*
	协议:执行操作
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.xxxxx",
		"parameters":
		{
			"xxx": "xxx",
			"xx1": xxx,
			...
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.xxxx",
     	"state":"done",
     	"results":
     	{
         	"xxx1":"xxxxxx",
         	"xxxx2":xxx,
         	...
     	}
 	}
	[ERR]:
	{
		"name":"camera.xxxxxx",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}

	① name, 命令名称, e.g. "camera._captureAll";
	② parameters, 对应参数, e.g. "path":"/mnt/DCIM/xxx_dir";
	③ state, 返回状态, e.g. "done"成功, "error"失败;
	④ results, 返回结果集, e.g. "filename1":"/mnt/DCIM/xxx_dir/20200101_120000_0_IMG.jpg";
	⑤ code, 返回错误结果, e.g. "code":"device is busy";
	⑥ message, 同code;
*/
var OSC_EXECUTE = "/osc/commands/execute";

/*
  not support now
*/
var OSC_CHECK = "/osc/checkForUpdates";

var OSC_JTAG_STATUS_TMPOWERON = "tmPowerOn";
var OSC_JTAG_STATUS_ISCAPTURING = "isCapturing";
var OSC_JTAG_STATUS_ISRECORDING = "isRecording";
var OSC_JTAG_STATUS_RECTIME = "recTime";
var OSC_JTAG_STATUS_ISSETMESURELIGHT = "isSettingMesureLight";
var OSC_JTAG_STATUS_ISLISTACCESSPOINTS = "isListingAccessPoints";
var OSC_JTAG_STATUS_ISSETAEPARAMS = "isSettingAEParams";
var OSC_JTAG_STATUS_ISSETRESOLUTION = "isSettingResolution";
var OSC_JTAG_STATUS_ISSETAPINFO = "isSettingApInfo";
var OSC_JTAG_STATUS_ISSETSTAINFO = "isSettingStaInfo";
var OSC_JTAG_STATUS_ISFORMATSD = "isFormatingSD";
var OSC_JTAG_STATUS_ISPACKETINGFILES = "isPacketingFiles";
var OSC_JTAG_STATUS_PACKETINGFILESPATH = "packetingFilesPath";
var OSC_JTAG_STATUS_ISCOPYINGFILES = "isCopyingFiles";
var OSC_JTAG_STATUS_COPYINGFILESPATH = "copyingFilesPath";

/*
	协议:执行操作
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/status
	[PARAMS]:NULL

	<RESP>
	[SUCCESS]:
	{
		"isCapturing"           : number,
		"isRecording"			: number,
		"recTime"               : number,
		"isSettingMesureLight"  : number,
		"isListingAccessPoints" : number,
		"isSettingAEParams"     : number,
		"isSettingResolution"   : number,
		"isSettingApInfo"       : number,
		"isSettingStaInfo"      : number,
		"isFormatingSD"         : number,
		"isPacketingFiles"      : number,
		"packetingFilesPath"    : string
 	}
	[ERR]:NULL

	① isCapturing, 是否在拍照或者录像, 详见_captureA, _captureB, _captureAll, _captureSingle,
	 _startRecord, _stopRecord;
	② isRecording, 是否在录像，如果在录像一定是isCapturing;
	③ recTime, 录像时间, 如果在录像, 返回录像时间;
	④ isSettingMesureLight, 是否在设置MesureLight, 详见 camera._setMesureLight;
	⑤ isListingAccessPoints, 是否在列wifi列表, 详见 camera._listAccessPoints;
	⑥ isSettingAEParams, 是否在设置AE参数, 详见 _aeParams;
	⑦ isSettingResolution, 是否在设置分辨率, 详见 _resolution;
	⑧ isSettingApInfo, 是否在设置热点信息, 详见 _apInfo;
	⑨ isSettingStaInfo, 是否在连接外网, 详见 _staInfo;
	⑩ isFormatingSD, 是否在格式化, 详见 camera._format;
	⑪ isPacketingFiles, 是否是在正在打包文件, 详见camera._packetFiles;
	⑫ packetingFilesPath, 当前正在打包或已完成打包的路径，详见camera._packetFiles;
	⑬⑭⑮⑯⑰⑱
*/
var OSC_STATUS = "/osc/commands/status";


var OSC_JTAG_PATH = "path";
var OSC_JTAG_NLENS = "nLens";

/*
	命令:单镜头拍照
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._captureSingle",
		"parameters":
		{
			"path" : string,
			"nLens": number
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._captureSingle",
     	"state":"done",
     	"results":
     	{
         	"path" : string
     	}
 	}
	[ERR]:
	{
		"name":"camera._captureSingle",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}

	① path, 保存的路径, e.g. "/mnt/DCIM/xxx_dir";
	② nLens, 指定哪个镜头拍照, e.g. 0~7, 详见_curLensIndexSupport;
	③ path, 返回文件的路径, e.g. "/mnt/DCIM/xxx_dir/20200101_120000_0_IMG.jpg";
	④ code, 返回错误结果, e.g. "code":"device is busy";
	⑤ message, 同code;
*/
var OSC_CMD_CAPTURESINGLE = "camera._captureSingle";

var OSC_JTAG_HDR = "HDR";
var OSC_JTAG_FILENAME0 = "filename0";
var OSC_JTAG_FILENAME1 = "filename1";
var OSC_JTAG_FILENAME2 = "filename2";
var OSC_JTAG_FILENAME3 = "filename3";
var OSC_JTAG_FILENAME4 = "filename4";

/*
	命令:A面拍照 镜头0,1,4,5
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._captureA",
		"parameters":
		{
			"HDR" : number,
			"path" : string
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._captureA",
     	"state":"done",
     	"results":
     	{
         	"HDR"       : number,
			"filename0" : string,
			"filename1" : string
     	}
 	}
	[ERR]:
	{
		"name":"camera._captureA",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}

	① path, 保存的路径, e.g. "/mnt/DCIM/xxx_dir";
	② HDR, HDR值, e.g. 0;
	③ filenameX, 返回文件的路径, e.g. "/mnt/DCIM/xxx_dir/20200101_120000_0_IMG.jpg";
	④ code, 返回错误结果, e.g. "code":"device is busy";
	⑤ message, 同code;
*/
var OSC_CMD_CAPTUREA = "camera._captureA";

var OSC_JTAG_FILENAME5 = "filename5";
var OSC_JTAG_FILENAME6 = "filename6";
var OSC_JTAG_FILENAME7 = "filename7";
var OSC_JTAG_FILENAME8 = "filename8";
var OSC_JTAG_STITCHFILE0 = "stitchfile0";
var OSC_JTAG_STITCHFILE1 = "stitchfile1";
var OSC_JTAG_STITCHFILE2 = "stitchfile2";
var OSC_JTAG_STITCHFILE3 = "stitchfile3";

/*
	命令:B面拍照 镜头2,3,6,7
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._captureB",
		"parameters":
		{
			"HDR" : number,
			"path" : string
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._captureB",
     	"state":"done",
     	"results":
     	{
         	"HDR"         : number,
			"stitchfile0" : string,
			"stitchfile1" : string,
     	}
 	}
	[ERR]:
	{
		"name":"camera._captureB",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① path, 保存的路径, e.g. "/mnt/DCIM/xxx_dir";
	② HDR, HDR值, e.g. 0;
	③ filenameX, 返回文件的路径, e.g. "/mnt/DCIM/xxx_dir/20200101_120000_X_IMG.jpg";
	④ stitchfileX, 返回拼接图片的文件的路径, e.g. "/mnt/DCIM/xxx_dir/20200522100935_X_STITCH.jpg";
	⑤ code, 返回错误结果, e.g. "code":"device is busy";
	⑥ message, 同code;

	注意：必须先拍照captureA，才能进行captuerB
*/
var OSC_CMD_CAPTUREB = "camera._captureB";

/*
	命令:全镜头拍照 
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._captureAll",
		"parameters":
		{
			"HDR" : number,
			"path" : string
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._captureAll",
     	"state":"done",
     	"results":
     	{
         	"HDR"         : number,
			"stitchfile0" : string
			"stitchfile1" : string,
     	}
 	}
	[ERR]:
	{
		"name":"camera._captureAll",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① path, 保存的路径, e.g. "/mnt/DCIM/xxx_dir";
	② HDR, HDR值, e.g. 0;
	③ filenameX, 返回文件的路径, e.g. "/mnt/DCIM/xxx_dir/20200101_120000_X_IMG.jpg";
	④ stitchfileX, 返回拼接图片的文件的路径, e.g. "/mnt/DCIM/xxx_dir/20200522100935_X_STITCH.jpg";
	⑤ code, 返回错误结果, e.g. "code":"device is busy";
	⑥ message, 同code; 
*/
var OSC_CMD_CAPTUREALL = "camera._captureAll";

/*
	命令:启动录像 
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._startRecord",
		"parameters":
		{
			"path" : string
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._startRecord",
     	"state":"done",
     	"results":
     	{
         	"path" : string
     	}
 	}
	[ERR]:
	{
		"name":"camera._startRecord",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① path, 保存的路径, e.g. "/mnt/DCIM/xxx_dir";
	② path, 返回文件的路径, e.g. "/mnt/DCIM/xxx_dir/20200101_120000.mp4";
	③ code, 返回错误结果, e.g. "code":"device is busy";
	④ message, 同code; 
	注：启动录像成功后，可以通过/osc/commands/status查看当前录了多长时间（秒单位更新）
*/
var OSC_CMD_STARTRECORD = "camera._startRecord";

var OSC_JTAG_TIME = "time";

/*
	命令:停止录像 
	<REQ> - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._stopRecord",
		"parameters":
		{
			"path" : string
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._stopRecord",
     	"state":"done",
     	"results":
     	{
         	"path" : string,
			"time" : number
     	}
 	}
	[ERR]:
	{
		"name":"camera._stopRecord",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① path, 保存的路径, e.g. "/mnt/DCIM/xxx_dir";
	② path, 返回文件的路径, e.g. "/mnt/DCIM/xxx_dir/20200101_120000.mp4";
	③ time, 录制时长, e.g. 100秒;
	④ code, 返回错误结果, e.g. "code":"device is busy";
	⑤ message, 同code; 

	注意：录像超过设备自定义时长，那么就不再需要调用该方法，设备自己会停。
*/
var OSC_CMD_STOPRECORD = "camera._stopRecord";

var OSC_JTAG_FL_PATH = "path";
var OSC_JTAG_FL_INDEX = "index";
var OSC_JTAG_FL_LENGTH = "length";
var OSC_JTAG_FL_COUNT = "count";
var OSC_JTAG_FL_FILES = "files";
var OSC_JTAG_FL_NAME = "name";
var OSC_JTAG_FL_TYPE = "type";
var OSC_JTAG_FL_FILESIZE = "size";
var OSC_FILE_TYPE_DIR = 4;
var OSC_FILE_TYPE_FILE = 8;

/*
	命令:列举文件列表 z->a/大到小排序
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.listFiles",
		"parameters":
		{
			"path"  : string,
			"index" : number,
			"length": number
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.listFiles",
     	"state":"done",
     	"results":
     	{
         	"path"  : string,
			"index" : number,
			"length": number,
			"count" : number,
			"files" :
			[
				{
					"name": string,
					"type": number,
					"size": number,
				},
				...
			]
     	}
 	}
	[ERR]:
	{
		"name":"camera.listFiles",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① path, 需要列举文件列表的路径, e.g. "/mnt/DCIM/xxx_dir";
	② index, 默认0，从第一个文件开始，如果不传默认是0, 如果是小于0，就是逆序获取;
	③ length, 默认10，每次至少取10个，如果length过大，则按实际的数量返回文件，详见files的长度;
	③ count, 当前目录文件总数(包含文件夹), e.g. 10;
	④ files, 文件列表数组, JSONArray;
	⑤ name, 文件/文件夹名称, e.g. "20200522_140000.mp4";
	⑥ type, 文件类型, e.g. 4是文件，8是文件类型;
	⑦ size, 文件大小, e.g. 1024, 单位字节；文件夹大小为-1;
	⑧ code, 返回错误结果, e.g. "code":"path not found";
	⑨ message, 同code; 

	注意：listFiles 支持列举/mnt/DCIM路径，用来查找所有项目目录。
*/
var OSC_CMD_LISTFILES = "camera.listFiles";

/*
	命令:文件删除 
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.delete",
		"parameters":
		{
			"path" : string
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.delete",
     	"state":"done",
     	"results":
     	{
         	"path" : string
     	}
 	}
	[ERR]:
	{
		"name":"camera.delete",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① path, 文件或文件夹路径, e.g. "/mnt/DCIM/xxx_dir";
	② path, 已删除的文件或文件夹的路径, e.g. "/mnt/DCIM/xxx_dir/20200101_120000.mp4";
	③ code, 返回错误结果, e.g. "code":"device is busy";
	④ message, 同code;
	注：目录「/」，「/mnt/DCIM」,特殊目录不允许删除。
*/
var OSC_CMD_DELETE = "camera.delete";

/*
	命令:文件查找
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._findFile",
		"parameters":
		{
			"path" : string
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._findFile",
     	"state":"done",
     	"results":
     	{
         	"path" : string
     	}
 	}
	[ERR]:
	{
		"name":"camera._findFile",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① path, 文件或文件夹路径, e.g. "/mnt/DCIM/xxx_dir";
	② path, 找到则返回文件或文件夹的路径, e.g. "/mnt/DCIM/xxx_dir/20200101_120000.mp4";
	③ code, 返回错误结果, e.g. "code":"parameters err";
	④ message, 同code; 
	注：目录「/」，「/mnt/DCIM」, 包含特殊目录不允许查找。
	「opt/sfm_init.bin」, 「/opt/sfm_init.json」允许查找。
*/
var OSC_CMD_FINDFILE = "camera._findFile";

/*
	命令:创建文件夹 
	<REQ> - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._createDir",
		"parameters":
		{
			"path" : string
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._createDir",
     	"state":"done",
     	"results":
     	{
         	"path" : string
     	}
 	}
	[ERR]:
	{
		"name":"camera._createDir",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① path, 要创建的文件夹路径, e.g. "/mnt/DCIM/xxx_dir";
	② path, 创建成功的文件夹的路径, e.g. "/mnt/DCIM/xxx_dir";
	③ code, 返回错误结果, e.g. "code":"parameters err";
	④ message, 同code; 
	注：目录「/」，「/mnt/DCIM」, 包含特殊目录不允许取创建文件夹。
	「*」结尾，类「/mnt/DCIMxxx」, 文件夹不允许创建。
*/
var OSC_CMD_CREATEDIR = "camera._createDir";

/*
	命令:打包文件/文件夹
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._packetFiles",
		"parameters":
		{
			"files" : [
				"xxxx",
				"xxxx",
				"xxxx"
			]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._packetFiles",
     	"state":"inprogress"
		"results":
     	{
         	"path"         : string
     	}
 	}
	[ERR]:
	{
		"name":"camera._packetFiles",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① path, 最终压缩包的路径, 如/mnt/DCIM/20200709_153252.tar.gz;
	② code/message, e.g. "code":"too many files"
*/
var OSC_CMD_PACKETFILES = "camera._packetFiles";

/*
	命令:剪切/移动/重命名 文件/文件夹
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._moveFiles",
		"parameters":
		{
			"files": 
			[
				"xxxxxxx",
				"xxxxxxx",
				...
			],
			"path" : "xxxxx"
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._moveFiles",
     	"state":"done"
		"results":
     	{
         	"path"         : string
     	}
 	}
	[ERR]:
	{
		"name":"camera._moveFiles",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① files, 原文件路径数组, 如/mnt/DCIM/tmp, /mnt/DCIM/xxx.mp4;
	② path, 新文件路径 或 重命名后的路径, 如/mnt/DCIM/tmp1;
	③ code/message, e.g. "device is busy"
*/
var OSC_CMD_MOVEFILES = "camera._moveFiles";

/*
	命令:复制 文件/文件夹
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._copyFiles"
		"parameters":
		{
			"files": 
			[
				"xxxxxxx",
				"xxxxxxx",
				...
			],
			"path" : "xxxxx"
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._copyFiles",
     	"state":"inprogress"
		"results":
     	{
         	"path"         : string
     	}
 	}
	[ERR]:
	{
		"name":"camera._copyFiles",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① files, 原文件路径数组, 如/mnt/DCIM/tmp, /mnt/DCIM/xxx.mp4;
	② path, 目的路径, 如/mnt/DCIM/tmp1;
	③ code/message, e.g. "device is busy"
*/
var OSC_CMD_COPYFILES = "camera._copyFiles";

var LIVE_PREVIEW_URL = "rtsp://192.168.10.1:554/ucast/12";

/*
	命令:获取直播url
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._getLivePreviewUrl"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._getLivePreviewUrl",
     	"state":"done",
     	"results":
     	{
         	"path" : string
     	}
 	}
	[ERR]: NULL
	
	① path, 返回直播路径, e.g. "rtsp://192.168.10.1:554/ucast/12";
*/
var OSC_CMD_GETLIVEPREVIEWURL = "camera._getLivePreviewUrl";

/*
	命令:关机
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._shutdown"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._shutdown",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera._shutdown",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① code, 返回错误结果, e.g. "code":"device is busy";
	② message, 同code 
	注：收到成功后1s关机；相机在忙时，不允许关机；
*/
var OSC_CMD_SHUTDOWN = "camera._shutdown";

/*
	命令:重启
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._reboot"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._reboot",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera._reboot",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① code, 返回错误结果, e.g. "code":"device is busy";
	② message, 同code 
	注：收到成功后1s重启；相机在忙时，不允许重启；
*/
var OSC_CMD_REBOOT = "camera._reboot";

var OSC_JTAG_AE_EXPMODE = "expMode";
var OSC_JTAG_AE_MANUALMODE = "manualMode";
var OSC_JTAG_AE_COMPENSATION = "compensation";
var OSC_JTAG_AE_EXPTIME = "expTime";
var OSC_JTAG_AE_EXPTIMEVALUE = "expTimeValue";
var OSC_JTAG_AE_ISO = "iso";
var OSC_JTAG_AE_COLORTEMPMANUALMODE = "colorTempratureManualMode";
var OSC_JTAG_AE_COLORTEMPRATURE = "colorTemprature";

/*
	命令:启动自动测光功能
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._setMesureLight"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._setMesureLight",
     	"state":"done",
		"results":
     	{
         	"manualMode"    : number,
        	"compensation"  : float,
        	"expTime"       : string,
       	    "expTimeValue"  : number,
         	"iso"           : number,
        	"colorTempratureMaualMode": number,
        	"colorTemprature"         : number
     	}
 	}
	[ERR]:
	{
		"name":"camera._setMesureLight",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}

	① manualMode, 当前是否手动AE模式, e.g. 0自动模式, 1手动模式, 详见_aeParamsSupport;
    ② compensation, 当前曝光补偿值, e.g. 0.0, 详见_aeParamsSupport;
    ③ expTime, 当前快门时间字符串值, e.g. "1/3000S", 详见_aeParamsSupport;
    ④ expTimeValue, 当前快门时间值, e.g. 330, 详见_aeParamsSupport;
    ⑤ iso, 当前感光度值, e.g. 800, 详见_aeParamsSupport;
    ⑥ colorTempratureMaualMode, 当前是否手动设置色温, e.g. 0自动, 1手动, 详见_aeParamsSupport;
    ⑦ colorTemprature, 当前色温值, e.g. 5000, 详见_aeParamsSupport;
	⑧ code, 返回错误结果, e.g. "code":"device is busy";
	⑨ message, 同code; 
*/
var OSC_CMD_SETMESURELIGHT = "camera._setMesureLight";

var OSC_JTAG_IMU = "imu";

/*
	命令:获取IMU数据
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._getIMUData"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._getIMUData",
     	"state":"done",
		 "results":{
      		 "imu": string
    	}
 	}
	[ERR]: NULL
	① imu, 一串字符数据; 
*/
var OSC_CMD_GETIMUDATA = "camera._getIMUData";


var OSC_JTAG_WIFI_LIST = "list";
var OSC_JTAG_WIFI_SSID = "ssid";
var OSC_JTAG_WIFI_LEVEL = "level";
var OSC_JTAG_WIFI_AUTH = "AUTH";
var OSC_JTAG_WIFI_MAC = "mac";
var OSC_JTAG_WIFI_STATUS = "status";
var OSC_JTAG_WIFI_ENABLE = "enable";
var OSC_JTAG_WIFI_PWD = "password";

/*
	命令:获取搜索到的wifi列表
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._listAccessPoints"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._listAccessPoints",
     	"state":"done",
		"results":
     	{
         	"list":
			[
				{
					"ssid"  : string,
					"level" : number,
					"AUTH"  : number,
					"mac"   : string
				},
				...
			],
			"count" : number
     	}
 	}
	[ERR]:
	{
		"name":"camera._listAccessPoints",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}

	① list, 存放各个搜索到的wifi信息的数组, JSONArray;
    ② ssid, wifi名字, e.g. "4DAGE_2W_5G";
    ③ level, wifi强度, e.g. -35, 单位dbm, -30~-120之间, 越大信号越好;
    ④ AUTH, wifi加密方式, e.g. 0开放, 1wpa, 2wep;
    ⑤ mac, wifi的mac地址, e.g. "08:68:8D:52:E4:29";
    ⑥ count, 搜索到多少个, e.g. 50个;
	⑦ code, 返回错误结果, e.g. "code":"device is busy";
	⑧ message, 同code; 
*/
var OSC_CMD_LISTACCESSPOINTS = "camera._listAccessPoints";

/*
	命令:重置镜头（切换为主镜头）
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._resetCamIndex"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._resetCamIndex",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera._resetCamIndex",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① code, 返回错误结果, e.g. "code":"device is busy";
	② message, 同code; 
*/
var OSC_CMD_RESETCAMINDEX = "camera._resetCamIndex";

/*
	命令:格式化机器存储
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._format"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._format",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera._format",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① code, 返回错误结果, e.g. "code":"device is busy";
	② message, 同code; 
*/
var OSC_CMD_FORMAT = "camera._format";

/*
	命令:心跳包
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._keepalive"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._keepalive",
     	"state":"done"
		"results":
     	{
         	"_apInfo"         : obj
     	}
 	}
	① _apInfo, 热点信息, 详见"_apInfo";;
*/
var OSC_CMD_KEEPALIVE = "camera._keepalive";

var OSC_JTAG_STREAMRATE_UP_AP = "apUpstreamRate";
var OSC_JTAG_STREAMRATE_DOWN_AP = "apDownstreamRate";
var OSC_JTAG_STREAMRATE_UP_STA = "staUpstreamRate";
var OSC_JTAG_STREAMRATE_DOWN_STA = "staDownstreamRate";

/*
	命令:打包文件/文件夹
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._streamRate"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._streamRate",
     	"state":"done"
		"results":
     	{
         	"apUpstreamRate"    : number,
			"apDownstreamRate"  : number,
			"staUpstreamRate"   : number,
			"staDownstreamRate" : number
     	}
 	}
	① apUpstreamRate, ap每秒上行数据量;
	② apDownstreamRate, ap每秒下行数据量;
	③ staUpstreamRate, sta每秒上行数据量;
	④ staDownstreamRate, sta每秒下行数据量;
*/
var OSC_CMD_STREAMRATE = "camera._streamRate";

/*
	命令:开机自检(power-on self-test)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._post"
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera._post",
     	"state":"done"
		"results":
     	{
			 "files" : [
				 string,
				 ....
				 ]
     	}
 	}
	[ERR]:
	{
		"name":"camera._post",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	①  
*/
var OSC_CMD_POST = "camera._post";

var OSC_JTAG_WIFI_BAND = "wifiBand";
/*
	设置wifi频段命令
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._setWifiBand",
		"parameters":
		{
			"wifiBand" : string
		}
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
		"name":"camera._setWifiBand",
     	"state":"done"
		"results":
		{
			"wifiBand": string
		}
 	}
	[ERR]:
	{
		"name":"camera._setWifiBand",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① wifiBand:wifi的频段，5G或者2.4G;
	② 调用此命令后，需要调用reboot命令重启相机，wifi才生效
*/
var OSC_CMD_SET_WIFIBAND = "camera._setWifiBand";

/*
	获取wifi频段命令
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera._getWifiBand",
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
		"name":"camera._getWifiBand",
     	"state":"done"
		"results":
		{
			"wifiBand": string
		}
 	}
	[ERR]:
	{
		"name":"camera._getWifiBand",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① wifiBand:wifi的频段，5G或者2.4G;
*/
var OSC_CMD_GET_WIFIBAND = "camera._getWifiBand";

/*
	命令:设置Option参数
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.setOptions",
		"parameters":
		{
			"options":
			{
            	$(optionname): number/string/obj
       		}
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.setOptions",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera.setOptions",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① options, 存放要设置的Option相关参数, JSONObject, 不能处理多个optionname设置;
	② $(optionname), 参数名字, 后面带该设置需要的参数, e.g. "_apInfo", 详见OSC_OPT_XXXX;
	③ code, 返回错误结果, e.g. "code":"parameters err";
	④ message, 同code;
	注: 设置完后，可以用「camera.getOptions」 + 「$(optionname)」来获取对应的参数。
*/
var OSC_CMD_SETOPTIONS = "camera.setOptions";

/*
	命令:获取Option参数
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	$(optionname1),
				$(optionname2),
				...
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"options":
			{
				$(optionsname1):number/string/obj,
				$(optionsname2):number/string/obj,
				....
			}
		}
 	}
	[ERR]:
	{
		"name":"camera.getOptions",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① optionNames, 存放要获取参数的optionname数组, JSONArray, 可处理获取多个optionname的参数;
	② $(optionname), 参数名字, e.g. "_apInfo", 详见OSC_OPT_XXXX;
	③ options, 保存所有optionname对应参数值的对象, JSONObject, 详见OSC_OPT_XXXX;
	④ code, 返回错误结果, e.g. "code":"parameters err";
	⑤ message, 同code;
	注: 获取多个optionname的参数，若中途有出现异常将直接返回异常。获取多个optionname参数时间也会累加。
*/
var OSC_CMD_GETOPTIONS = "camera.getOptions";


/*
	选项:获取设备总存储容量(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"totalSpace"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"toalSpace": number
		}
 	}
	[ERR]:NULL
	① totalSpace, 设备总容量, e.g. 13983, 单位M, 即13.9G;
*/
var OSC_OPT_TOTALSPACE = "totalSpace";

/*
	选项:获取设备剩余存储容量(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"remainingSpace"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"remainingSpace": number
		}
 	}
	[ERR]:NULL
	① remainingSpace, 设备剩余容量, e.g. 13914, 单位M, 即13.9G;
*/
var OSC_OPT_REMAININGSPACE = "remainingSpace";

/*
	选项:获取当前预览分辨率大小(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"previewFormat"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"previewFormat": number
		}
 	}
	[ERR]:NULL
	① previewFormat, 当前预览分辨率, e.g. 0, 详见previewFormatSupport;
	注意：暂时不支持设置预览分辨率；
	可先getOptions+previewFormatSupport获取列表，在找对应previewFormat值对应位置的详细参数;
*/
var OSC_OPT_PREVIEWFORMAT = "previewFormat";

var OSC_JTAG_VIDEO_WIDTH = "width";
var OSC_JTAG_VIDEO_HEIGHT = "height";
var OSC_JTAG_VIDEO_FRAMERATE = "framerate";

/*
	选项:获取当前预览分辨率支持列表(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"previewFormatSupport"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"previewFormatSupport": Array
		}
 	}
	[ERR]:NULL
	① previewFormatSupport, 支持列表, JSONArray;
	e.g.
	[
		{
			"width": 640,
			"height": 480,
			"framerate":25
		},
		...
	]
	注意：previewFormat值即对应previewFormatSupport数组的第几项;
*/
var OSC_OPT_PREVIEWFORMATSUPPORT = "previewFormatSupport";
//[{"width":640,"height":480,"framerate":25}]

/*
	选项:获取当前AE参数(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_aeParams"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"_aeParams":
			{
				"manualMode"    : number,
				"compensation"  : float,
				"expTime"       : string,
				"expTimeValue"  : number,
				"iso"           : number,
				"colorTempratureMaualMode": number,
				"colorTemprature"         : number
			}
		}
 	}
	[ERR]:NULL
	① _aeParams, 包含各个子参数的对象, JSONObject, 参数详见_aeParamsSupport;
	
	选项:设置AE参数(Setter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.setOptions",
		"parameters":
		{
			"options":
			{
            	"_aeParams":
				{
					"manualMode"    : number,
					"compensation"  : float,
					"expTime"       : string,
					"expTimeValue"  : number,
					"iso"           : number,
					"colorTempratureManualMode": number,
					"colorTemprature"         : number
				}
       		}
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.setOptions",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera.setOptions",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① _aeParams, 包含各个子参数的对象, JSONObject, 参数详见_aeParamsSupport;
	② expTime, 可选, 由expTimeValue可以转化expTime;
	③ code, 返回错误结果, e.g. "code":"parameters err";
	④ message, 同code;
*/
var OSC_OPT_AEPARAMS = "_aeParams";


var OSC_JTAG_PARAM_MAX = "max";
var OSC_JTAG_PARAM_MIN = "min";
var OSC_JTAG_PARAM_INTERVAL = "interval";
var OSC_JTAG_PARAM_UNIT = "unit";


/*
	选项:获取AE支持列表(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_aeParamsSupport"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
    "name":"camera.getOptions",
    "state":"done",
    "results":{
        "_aeParamsSupport":[
            {
                "manualMode":0
            },
            {
                "manualMode":1,
				"expMode":[
					0,
					1
				],
                "iso":{
                    "max":800,
                    "min":100,
                    "interval":100
                },
                "compensation":{
                    "max":1,
                    "min":-1,
                    "interval":0.1
                },
                "expTime":[
                    "1/3000S",
                    "1/2000S",
                    "1/1000S",
                    "1/500S",
                    "1/250S",
                    "1/125S",
                    "1/60S",
                    "1/30S",
                    "1/15S",
                    "1/8S",
                    "1/2S",
                    "1S"
                ],
                "expTimeValue":[
                    330,
                    500,
                    1000,
                    2000,
                    4000,
                    8000,
                    16700,
                    33000,
                    66000,
                    125000,
                    500000,
                    1000000
                ],
                "colorTemprature":[
                    {
                        "colorTempratureManualMode":0
                    },
                    {
                        "colorTempratureManualMode":1,
                        "colorTemprature":{
                            "max":10000,
                            "min":2000,
                            "interval":1,
                            "unit":"K"
                        }
                    }
                ]
            }
        ]
    }
}
	[ERR]:NULL
	① _aeParamsSupport, _aeParams支持列表, JSONArray;
	② manualMode, number, 是否手动AE模式, e.g. 0自动模式, 1手动模式;
    ③expMode,曝光模式，0：自动曝光（曝光采用compensation的值）	1：手动曝光（曝光采用expTime和iso的值）
    ④ compensation, array, 曝光补偿值域;
    ⑤ expTime, array, 快门时间字符串值值域;
    ⑥ expTimeValue, array, 快门时间值值域;
    ⑦ iso, array, 感光度值域;
    ⑧colorTempratureMaualMode, array, 是否手动设置色温;
	⑨colorTemprature, array, 色温值域;
	注意： 
	manualMode=0, colorTempratureManualMode/colorTemprature/compensation 可调;
	manualMode=1, colorTempratureManualMode/colorTemprature/expTime/iso 可调;
	colorTempratureManualMode=0, colorTemprature设置无效;
	colorTempratureManualMode=1, colorTemprature设置有效;
*/
var OSC_OPT_AEPARAMSSUPPORT = "_aeParamsSupport";
//[{"manualMode":0},{"manualMode":1,"expMode":[0,1],"iso":{"max":800,"min":100,"interval":100},"compensation":{"max":1,"min":-1,"interval":0.1},"expTime":["1/3000S","1/2000S","1/1000S","1/500S","1/250S","1/125S","1/60S","1/30S","1/15S","1/8S","1/2S","1S"],"expTimeValue":[330,500,1000,2000,4000,8000,16700,33000,66000,125000,500000,1000000],"colorTemprature":[{"colorTempratureManualMode":0},{"colorTempratureManualMode":1,"colorTemprature":{"max":10000,"min":2000,"interval":1,"unit":"K"}}]}]

/*
	选项:获取当前分辨率值(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_resolution"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"_resolution": number
		}
 	}
	[ERR]:NULL
	① _resolution, 当前分辨率值, number, 参数详见_resolutionSupport;
	
	选项:设置分辨率(Setter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.setOptions",
		"parameters":
		{
			"options":
			{
            	"_resolution": numer
       		}
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.setOptions",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera.setOptions",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① _resolution, 分辨率值, number, 参数详见_resolutionSupport;
	② code, 返回错误结果, e.g. "code":"parameters err";
	③ message, 同code;
*/
var OSC_OPT_RESOLUTION = "_resolution";


/*
	选项:获取分辨率支持列表(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_resolutionSupport"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"_resolutionSupport":
			[
				{
					"with":4608, 
					"height":3456, 
				},
				{
					"with":2592, 
					"height":1944, 
				},
				{
					"with":2112, 
					"height":1584, 
				}
			]
		}
 	}
	[ERR]:NULL
	① _resolutionSupport, 分辨率支持列表, JSONArray;
	② width, number, 宽;
    ③ height, number, 高;
*/
var OSC_OPT_RESOLUTIONSUPPORT = "_resolutionSupport";
//[{"with":4608,"height":3456},{"with":2592,"height":1944},{"with":2112,"height":1584}]

/*
	选项:获取当前使用的镜头号(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_curLensIndex"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"_curLensIndex": number
		}
 	}
	[ERR]:NULL
	① _curLensIndex, 当前使用的是哪个镜头, number, 参数详见_curLensIndexSupport;
	
	选项:设置使用哪个镜头(Setter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.setOptions",
		"parameters":
		{
			"options":
			{
            	"_curLensIndex": numer
       		}
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.setOptions",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera.setOptions",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① _curLensIndex, 要设置的镜头号, number, 参数详见_curLensIndexSupport;
	② code, 返回错误结果, e.g. "code":"parameters err";
	③ message, 同code;
*/
var OSC_OPT_CURLENSINDEX = "_curLensIndex";

/*
	选项:获取镜头支持列表(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_curLensIndexSupport"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"_curLensIndexSupport": [0, 1, 2, 3, 4, 5, 6, 7]
		}
 	}
	[ERR]:NULL
	① _curLensIndexSupport, 镜头支持列表, JSONArray;
	② width, number, 宽;
    ③ height, number, 高;
*/
var OSC_OPT_CURLENSINDEXSUPPORT = "_curLensIndexSupport";
//[0, 1, 2, 3, 4, 5, 6, 7]

var OSC_JTAG_TM_YEAR = "year";
var OSC_JTAG_TM_MONTH = "month";
var OSC_JTAG_TM_DAY = "day";
var OSC_JTAG_TM_HOUR = "hour";
var OSC_JTAG_TM_MINUTE = "minute";
var OSC_JTAG_TM_SECOND = "second";

/*
	选项:获取设备时间(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_dateTime"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"_dateTime":
			e.g.
			{
				"year":  2020,
				"month": 5,
				"day":   15,
				"hour":  17,
				"minute":03,
				"second":30
			}
		}
 	}
	[ERR]:NULL
	
	选项:设置设备时间(Setter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.setOptions",
		"parameters":
		{
			"options":
			{
            	"_dateTime": number
       		}
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.setOptions",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera.setOptions",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① _dateTime, setter时候, number, 是自1970到现在的秒数, e.g. 1590139364(2020-05-22 17:22:44);
	② code, 返回错误结果, e.g. "code":"parameters err";
	③ message, 同code;
*/
var OSC_OPT_DATETIME = "_dateTime";

/*
    _timeZone 时区
    Setter, number,
    Getter, obj
    {
        "_timeZone":"GMT+08:00",
        "_timeZoneValue": 27
    }
	Setter, number
	{
		"_timeZoneValue":number
	}
*/


/*
	选项:获取设备时区(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_timeZoneValue"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			e.g.
			"_timeZoneValue":
			{
				"_timeZoneValue": 27,
				"_timeZone": "GMT+08:00"
			}
		}
 	}
	[ERR]:NULL
	①_timeZoneValue, number, 对应字符串时区在数组的位置;
	②_timeZone, string, 字符串时区, 详见_timeZoneSupport;

	选项:设置设备时间(Setter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.setOptions",
		"parameters":
		{
			"options":
			{
            	"_timeZoneValue": number
       		}
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.setOptions",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera.setOptions",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① _timeZoneValue, setter时候, number, 所需要设置的字符串时区在数组的位置;
	② code, 返回错误结果, e.g. "code":"parameters err";
	③ message, 同code;
*/
var OSC_OPT_TIMEZONE = "_timeZoneValue";

/*
	选项:获取时区列表(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_timeZoneSupport"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			e.g.
			"_timeZoneSupport": 
			[
				"GMT-12:00",
				"GMT-11:00",
				"GMT-10:00",
				"GMT-09:00",
				"GMT-08:00",
				"GMT-07:00",
				"GMT-06:00",
				"GMT-05:00",
				"GMT-04:30",
				"GMT-04:00",
				"GMT-03:30",
				"GMT-03:00",
				"GMT-02:00",
				"GMT-01:00",
				"GMT+00:00",
				"GMT+01:00",
				"GMT+02:00",
				"GMT+03:00",
				"GMT+03:30",
				"GMT+04:00",
				"GMT+04:30",
				"GMT+05:00",
				"GMT+05:30",
				"GMT+05:45",
				"GMT+06:00",
				"GMT+06:30",
				"GMT+07:00",
				"GMT+08:00",
				"GMT+09:00",
				"GMT+09:30",
				"GMT+10:00",
				"GMT+11:00",
				"GMT+12:00",
				"GMT+13:00"
			]
		}
 	}
	[ERR]:NULL
*/
var OSC_OPT_TIMEZONESUPPORT = "_timeZoneSupport";
//["GMT-12:00","GMT-11:00","GMT-10:00","GMT-09:00","GMT-08:00","GMT-07:00","GMT-06:00","GMT-05:00","GMT-04:30","GMT-04:00","GMT-03:30","GMT-03:00","GMT-02:00","GMT-01:00","GMT+00:00","GMT+01:00","GMT+02:00","GMT+03:00","GMT+03:30","GMT+04:00","GMT+04:30","GMT+05:00","GMT+05:30","GMT+05:45","GMT+06:00","GMT+06:30","GMT+07:00","GMT+08:00","GMT+09:00","GMT+09:30","GMT+10:00","GMT+11:00","GMT+12:00","GMT+13:00"]

/*
	选项:获取热点信息(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_apInfo"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"_apInfo":
			e.g.
			{
				"ssid":  "4DAGE_2W_5G",
				"password": "4DAGE168",
				"mac": "74:ee:2a:58:27:f8"
			}
		}
 	}
	[ERR]:NULL
	
	选项:修改热点信息(Setter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.setOptions",
		"parameters":
		{
			"options":
			{
				e.g.
            	"_apInfo": 
				{
					"ssid":  "4DAGE_2W_5G",
					"password": "4DAGE888",
				}
       		}
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.setOptions",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera.setOptions",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① ssid, setter, string, [1,64]个字符;
	② password, setter, string, [8,16]个字符，只允许可显示的ASCII码, [32,126];
	③ code, 返回错误结果, e.g. "code":"parameters err";
	④ message, 同code;
*/
var OSC_OPT_APINFO = "_apInfo";


/*
	选项:获取当前外网信息(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_staInfo"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"_staInfo":
			e.g.
			{
				"ssid":  "4DAGE_2W_5G",
				"password": "4DAGE168",
				"mac": "74:ee:2a:58:27:f8"
				"status": 0
			}
		}
 	}
	[ERR]:NULL
	
	选项:连接指定WIFI(Setter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.setOptions",
		"parameters":
		{
			"options":
			{
            	"_staInfo": 
				{
					"enable":   number,
					"ssid":     string,
					"password": string,
					"mac":      string,
					"AUTH":     number
				}
       		}
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.setOptions",
     	"state":"done"
 	}
	[ERR]:
	{
		"name":"camera.setOptions",
		"state":"error",
		"error":
		{
			"code"    : string,
			"message" : string
		}
	}
	① status, getter, number, WIFI是否链接成功 0-成功 其他-错误码;
	② enable, setter, number, 0-断开外网WIFI, 1-连接外网WIFI, 为0是, 其它参数不再检查;
	③ ssid, setter, string, [1,64]个字符;
	④ password, setter, string, [8,16]个字符，只允许可显示的ASCII码, [32,126];
	⑤ mac, setter, string, 17个字符，[A~Z][a~z][0~9][:];
	⑥ AUTH, setter, number, 加密方式，0-开放；1-wpa; 2-wep;
	⑦ code, 返回错误结果, e.g. "code":"parameters err";
	⑧ message, 同code;

	注:如果_staSupport返回0，不支持连接WIFI, 则_staInfo不支持
*/
var OSC_OPT_STAINFO = "_staInfo";

/*
	选项:设备是否支持连接WIFI(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_staSupport"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"_staSupport": number
		}
 	}
	[ERR]:NULL
	① _staSupport, number, 0-不支持，1-支持;
*/
var OSC_OPT_STASUPPORT = "_staSupport";

/*
	选项:获取设备SN码(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_sn"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"_sn": string
		}
 	}
	[ERR]:NULL
	① _sn, string, 设备SN码;
*/
var OSC_OPT_SN = "_sn";

/*
	选项:获取自动关机参数(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"offDelay"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			"offDelay": number
		}
 	}
	[ERR]:NULL
	① offDelay, number, 当前自动关机时间, 单位分钟;

	选项:设置自动关机时间(Setter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.setOptions",
		"parameters":
		{
			"options":
			{
            	"offDelay": number
       		}
		}
 	}

	<RESP>
	[SUCCESS]:
	{
		"name":"camera.setOptions",
     	"state":"done"
 	}
	[ERR]:NULL
*/
var OSC_OPT_OFFDELAY = "offDelay";

/*
	选项:获取自动关机支持时间列表(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"offDelaySupport"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			e.g.
			"offDelaySupport": [0, 5, 10, 30]
		}
 	}
	[ERR]:NULL
	① offDelaySupport, array, 当前自动关机时间支持列表, 单位分钟;
*/
var OSC_OPT_OFFDELAYSUPPORT = "offDelaySupport";
//[0, 5, 10, 30]

/*
	选项:获取HDR支持列表(Getter)
	<REQ>  - POST
	[URL]:http://${IP}:${PORT}/osc/commands/execute
	[PARAMS]:
	{
		"name":"camera.getOptions",
		"parameters":
		{
			"optionNames":
			[
            	"_hdrSupport"
       		]
		}
 	}

	<RESP>
	[SUCCESS]:
	e.g.
	{
		"name":"camera.getOptions",
     	"state":"done"
		"results":
		{
			e.g.
			"_hdrSupport": [0, 1, 2, 3]
		}
 	}
	[ERR]:NULL
	① _hdrSupport, array, 当前hdr支持列表;
*/
var OSC_OPT_HDRSUPPORT = "_hdrSupport";
//[0, 1, 2, 3]

/*
获取/设置 参数成功
*/
var OSC_RTN_OPT_OK = 0;

/*
获取/设置 参数错误
*/
var OSC_RTN_OPT_PARAMERR = -1;

/*
获取/设置 这个OPTION不支持
*/
var OSC_RTN_OPT_OPTNOTSUPPORT = -2;

/*
获取/设置 相机正在忙，不允许操作
*/
var OSC_RTN_OPT_DEV_BUSY = -3;

/*
获取/设置 返回结果失败
*/
var OSC_RTN_OPT_ERRRESULT = -4;

/*
获取/设置 设置返回超时
*/
var OSC_RTN_OPT_TIMEOUT = -5;


/*
参数错误
同OSC_RTN_OPT_PARAMERR
*/
var OSC_ERR_PARAMSERR = "parameters err";

/*
不支持的命令
*/
var OSC_ERR_COMMANDNOTSUPPORT = "command not support";

/*
不支持的OPTION
同 OSC_RTN_OPT_OPTNOTSUPPORT
*/
var OSC_ERR_OPTIONNOTSUPPORT = "option not support";

/*
相机正忙，不允许操作
同 OSC_RTN_OPT_DEV_BUSY
*/
var OSC_ERR_DEVBUSY = "device is busy";

/*
相机空闲，不允许该操作
如 没在录像，却调用stopRecord
*/
var OSC_ERR_DEVIDLE = "device is idle";

/*
Http错误请求，协议不对，GET/POST使用错误，传参有误
*/
var OSC_ERR_ERRREQUEST = "error request";

/*
没有插卡
*/
var OSC_ERR_NOTFCARD = "no tfcard";

/*
设备存储用量不够
*/
var OSC_ERR_STORAGENOTENOUGTH = "storage not enougth";

/*
路径找不到，报错
*/
var OSC_ERR_PATHNOTFOUND = "path not found";

/*
路径存在， 报错
如创建文件夹时，文件夹本来就存在
*/
var OSC_ERR_PATHEXIST = "path exist";

/*
找不到文件，报错
*/
var OSC_ERR_FILENOTFOUND = "file not found";

/*
打包文件，一次性打包太多了
文件太多了
*/
var OSC_ERR_TOOMUCHFILES = "too much files";

/*
操作超时
如连接wifi超过15s
同 OSC_RTN_OPT_TIMEOUT
*/
var OSC_ERR_REQUESTTIMEOUT = "request time out";

/*
操作不合法
如操作根路径等
*/
var OSC_ERR_REQUESTNOTPERMIT = "request not permit";

/*
服务器报错
比如没有实现Protocol层的回调
*/
var OSC_ERR_SERVERERR = "server err";

/*
操作结果返回错误
同OSC_RTN_OPT_ERRRESULT
*/
var OSC_ERR_RESULT = "err result";

/*
拍照潜规则，要先将分辨率设置0/1，如果>=2 报错
*/
var OSC_ERR_RESOLUTION = "err resolution";

/*
设置hdr模式[0, 1, 2, 3],不在此范围报错
*/
var OSC_ERR_HDR = "err hdr mode";

/*
输入的命名只允许 a-z, A-Z, _, .
*/
var OSC_ERR_NAMENOTRIGHT = "only a-z, A-Z, '_', '.', first letter can not be '.'";


