(function() {
    // The width and height of the captured photo. We will set the
    // width to the value defined here, but the height will be
    // calculated based on the aspect ratio of the input stream.

    var iconSize = 32;

    var queryUrl = '/query'; // 'http://snsoffice.com:9092/query'
    var settings = null;
    var locateresult = null;

    var spotx, spoty, spota;

    var visitor = {
        element: null,
        x: 0,
        y: 0,
        angle: 0
    };
    var anchor = {
        element: null,
        x: 0,
        y: 0,
        angle: 0
    };

    // 图片信息
    var house = {
        element: null,
        width: 3021,
        height: 2280,
        // orig: [1826, 1362],
        // resolution: 3.3,
        orig: [1840, 1228],
        resolution: 4.0,
    };

    function initSettings() {
        document.getElementById('focalinput').value = navigator.userAgent.indexOf('iPhone') == -1 ? '3.5' : '4.2';
        document.getElementById('sizeinput').value = '3.6,4.8';
    }

    function resetHouse() {
        house.resolution = house.width / house.element.clientWidth;
        house.imageSize = [house.element.clientWidth, house.element.clientHeight];
    }

    function resetOrigin() {
        var element = document.getElementById('origin');
        element.style.left = (house.orig[0] / house.resolution - iconSize / 2) + 'px';
        element.style.top = (house.orig[1] / house.resolution - iconSize / 2) + 'px';
        // element.scrollIntoView();
    }

    var houseGrid = {
        width: 2139,            // 行宽
        height: 1786,            // 列高
        top: 80,                // 第 0 行距离房子原点的偏移量
        left: 300,              // 中间区域的左边偏移，相对于房子原点
        right: 50,              // 大厅右边的墙的宽度
        bottom: 250,            // 大厅下方的空白距离
        row: [ 20, 80, 80, 80, 80, 80, 80, 80, 80, 80],       // 大厅南面每一行的高度
        rowCenter: [ 80, 80, 80, 80],                         // 中间区域每一行的高度
        rowNorth: [ 20, 80, 80, 80, 80, 80, 80, 80, 80, 80],  // 北面区域每一行的高度
        col: [ 80, 80, 80, 80, 80, 80, 80, 80, 80],           // 中间区域的列宽
        colLeft: [ 20, 80, 80, 80, 80, 80, 80, 80, 80],       // 左边区域的列宽，从右向左
        colRight: [ 20, 80, 80, 80, 80, 80, 80, 80, 80, 20],  // 右边区域的列宽，从左往右
    };

    function createHouseGrid() {
        var container = house.element.parentElement;
        var n = houseGrid.row.length;
        for (var i=0; i<n; i++) {
            var row = document.createElement('DIV');
            row.className = 'house-grid house-row house-south';
            row.style.height = '2px';
            if (i)
                row.textContent = i;
            container.appendChild(row);
        }
        n = houseGrid.rowCenter.length;
        for (var i=0; i<n; i++) {
            var row = document.createElement('DIV');
            row.className = 'house-grid house-row house-center';
            row.style.height = '2px';
            row.textContent = i + 1;
            container.appendChild(row);
        }
        n = houseGrid.rowNorth.length;
        for (var i=0; i<n; i++) {
            var row = document.createElement('DIV');
            row.className = 'house-grid house-row house-north';
            row.style.height = '2px';
            if (i)
                row.textContent = i;
            container.appendChild(row);
        }
        n = houseGrid.col.length;
        for (var i=0; i<n; i++) {
            var col = document.createElement('DIV');
            col.className = 'house-grid house-col house-center';
            col.style.width = '2px';
            col.textContent = i + 1;
            container.appendChild(col);
        }
        n = houseGrid.colLeft.length;
        for (var i=0; i<n; i++) {
            var col = document.createElement('DIV');
            col.className = 'house-grid house-col house-left';
            col.style.width = '2px';
            if ( i )
                col.textContent = i;
            container.appendChild(col);
        }
        n = houseGrid.colRight.length;
        for (var i=0; i<n; i++) {
            var col = document.createElement('DIV');
            col.className = 'house-grid house-col house-right';
            col.style.width = '2px';
            if ( i )
                col.textContent = i;
            container.appendChild(col);
        }
    }

    function resetHouseGrid() {
        var r = house.resolution;
        var container = house.element.parentElement;

        var top = house.orig[1] + houseGrid.top;
        var left = parseInt((house.width - houseGrid.width - houseGrid.right) / r) + 'px';
        var width = parseInt(houseGrid.width / r) + 'px';
        if (1) {
            var rows = container.querySelectorAll('.house-grid.house-row.house-south');
            var n = houseGrid.row.length;
            for (var i=0; i<n; i++) {
                row = rows[i];
                row.style.left = left;
                row.style.top = parseInt(top / r) + 'px';
                row.style.width = width;
                top += houseGrid.row[i];
            }
        }
        if (2) {
            var rows = container.querySelectorAll('.house-grid.house-row.house-center');
            var n = houseGrid.rowCenter.length;
            top = house.orig[1] + houseGrid.top;
            for (var i=0; i<n; i++) {
                top -= houseGrid.rowCenter[i];
                row = rows[i];
                row.style.left = left;
                row.style.top = parseInt(top / r) + 'px';
                row.style.width = width;
            }
        }
        if (3) {
            var rows = container.querySelectorAll('.house-grid.house-row.house-north');
            var n = houseGrid.rowNorth.length;
            for (var i=0; i<n; i++) {
                top -= houseGrid.rowNorth[i];
                row = rows[i];
                row.style.left = left;
                row.style.top = parseInt(top / r) + 'px';
                row.style.width = width;
            }
        }

        var height = parseInt(houseGrid.height / r) + 'px';
        var left = house.orig[0] - houseGrid.left;
        var top = parseInt((house.height - houseGrid.height - houseGrid.bottom) / r) + 'px';
        var padding = parseInt(houseGrid.height * 0.6 / r) + 'px';
        if (1) {
            var cols = container.querySelectorAll('.house-grid.house-col.house-center');
            var n = houseGrid.col.length;
            for (var i=0; i<n; i++) {
                col = cols[i];
                col.style.left = parseInt(left / r) + 'px';
                col.style.top = top;
                col.style.height = height;
                col.style.paddingTop = padding;
                left += houseGrid.col[i];
            }
        }
        if (2) {
            var cols = container.querySelectorAll('.house-grid.house-col.house-right');
            var n = houseGrid.colRight.length;
            for (var i=0; i<n; i++) {
                col = cols[i];
                col.style.left = parseInt(left / r) + 'px';
                col.style.top = top;
                col.style.height = height;
                col.style.paddingTop = padding;
                left += houseGrid.colRight[i];
            }
        }
        if (3) {
            var left = house.orig[0] - houseGrid.left;
            var cols = container.querySelectorAll('.house-grid.house-col.house-left');
            var n = houseGrid.colLeft.length;
            for (var i=0; i<n; i++) {
                left -= houseGrid.colLeft[i];
                col = cols[i];
                col.style.left = parseInt(left / r) + 'px';
                col.style.top = top;
                col.style.height = height;
                col.style.paddingTop = padding;
            }
        }
    }


    function startup() {

        initSettings();

        settings = document.getElementById('settings');
        spotx = document.getElementById('spotxinput');
        spoty = document.getElementById('spotyinput');
        spota = document.getElementById('spotainput');
        locateresult = document.getElementById('result');

        visitor.element = document.getElementById('visitor');
        anchor.element = document.getElementById('anchor');
        house.element = document.getElementById('house');
        house.element.style.opacity = 0.8;
        createHouseGrid();

        anchor.element.style.visibility = 'hidden';
        anchor.element.style.transformOrigin = 'bottom center';
        resetHouse();
        resetHouseGrid();
        resetOrigin();
        locateresult.style.height = locateresult.clientHeight + 'px';
        locateresult.style.overflow = 'auto';

        var map = document.getElementById('map');
        map.style.height = (window.innerHeight - map.nextElementSibling.clientHeight) + 'px';
        map.style.width = window.innerWidth + 'px';

        document.getElementById('locatebutton').addEventListener('click', function(ev){
            ev.preventDefault();
            startQueryLocation();            
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

        house.element.addEventListener('click', function (e) {
            setVisitorPosition(e.offsetX, e.offsetY);
            e.preventDefault();
        }, false);

        var onSpotChanged = function (e) {
            e.preventDefault();
            var x = parseInt(spotx.value);
            var y = parseInt(spoty.value);
            if (isNaN(x) || isNaN(y))
                return;
            var pos = house2img(x, y);
            setVisitorPosition(pos[0], pos[1]);
            // visitor.element.scrollIntoView();
        };
        spotx.addEventListener('change', onSpotChanged, false);
        spoty.addEventListener('change', onSpotChanged, false);

        var onSpotClicked = function (e) {
            e.preventDefault();
            var elements = document.querySelectorAll('.controls input.form-control');
            for (var i = 0; i < elements.length; i ++)
                elements[i].className = 'form-control';
            this.className = 'form-control active';
        };
        spotx.addEventListener('click', onSpotClicked, false);
        spoty.addEventListener('click', onSpotClicked, false);
        spota.addEventListener('click', onSpotClicked, false);

        document.addEventListener( 'click', function ( e ) {
            var tag = e.target.tagName;
            if (tag !== 'INPUT' && tag !== 'A' && tag !== 'BUTTON')
                document.getElementById('message').style.visibility = 'hidden';
        }, false );

        document.getElementById('incbutton').addEventListener('click', function (ev) {
            size = house.imageSize;
            size[0] = parseInt(size[0] * 1.1);
            size[1] = parseInt(size[1] * 1.1);
            house.element.width = size[0];
            house.element.height = size[1];
            house.resolution = house.width / size[0];
            resetHouseGrid();
            resetOrigin();
            onSpotChanged(ev);
            placeAnchor(anchor.x, anchor.y);
        }, false);
        document.getElementById('decbutton').addEventListener('click', function (ev) {
            size = house.imageSize;
            size[0] = parseInt(size[0] / 1.1);
            size[1] = parseInt(size[1] / 1.1);
            house.element.width = size[0];
            house.element.height = size[1];
            house.resolution = house.width / size[0];
            resetHouseGrid();
            resetOrigin();
            onSpotChanged(ev);
            placeAnchor(anchor.x, anchor.y);
        }, false);

    }

    function showMessage( msg ) {
        var className = 'info';
        var element = document.getElementById('message');
        element.innerHTML = '<div class="alert alert-' + className + '" role="alert">' +
            '<button type="button" class="close" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
            msg + '</div>';
        // element.style.visibility = 'visible';
        locateresult.innerHTML = msg;
    };

    function startQueryLocation() {
        var fileinput = document.createElement('INPUT');
        fileinput.setAttribute('type', 'file');
        fileinput.addEventListener('change', function(e){
            if (!this.files.length)
                return;
            fileLocate(this.files[0]);
        }, false);
        var e = document.createEvent('MouseEvent');     
        e.initEvent('click', false, false);
        fileinput.dispatchEvent(e);        
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

    function fileLocate( file ) {
        anchor.element.style.visibility = 'hidden';
        var reader = new FileReader();
        reader.addEventListener("loadend", function(evt) {
            EXIF.getData(file, function () {
                var make = EXIF.getTag(this, "Make");
                var model = EXIF.getTag(this, "Model");
                var fc = EXIF.getTag(this, "FocalLength");
                var url = buildQueryUrl(make, model, fc);
                if (url === null)
                    return;

                showMessage('开始上传图片...');
                sendRequest( url, reader.result, function ( data ) {
                    showResult(data);
                });
            });
        });
        showMessage('准备上传图片...');
        reader.readAsArrayBuffer(file);
    }

    function queryLocation() {
        var canvas = document.createElement('CANVAS');
        var context = canvas.getContext('2d');
        if (width && height) {
            var w = width, h = height;
            canvas.width = w;
            canvas.height = h;
            // flip image
            context.translate(0, h);
            context.scale(1, -1);

            context.drawImage(video, 0, 0, w, h);

            canvas.toBlob(function(blob) {
                var reader = new FileReader();
                reader.addEventListener("loadend", function(evt) {
                    // reader.result contains the contents of blob as a typed array
                    sendRequest( queryUrl, reader.result, function ( data ) {
                        showResult(data);
                    });
                }, 'image/jpeg', 1.0);
                reader.readAsArrayBuffer(blob);
            });
        }
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

    function img2house(x, y) {
        var r = house.resolution;
        var orig = house.orig;
        x *= r;
        y *= r;
        x -= orig[0];
        y -= orig[1];
        return [x, -y];
    }

    function house2img(x, y) {
        var r = house.resolution;
        var orig = house.orig;
        x += orig[0];
        y = -y + orig[1];
        return [x/r, y/r];
    }

    function setVisitorPosition(x, y) {
        var pos = img2house(x, y);
        document.getElementById('spotxinput').value = pos[0].toFixed(0);
        document.getElementById('spotyinput').value = pos[1].toFixed(0);
        visitor.x = pos[0];
        visitor.y = pos[1];
        visitor.element.style.left = (x - iconSize / 2) + 'px';
        visitor.element.style.top = (y - iconSize) + 'px';
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
})();
