$(document).ready(function() {

	$('div.candelete').mouseover(function() {
		
	});

	var deviceAgent = navigator.userAgent.toLowerCase();
	var iDevice = deviceAgent.match(/(iphone|ipod)/);
	
	if (iDevice) {
		window.addEventListener("load",function() {
		  setTimeout(function(){
		    window.scrollTo(0, 1);
		  }, 0);
		});
	}

	var defaultInputValue = "Download URL";
	
	$('input#formInput').val(defaultInputValue);
	$('input#formInput').addClass('inputDefaultValue');
	
	$('input#formInput').blur(function() {
		if ($(this).val() == '' || $(this).val() == defaultInputValue) {
			$(this).val(defaultInputValue);
			$(this).addClass('inputDefaultValue');
		} else {
			$(this).removeClass('inputDefaultValue');
		}
	});
	
	$('input#formInput').focus(function() {
		if ($(this).val() == defaultInputValue) {
			$(this).val('');
			$(this).removeClass('inputDefaultValue');
		}
	});
	
	/**
	 * Lauching a new download
	 */
	$('div#formSubmit').click(function() {
		downloadMessage.set(false, '');
		
		var fileURL = $('#formInput').val();
		if (!/(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/.test(fileURL)) {
			downloadMessage.set(true, 'Download error: Please fill the form with a valid http or ftp url.');
			return false;
		}

		$('#formInput').addClass('inputDefaultValue').attr('disabled', 'disabled');
		$('#formSubmit').fadeOut(100);
		$('#formLoader').fadeIn(100);
		
		$.ajax({
			url: '/add-url',
			dataType: 'json',
			data: 'fileURL=' + encodeURI(fileURL),
			success: function() {
				$('#formLoader').fadeOut(100);
				$('#formSubmit').fadeIn();
				$('#formInput').removeClass('inputDefaultValue').removeAttr('disabled');
				downloadMessage.set(false, 'Download launched successfully.');
				download.getAllStatuses();
			},
			error: function() {
				$('#formLoader').fadeOut(100, function() { $('#formSubmit').fadeIn() });
				$('#formInput').removeClass('inputDefaultValue').removeAttr('disabled');
				downloadMessage.set(true, 'Download error: An error has occured during the download request.');
			}
		})
		
		
	});
});

/**
 * Download Message Handler/Setter
 */
var downloadMessage = {
	set: function (isError, downloadMessage) {
		$('#downloadMessage').removeClass('errorColor').removeClass('successColor');
		$('#downloadMessage').html(downloadMessage);
	
		if (isError)	$('#downloadMessage').addClass('errorColor');
		else			$('#downloadMessage').addClass('successColor');
	}
};
	
var colours = [ 'blue', 'orange', 'green' ];
var currentColor 	= 0;
var totalDownloads 	= 0; 
var downloadFileList = [ ];

var download = {
	display: function(currentDownload, filename, fileURL, filePercent, fileSpeed) {
		
		filePercent = (filePercent) ? filePercent : 0; 
		fileSpeed = (fileSpeed) ? fileSpeed : 0;

		fileClasses = (currentDownload) ? 'blue stripes' : 'green candelete';
		fileSpeedData = (currentDownload) ? ' - ' + fileSpeed : '';

		if (filename.length > 50) {
			middle = filename.length / 2;
			displayFilename = filename.substr(0, 25) + '[...]' + filename.substr(filename.length - 25, 25);
		} else {
			displayFilename = filename;
		} 
		
		totalDownloads++;
	
		var HTML = '';
		HTML	+= "<div style='' class='download-filename'>" + displayFilename + fileSpeedData + "</div>";
		HTML	+= "<div style='height: 35px;' class='downloadStatus' id='currentDownload." + totalDownloads + "' filename='" + filename + "' fileUrl='" + fileURL.replace(/'/g, "-") + "'>";
		HTML	+= "	<div style='float: left;' class='progress-bar " + fileClasses + "'><span class='progress-percent' style='width: " + filePercent + "%'><nobr>" + filePercent + " %</nobr></span></div>";
		HTML	+= "</div>";

		if (currentDownload)
			$('div#currentDownloads').append(HTML);
		else
			$('div#completedDownloads').append(HTML);
	},
	
	update: function(filename, fileURL, filePercent, fileSpeed)
	{
		filePercent = (filePercent) ? filePercent : 0;
		fileSpeed = (fileSpeed) ? fileSpeed : 0;
		
		if (filename.length > 50) {
			middle = filename.length / 2;
			displayFilename = filename.substr(0, 25) + '[...]' + filename.substr(filename.length - 25, 25);
		} else {
			displayFilename = filename;
		} 
		
		var downloadElement = download.returnDivElement(fileURL);
		
		$(downloadElement).children().children().html('<nobr>' + filePercent + ' %</nobr>');
		$(downloadElement).children().children().css('width', filePercent + '%');

		if (download.returnDivElement_Completed(fileURL) === false)
			$(downloadElement).prev().html(displayFilename + ' - ' + fileSpeed);
		
		if ((filePercent >= 100) && (download.returnDivElement_Completed(fileURL) === false))
		{
			$(downloadElement).prev().remove();
			$(downloadElement).remove();
			download.display(false, filename, fileURL, filePercent);
		}
	},
	
	returnDivElement: function(fileURL) {
		var foundElement = false;
		
		$('.downloadStatus').each(function(downloadIndex, downloadElement) {
			if ($(downloadElement).attr('fileurl').replace(/'/g, "-") == fileURL.replace(/'/g, "-"))
				foundElement = $(downloadElement);
		});
		
		return foundElement;
	},
	
	returnDivElement_Completed: function(fileURL) {
		var foundElement = false;
		
		$('#completedDownloads .downloadStatus').each(function(downloadIndex, downloadElement) {
			if ($(downloadElement).attr('fileurl') == fileURL)
				foundElement = $(downloadElement);
		});
		
		return foundElement;
	},
	
	updateSpaceData: function(free_space, total_space) {
		percent = (free_space * 100) / total_space;
		percent = percent.toFixed(2);
		
		$('#freespace-bar').css('width', percent + '%');
		$('#freespace-bar').html('<nobr>' + free_space + ' Gb available / ' + total_space + ' Gb total</nobr>');
	},
	
	getAllStatuses: function() {
		$.getJSON('/check-dl', null, function(ajaxReturn) {
			var space_data = ajaxReturn[0];
			var free_space = space_data[0];
			var total_space = space_data[1]
			var tasks_list = ajaxReturn[1];
			
			download.updateSpaceData(free_space, total_space);
			
			$.each(tasks_list, function(downloadIndex, downloadElement) {
				downloadElement.fileURL  		= downloadElement[0];
				downloadElement.filename 		= downloadElement[1];
				downloadElement.filetype		= downloadElement[2];
				downloadElement.filesize		= downloadElement[3];
				downloadElement.downloaded		= downloadElement[4];
				downloadElement.downloadStatus	= downloadElement[5];
				downloadElement.downloadCheck	= downloadElement[6];
				downloadElement.downloadSpeed	= downloadElement[7];
				downloadElement.downloadPercent = downloadElement[8];
				
				divElement = download.returnDivElement(downloadElement.fileURL);
				if (divElement !== false)
				{
					download.update(downloadElement.filename, downloadElement.fileURL, downloadElement.downloadPercent, downloadElement.downloadSpeed);
				}
				else
				{
					// Create Div
					var Completed = (downloadElement.downloadStatus == '3') ? true : false;
					download.display(!Completed, downloadElement.filename, downloadElement.fileURL, downloadElement.downloadPercent, downloadElement.downloadSpeed);
				}

			});
		});
	}
	
};

setInterval(function() {
	download.getAllStatuses();
}, 5000);

download.getAllStatuses();