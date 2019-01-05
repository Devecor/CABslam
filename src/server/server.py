# -*- coding: utf-8 -*-
#! /usr/bin/env python
from __future__ import print_function

import glob
import logging
import json
import os
import posixpath
import shutil
import sys
from time import strftime

import numpy as np
import cv2

sys.path.append('..')
import config
config.base_data_path = '../data'
from istar import locate_image_in_region
from verify.check_feature import main as detect_features
from verify.check_match import main as match_features

try:
    from urllib import unquote
    from urlparse import urlparse, parse_qsl
except Exception:
    from urllib.parse import unquote, urlparse, parse_qsl
try:
    from BaseHTTPServer import BaseHTTPRequestHandler
except ImportError:
    from http.server import BaseHTTPRequestHandler
try:
    import SocketServer as socketserver
except ImportError:
    import socketserver

__version__ = '0.1'
__log_path__ = 'test-images'
__prev_path__ = 'preview'

class Arguments(dict):
    def __getattr__(self, name):
        return self[name]

class HelperHandler(BaseHTTPRequestHandler):
    '''Based on SimpleHTTPRequestHandler'''

    server_version = "HelperHTTP/" + __version__

    def do_POST(self):
        """Serve a POST request."""
        if self.path.startswith('/preview'):
            params = dict(parse_qsl(urlparse(self.path).query))
            try:
                result = self.preview_images(params)
            except Exception as e:
                result = dict(errcode=1, result=str(e))
            self.send_result(result)
            return

        if self.path.startswith('/detect'):
            params = dict(parse_qsl(urlparse(self.path).query))
            result = self.detect_features(params)
            self.send_result(result)
            return

        if self.path.startswith('/match'):
            params = dict(parse_qsl(urlparse(self.path).query))
            result = self.match_features(params)
            self.send_result(result)
            return

        if not (self.path.startswith('/query') or self.path.startswith('/upload')):
            self.send_error(404, "File not found")
            return

        n = int(self.headers.get('Content-Length', 0))
        t = self.headers.get('Content-Type', 'text/json;charset=UTF-8')
        if n == 0:
            imagedata = bytearray('')
        else:
            imagedata = bytearray(self.rfile.read(n))

        # self.log_message("Arguments '%s'", type(imagedata))
        name = strftime('img-%Y%m%d-%H%M%S')
        filename = os.path.join(__log_path__, name + '.jpg')
        with open(filename, 'wb') as f:
            f.write(imagedata)

        # this way doesn't work
        # imagedata = cv2.imdecode(np.array(imagedata), cv2.IMREAD_GRAYSCALE)
        imagedata = cv2.imread(filename, 0)

        preview = os.path.join(__prev_path__, name + '.jpg')
        previewSize = 180, 240
        cv2.imwrite(preview, cv2.resize(imagedata, previewSize))

        if self.path.startswith('/upload'):
            response = json.dumps(dict(filename=filename)).encode()
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.send_header("Content-Length", str(len(response)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Last-Modified", self.date_time_string())
            self.end_headers()
            self.wfile.write(response)
            return


        params = dict(parse_qsl(urlparse(self.path).query))
        result = self.query_location(params, imagedata)
        self.send_result(result)

        # Log result
        filename = os.path.join(__log_path__, name + '.json')
        with open(filename, 'w') as f:
            params['user-agent'] = self.headers.getheader('user-agent');
            params['result'] = result;
            json.dump(params, f)

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def send_result(self, result):
        if result is None:
            self.send_error(501, "Server internal error")
        else:
            response = json.dumps(result).encode()
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.send_header("Content-Length", str(len(response)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Last-Modified", self.date_time_string())
            self.end_headers()
            self.wfile.write(response)

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                self.send_error(404, "File not found")
                return None
        # if os.path.basename(path) not in (
        #         'bootstrap.min.css', 'bootstrap.min.js', 'jquery.min.js',
        #         'pyarmor.js', 'index.html'):
        #     self.send_error(404, "File not found")
        #     return None

        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def query_location(self, params, image):
        try:
            args = Arguments(params)
            pose = locate_image_in_region(args, image)
            if pose is None:
                errcode = 1
                result = '没有匹配的参考照片'
            else:
                result = dict(x=pose[1][0], y=pose[1][2], angle=pose[0])
                errcode = 0
        except Exception as e:
            errcode = 1
            result = "服务器错误信息: %s" % str(e)
            logging.exception("Unhandle Server Error")
        return dict(errcode=errcode, result=result)

    def detect_features(self, params):
        filename = params.get('filename')
        if filename is None:
            return dict(errcode=1, result="缺少图片文件名称")
        output = 'features'

        args = [ '--save', '--output', output ]
        mask = params.get('mask')
        if mask:
            args.extend(['--mask', mask])
        tilt = params.get('tilt', '0')
        if tilt != '0':
            args.extend(['--asift', '--tilt', tilt])
        n = params.get('nFeatures')
        if n:
            args.extend(['--nFeatures', n])
        args.append(filename)
        try:
            detect_features(args)
        except Exception as e:
            return dict(errcode=1, result=str(e))

        asift = '' if tilt == '0' else 'asift.'
        destname = filename[:filename.rfind('.')] + '-' + asift + 'orb.jpg'
        destname = os.path.join(output, os.path.basename(destname))
        return dict(errcode=0, filename=destname)

    def match_features(self, params):
        trainimage = params.get('trainimage')
        queryimage = params.get('queryimage')
        if trainimage is None or queryimage is None:
            return dict(errcode=1, result="缺少图片文件名称")

        output = 'features'
        args = [ '--save', '--output', output, '--path', output ]
        suffix = params.get('suffix', 'asift.orb,orb')
        # if tilt == '0':
        #     suffix = 'asift.orb,orb'
        # else:
        #     suffix = 'asift.orb,asift.orb'
        args.extend(['--suffix', suffix])
        args.append(trainimage)
        args.append(queryimage)
        try:
            match_features(args)
        except Exception as e:
            return dict(errcode=1, result=str(e))

        filename = '%s-%s.jpg' % (trainimage.rsplit('.')[0], os.path.basename(queryimage).rsplit('.')[0])
        filename = os.path.join(output, os.path.basename(filename))
        return dict(errcode=0, filename=filename)

    def preview_images(self, params):
        result = {}
        start = int(params.get('start', '1'))
        size = int(params.get('size', '10'))
        files = glob.glob(os.path.join(__prev_path__, '*.jpg'))
        files.sort()
        files.reverse()
        result['errcode'] = 0
        result['start'] = start
        result['size'] = size
        result['files'] = files[(start-1)*size:start*size]
        result['count'] = len(result['files'])
        result['sep'] = os.sep
        result['path'] = __log_path__
        return result

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']
    extensions_map = {
        '': 'application/octet-stream', # Default
        '.css': 'text/css',
        '.html': 'text/html',
        '.js': 'application/x-javascript',
        }

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
    )
    if not os.path.exists(__log_path__):
        os.mkdir(__log_path__)

    try:
        PORT = int(sys.argv[1])
    except Exception:
        PORT = 9092
    server = socketserver.TCPServer(("", PORT), HelperHandler)
    print("Serving HTTP on %s port %s ..." % server.server_address)
    # try:
    #     from webbrowser import open_new_tab
    #     open_new_tab("http://localhost:%d" % server.server_address[1])
    # except Exception:
    #     pass
    server.serve_forever()
