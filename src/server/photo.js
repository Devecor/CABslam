(function() {

    var settings;
    var leftCorner = null;
    var anchor = null;
    var mask = null;
    var selectbox = null;

    var matchpage = null;
    var trainImageName = null;

    var selectpage = null;

    var photoContainer;
    var photo = null;
    var imageName = null;
    var uploaded = false;

    var imageWidth, imageHeight;
    var scale = 1.0;

    var currentPage = 0, pageSize = 10;

    function basename(fullname) {
        var index = fullname.lastIndexOf('/');
        if (index === -1)
            index = fullname.lastIndexOf('\\');
        return fullname.substring(index + 1);
    }

    function startup() {

        selectpage = document.getElementById('selectpage');
        matchpage = document.getElementById('matchpage');
        settings = document.getElementById('settings');
        mask = document.getElementById('mask');
        selectbox = document.getElementById('selectbox');
        selectbox.style.visibility = 'hidden';

        photoContainer = document.querySelector('.photo-container');
        photoContainer.style.height = (window.innerHeight - document.querySelector('div.controls').clientHeight) + 'px';

        var output = document.querySelector('#output');
        output.style.height = output.clientHeight + 'px';
        output.style.overflow = 'auto';

        document.getElementById('take-photo').addEventListener('click', function(ev){
            ev.preventDefault();
            takePhoto();
        }, false);

        document.getElementById('upload').addEventListener('click', function(ev){
            ev.preventDefault();
            uploadPhoto();
        }, false);

        document.getElementById('toggle-photo').addEventListener('click', function(ev){
            ev.preventDefault();
            togglePhoto();
        }, false);

        document.getElementById('query-feature').addEventListener('click', function(ev){
            ev.preventDefault();
            detectFeatures();
        }, false);

        document.getElementById('query-feature1').addEventListener('click', function(ev){
            ev.preventDefault();
            settings.style.visibility = 'hidden';
            detectFeatures();
        }, false);

        document.getElementById('settingsbutton').addEventListener('click', function(ev){
            settings.style.visibility = 'visible';
            ev.preventDefault();
        }, false);

        document.querySelector('#settings .close').addEventListener('click', function(ev){
            settings.style.visibility = 'hidden';
            ev.preventDefault();
        }, false);

        settings.addEventListener('click', function(ev){
            if (ev.target.tagName === 'DIV') {
                this.style.visibility = 'hidden';
                ev.preventDefault();
            }
        }, false);

        document.getElementById('selectbutton').addEventListener('click', function(ev){
            selectpage.style.visibility = 'visible';
            ev.preventDefault();
        }, false);

        document.querySelector('#selectpage .close').addEventListener('click', function(ev){
            selectpage.style.visibility = 'hidden';
            ev.preventDefault();
        }, false);

        selectpage.addEventListener('click', function(ev){
            if (ev.target.tagName === 'DIV') {
                this.style.visibility = 'hidden';
                ev.preventDefault();
            }
        }, false);

        document.getElementById('trainbutton').addEventListener('click', function(ev){
            if (uploaded === true && imageName) {
                trainImageName = imageName;
                document.getElementById('trainimage').textContent = basename(imageName);
                showMessage('参考图片设置为：' + trainImageName);
            }
            else
                showMessage('图片上传之后才可以作为参考图片');
            ev.preventDefault();
        }, false);

        matchpage.addEventListener('click', function(ev){
            if (ev.target.tagName === 'DIV') {
                this.style.visibility = 'hidden';
                ev.preventDefault();
            }
        }, false);

        document.getElementById('matchbutton').addEventListener('click', function(ev){
            matchpage.style.visibility = 'visible';
            document.getElementById('queryimage').textContent = basename(imageName);
            ev.preventDefault();
        }, false);

        document.getElementById('match-photo').addEventListener('click', function(ev){
            matchPhoto();
            ev.preventDefault();
        }, false);

        document.getElementById('prev-page').addEventListener('click', function(ev){
            ev.preventDefault();
            if (currentPage > 1)
                currentPage --;
            else
                currentPage = 1;
            fetchImages();
        }, false);

        document.getElementById('next-page').addEventListener('click', function(ev){
            ev.preventDefault();
            currentPage ++;
            fetchImages();
        }, false);

        document.getElementById('thumbnails').addEventListener('click', function(ev){
            ev.preventDefault();
            if (ev.target.tagName === 'IMG') {
                selectImage(ev.target.getAttribute('alt'));
                selectpage.style.visibility = 'hidden';

            }
        }, false);

    }

    function selectImage(remoteImage) {
        if (photo !== null)
            photo.remove();
        imageName = remoteImage;
        uploaded = true;

        photo = document.createElement("img");
        photo.src = remoteImage;
        photo.style.width = "100%";
        photoContainer.appendChild(photo);
        photo.addEventListener('click', function (e) {
            setMaskArea(e.offsetX, e.offsetY);
            e.preventDefault();
        }, false);

        photo.onload = function (e) {
            EXIF.getData(this, function() {
                var make = EXIF.getTag(this, "Make");
                var model = EXIF.getTag(this, "Model");
                imageWidth = parseInt(EXIF.getTag(this, "ImageWidth"));
                imageHeight = parseInt(EXIF.getTag(this, "ImageLength"));
                if (isNaN(imageWidth)) {
                    imageWidth = parseInt(EXIF.getTag(this, "PixelXDimension"));
                    imageHeight = parseInt(EXIF.getTag(this, "PixelYDimension"));
                }
                scale = imageWidth / photo.clientWidth;
            });
            photo.onload = null;
        };
        showMessage("选中服务器图片：" + remoteImage);
    }

    function togglePhoto() {
        if (photo === null)
            return;
        photo.style.width = photo.style.width ? "" : "100%";
        var s2 = scale;
        scale = photo.style.width ? imageWidth / photo.clientWidth : 1.0;
        s2 = photo.style.width ? 1 / scale : s2;
        selectbox.style.left = parseInt(parseInt(selectbox.style.left) * s2) + 'px';
        selectbox.style.top = parseInt(parseInt(selectbox.style.top) * s2) + 'px';
        selectbox.style.width = parseInt(parseInt(selectbox.style.width) * s2) + 'px';
        selectbox.style.height = parseInt(parseInt(selectbox.style.height) * s2) + 'px';
    }

    function takePhoto() {
        var fileinput = document.createElement('INPUT');
        fileinput.setAttribute('type', 'file');
        fileinput.addEventListener('change', function(e){
            if (!this.files.length)
                return;
            showImage(this.files[0]);
        }, false);
        var e = document.createEvent('MouseEvent');
        e.initEvent('click', false, false);
        fileinput.dispatchEvent(e);
    }

    function showImage( file ) {
        if (photo !== null)
            photo.remove();
        imageName = null;
        uploaded = false;

        photo = document.createElement("img");
        photo.file = file;
        photo.style.width = "100%";
        photoContainer.appendChild(photo);
        photo.addEventListener('click', function (e) {
            setMaskArea(e.offsetX, e.offsetY);
            e.preventDefault();
        }, false);

        var reader = new FileReader();
        reader.onload = (function(aImg) { return function(e) { aImg.src = e.target.result; }; })(photo);
        reader.readAsDataURL(file);

        EXIF.getData(file, function() {
            var make = EXIF.getTag(this, "Make");
            var model = EXIF.getTag(this, "Model");
            imageWidth = parseInt(EXIF.getTag(this, "ImageWidth"));
            imageHeight = parseInt(EXIF.getTag(this, "ImageLength"));
            if (isNaN(imageWidth)) {
                imageWidth = parseInt(EXIF.getTag(this, "PixelXDimension"));
                imageHeight = parseInt(EXIF.getTag(this, "PixelYDimension"));
            }
            scale = imageWidth / photo.clientWidth;
        });

        showMessage("符合要求的照片可以点击上传将图片上传到服务器<br>在点击特征，查看图片上的关键点");
    }

    function matchPhoto() {
        var result = document.querySelector('.match-container');
        if (trainImageName == null) {
            result.textContent = "请首先设置参考图片，然后在进行匹配";
            return;
        }
        if (imageName == null) {
            result.textContent = "请首先上传当前图片，并生成特征关键点，然后在进行匹配";
            return;
        }
        result.textContent = "正在匹配图片 " + trainImageName + ' : ' + imageName;

        var params = [];
        params.push('trainimage=' + trainImageName);
        params.push('queryimage=' + imageName);
        // params.push('tilt=' + document.getElementById('tilt').value);
        params.push('suffix=' + [document.getElementById('train-suffix').value, document.getElementById('query-suffix').value].join(','));
        var url = "/match?" + params.join('&');
        sendRequest( url, '', function (data) {
            if (data.errcode)
                result.textContent = data.result;
            else {
                result.textContent = '正在装载匹配结果图片...';
                var img = document.createElement('IMG');
                img.src = data.filename + "?" + Math.random();
                img.style.width = "100%";
                img.onload = function (e) {
                    showMessage('匹配结果：<a href="' + data.filename + '">' + data.filename + '</a>');
                    result.textContent = '';
                    result.appendChild(img);
                };
                img.addEventListener('click', function (e){
                    img.style.width = img.style.width ? "" : "100%";
                }, false);
            }
        });
    }

    function setMaskArea(x, y) {
        if (leftCorner === null) {
            leftCorner = [x, y];

            selectbox.style.left = x + 'px';
            selectbox.style.top = y + 'px';
            selectbox.style.width = '4px';
            selectbox.style.height = '4px';

            selectbox.style.visibility = 'visible';
            mask.value = '';
            return;
        }

        if (mask.value === '') {
            leftCorner.push(x);
            leftCorner.push(y);
            mask.value = leftCorner.map(function(x){return parseInt(x*scale);}).join(',');
            selectbox.style.width = (x - leftCorner[0]) + 'px';
            selectbox.style.height = (y - leftCorner[1]) + 'px';
            return;
        }
        selectbox.style.visibility = 'hidden';
        leftCorner = null;
        mask.value = null;
    }

    function showMessage( msg ) {
        var element = document.getElementById('output');
        element.innerHTML = msg;
    };

    function uploadPhoto() {
        if (uploaded === true) {
            showMessage("图片已经上传!");
            return;
        }
        if (photo === null) {
            showMessage("请首先拍照，然后在点击上传");
            return;
        }

        showMessage("正在准备上传图片...");
        var reader = new FileReader();
        reader.addEventListener("loadend", function(evt) {
            var url = "/upload";
            sendRequest( url, reader.result, function ( data ) {
                uploaded = true;
                imageName = data.filename;
                showMessage("图片已经被保存到服务器： " + imageName);
            });
        }, false);
        reader.readAsArrayBuffer(photo.file);
    }

    function detectFeatures() {
        if (imageName == null) {
            showMessage("请首先上传图片之后，然后在查看特征");
            return;
        }
        var params = [];
        params.push('filename=' + imageName);
        var tilt = document.getElementById('tilt').value;
        params.push('tilt=' + tilt);
        var n = document.getElementById(tilt === '0' ? 'nFeatures' : 'nAsiftFeatures').value;
        params.push('nFeatures=' + n);
        if (mask.value)
            params.push('mask=' + mask.value);
        var url = "/detect?" + params.join('&');

        showMessage("正在查询图片特征关键点...<br>" + (tilt === '0' ? 'orb' : 'asift, tilt=' + tilt) + ', nFeatures=' + n);
        sendRequest( url, '', function (result) {
            if (result.errcode)
                showMessage(result.result);
            else {
                showMessage('正在装载特征图片文件：<a href="' + result.filename + '">' + result.filename + '</a>...');
                photo.src = result.filename + "?" + Math.random();
                photo.onload = function (e) {
                    showMessage('特征图片文件：<a href="' + result.filename + '">' + result.filename + '</a>');
                };
            }
        });
    }

    function fetchImages() {
        var thumbnails = document.getElementById('thumbnails');
        thumbnails.textContent = "正在查询服务器图片...";

        var params = [];
        params.push('start=' + currentPage);
        params.push('size=' + pageSize);
        var url = "/preview?" + params.join('&');
        sendRequest( url, '', function (data) {
            if (data.errcode)
                thumbnails.textContent = data.result;
            else {
                var items = ['<div class="row">'];                
                var sep = data.sep;
                var path = data.path;
                document.getElementById('next-page').disabled = data.count < data.size;
                data.files.forEach( function (filename) {
                    var index = filename.lastIndexOf(sep);
                    var name = filename.substring(index + 1);
                    var altname = path + filename.substring(index);
                    items.push('<div class="col-xs-6 col-sm-2 col-md-1">' +
                               '  <div class="thumbnail">' +
                               '    <img src="' + filename + '" alt="' + altname + '">' +
                               // '    <div class="caption">' +
                               // '      <h3>' + name + '</h3>' +
                               // '    </div>' +
                               '  </div>' +
                               '</div>');
                });
                items.push('</div>');
                thumbnails.innerHTML = items.join('');
            }
        });
    }

    function getExif(file) {
        EXIF.getData(file, function() {
            var make = EXIF.getTag(this, "Make");
            var model = EXIF.getTag(this, "Model");
            var fc = EXIF.getTag(this, "FocalLength");
            var sx = EXIF.getTag(this, "FocalPlaneXResolution");
            var sy = EXIF.getTag(this, "FocalPlaneYResolution");
            var su = EXIF.getTag(this, "FocalPlaneResolutionUnit");
        });
    }

    function onError(e) {
        showMessage('服务器错误：' + e);
    }

    function sendRequest(url, args, callback) {

        var data = args;
        var request = new XMLHttpRequest();

        request.upload.addEventListener("progress", function(e) {
            if (e.lengthComputable) {
                if (e.total === e.loaded)
                    showMessage('图片上传完毕');
                else {
                    var percentage = Math.round((e.loaded * 100) / e.total);
                    showMessage('正在上传图片（共' + (e.total / 1024 / 1024).toFixed(2) + 'M): ' + percentage + '% ...');
                }
            }
        }, false);

        request.upload.addEventListener("loadend", function(e){
            if (e.total === e.loaded)
                showMessage('图片上传完毕');
            else
                showMessage('图片上传出现错误');
        }, false);

        request.upload.addEventListener("error", function(e) {
            showMessage('图片上传出现错误');
        }, false);

        request.onerror = onError;
        request.onload = function() {
            if (request.status != 200) {
                showMessage('上传失败，返回错误代码: ' + request.status);
                return;
            }

            if (typeof callback === 'function')
                callback(JSON.parse(request.responseText));
        };
        request.overrideMimeType('text/plain; charset=x-user-defined-binary');
        request.open('POST', url, true);
        request.send(data);
    }

    // Set up our event listener to run the startup process
    // once loading is complete.
    window.addEventListener('load', startup, false);
})();
