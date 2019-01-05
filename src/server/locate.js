(function() {
    // The width and height of the captured photo. We will set the
    // width to the value defined here, but the height will be
    // calculated based on the aspect ratio of the input stream.

    var locateUrl = '/query'; // 'http://snsoffice.com:9092/query'
    var locateresult = null;
    var video = {
        element: null,
        width: 320,
        height: 240
    };

    function initSettings() {
        document.getElementById('focalinput').value = navigator.userAgent.indexOf('iPhone') == -1 ? '3.5' : '4.2';
        document.getElementById('sizeinput').value = '3.6,4.8';
    }

    function startup() {

        initSettings();

        video.element = document.getElementById('video');
        locateresult = document.querySelector('p.navbar-text');

        document.getElementById('browse').addEventListener('click', function(ev){
            selectVideo();
            ev.preventDefault();
        }, false);

        document.getElementById('play').addEventListener('click', function(ev){
            ev.preventDefault();
            if (video.element.paused)
                video.element.play();
            else
                video.element.pause();
        }, false);

        document.getElementById('locate').addEventListener('click', function(ev){
            video.element.pause();
            queryLocation();
            ev.preventDefault();
        }, false);

        video.element.addEventListener( 'pause', function ( e ) {
            document.getElementById('play').textContent = '播放';
        }, false );

        video.element.addEventListener( 'ended', function ( e ) {
            document.getElementById('play').textContent = '播放';
        }, false );

        video.element.addEventListener( 'playing', function ( e ) {
            document.getElementById('play').textContent = '暂停';
        }, false );

    }

    function selectVideo(){
        var fileinput = document.createElement('INPUT');
        fileinput.setAttribute('type', 'file');
        fileinput.addEventListener('change', function(e){
            if (!this.files.length)
                return;
            loadVideo(this.files[0]);
        }, false);
        var e = document.createEvent('MouseEvent');
        e.initEvent('click', false, false);
        fileinput.dispatchEvent(e);
    }

    function loadVideo(file){
    
        if ((!file.type.startsWith('video/')) && (!file.type.startsWith('audio/')))
            return;
    
        var reader = new FileReader();
        reader.onload = function(e) {
            video.element.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    function showMessage( msg ) {
        locateresult.innerHTML = msg;
    };

    function startQueryLocation() {
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

    function buildQueryUrl(make, model, fc) {
        if (!fc) {
            fc = document.getElementById('focalinput').value;
            if (!fc) {
                showMessage('缺少相片焦距数据，请点击设置，输入相机焦距');
                return null;
            }
        }
        var size = document.getElementById('sizeinput').value;

        var params = [];
        params.push('building=' + document.getElementById('buildinginput').value);
        params.push('region=' + document.getElementById('regioninput').value);
        params.push('focal=' + fc);
        params.push('size=' + size);
        params.push('mode=' + document.getElementById('modeinput').value);
        params.push('spot=' + [spotx.value, spoty.value, spota.value].join(','));
        url = queryUrl + '?' + params.join('&');
        return url;
    }

    function queryLocation() {
        var canvas = document.createElement('CANVAS');
        var context = canvas.getContext('2d');
        var w = video.width, h = video.height;
        canvas.width = w;
        canvas.height = h;
        // flip image
        context.translate(0, h);
        context.scale(1, -1);

        context.drawImage(video.element, 0, 0, w, h);

        canvas.toBlob(function(blob) {
            var reader = new FileReader();
            reader.addEventListener("loadend", function(evt) {
                sendRequest( locateUrl, reader.result, function ( data ) {
                    showResult(data);
                });
            }, 'image/jpeg', 1.0);
            reader.readAsArrayBuffer(blob);
        });
    }

    function placeAnchor(x, y) {
        var p2 = house2img(x, y)
        anchor.element.style.left = (p2[0] - iconSize / 2) + 'px';
        anchor.element.style.top = (p2[1] - iconSize) + 'px';
    }

    function showResult(data) {
        if (data.errcode) {
            showMessage('定位失败：' + data.result);
            return;
        }
        var pose = data.result;
        var x = pose.x;
        var y = pose.y;
        var a = pose.angle;
        var dx = x - visitor.x;
        var dy = y - visitor.y;
        var da = a - visitor.angle;
        var dt = Math.sqrt(dx*dx + dy*dy);
        if (x > house.width - house.orig[0] + 200 || x < - house.orig[0]
            || y > house.orig[1] || y < house.orig[1] - house.width) {
            showMessage('定位失败： 返回的定位结果在建筑物之外');
            return;
        }
        showMessage('定位结果: ' + x.toFixed(2) + 'cm / ' + y.toFixed(2) + 'cm / ' + a.toFixed(2) + '度 <br>' +
                    '定位误差: ' + dx.toFixed(2) + 'cm / ' + dy.toFixed(2) + 'cm ' +
                    '<span style="color: red"> ( ' + dt.toFixed(2) + 'cm )</span>');

        anchor.x = x;
        anchor.y = y;
        anchor.angle = a;
        placeAnchor(x, y);
        anchor.element.style.transform = 'rotate(' + a + 'deg)';
        anchor.element.style.visibility = 'visible';
        anchor.element.scrollIntoView();
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
                    showMessage('图片上传完毕，正在定位...');
                else {
                    var percentage = Math.round((e.loaded * 100) / e.total);
                    showMessage('正在上传图片（共' + (e.total / 1024 / 1024).toFixed(2) + 'M): ' + percentage + '% ...');
                }
            }
        }, false);

        request.upload.addEventListener("loadend", function(e){
            if (e.total === e.loaded)
                showMessage('图片上传完毕，正在定位...');
            else
                showMessage('图片上传出现错误');
        }, false);

        request.upload.addEventListener("error", function(e) {
            showMessage('图片上传出现错误');
        }, false);

        request.onerror = onError;
        request.onload = function() {
            if (request.status != 200) {
                showMessage('服务器无法定位，返回错误代码: ' + request.status);
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

    // A low performance polyfill based on toDataURL.
    if (!HTMLCanvasElement.prototype.toBlob) {
        Object.defineProperty(HTMLCanvasElement.prototype, 'toBlob', {
            value: function (callback, type, quality) {
                var canvas = this;
                setTimeout(function() {

                    var binStr = atob( canvas.toDataURL(type, quality).split(',')[1] ),
                    len = binStr.length,
                    arr = new Uint8Array(len);

                    for (var i = 0; i < len; i++ ) {
                        arr[i] = binStr.charCodeAt(i);
                    }

                    callback( new Blob( [arr], {type: type || 'image/png'} ) );

                });
            }
        });
    }

})();
