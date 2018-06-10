; (function () {
    "use strict"

    // 兼容IE9
    if ((typeof Range !== "undefined") && !Range.prototype.createContextualFragment) {
        Range.prototype.createContextualFragment = function (html) {
            var frag = document.createDocumentFragment(),
                div = document.createElement("div");
            frag.appendChild(div);
            div.outerHTML = html;
            return frag;
        };
    }

    //ie版本号
    var ieVersion = (function () {
        var userAgent = navigator.userAgent; //取得浏览器的userAgent字符串  
        var isIE = userAgent.indexOf("compatible") > -1 && userAgent.indexOf("MSIE") > -1; //判断是否IE<11浏览器  
        var isEdge = userAgent.indexOf("Edge") > -1 && !isIE; //判断是否IE的Edge浏览器  
        var isIE11 = userAgent.indexOf('Trident') > -1 && userAgent.indexOf("rv:11.0") > -1;
        if (isIE) {
            var reIE = new RegExp("MSIE (\\d+\\.\\d+);");
            reIE.test(userAgent);
            var fIEVersion = parseFloat(RegExp["$1"]);
            if (fIEVersion == 7) {
                return 7;
            } else if (fIEVersion == 8) {
                return 8;
            } else if (fIEVersion == 9) {
                return 9;
            } else if (fIEVersion == 10) {
                return 10;
            } else {
                return 6;//IE版本<=7
            }
        } else if (isEdge) {
            return 'edge';//edge
        } else if (isIE11) {
            return 11; //IE11  
        } else {
            return -1;//不是ie浏览器
        }
    })();

    //默认换行内容
    var defaultContent;
    if (ieVersion === 9 || ieVersion === 10) {
        defaultContent = '<p></p>';
    } else {
        defaultContent = '<p><br></p>';
    }

    //添加style样式
    setTimeout(function () {
        var styleList = {
            '.easyEditor': [
                'text-align: left',
                '-webkit-user-select: auto',
                '-moz-user-select: auto',
                '-ms-user-select: auto',
                '-o-user-select: auto',
                'user-select: auto',
                'overflow-y: auto',
                'word-break: break-all',
                'word-wrap: break-word',
            ],
            '.easyEditor img': [
                '-webkit-user-select: none',
                '-moz-user-select: none',
                '-ms-user-select: none',
                '-o-user-select: none',
                'user-select: none',
                'cursor: default',
                'resize: none',
                'vertical-align: middle',
            ],
            '.easyEditor input': [
                'text-align: center',
                'white-space: nowrap',
                'overflow: hidden',
                'border:0px',
                'outline:0px',
                'background-color:transparent',
                '-webkit-user-select: none',
                '-moz-user-select: none',
                '-ms-user-select: none',
                '-o-user-select: none',
                'user-select: none',
                'cursor: default',
                'resize: none',
            ],
            '.easyEditor[contentEditable=true]:not(:focus):before': [
                'color:#aaa',
                'content:attr(placeholder)',
            ]
        };
        var styleHtml = '';
        for (var i in styleList) {
            styleHtml += i + '{'
            for (var j = 0; j < styleList[i].length; j++) {
                styleHtml += styleList[i][j] + ';'
            }
            styleHtml += '}'
        }
        var docStyle = document.getElementById('easyEditor-style');
        if (docStyle == null) {
            var style = document.createElement('style');
            style.id = 'easyEditor-style';
            style.type = 'text/css';
            style.innerHTML = styleHtml;
            document.getElementsByTagName('head')[0].appendChild(style);
            style = null;
        } else {
            docStyle.innerHTML = styleHtml;
        }
    }, 1);

    //解绑事件
    var removeEvent = function (_ele, eType, bol) {
        if (!_ele.editEvent) return false;
        var handleType = eType.split('.')[0];
        var handleName = eType.split('.')[1] || 'all';
        if (!_ele.editEvent[handleName + handleType]) return false;
        var handle = _ele.editEvent[handleName + handleType];
        if (_ele.addEventListener) {
            bol = bol == undefined ? false : bol;
            _ele.removeEventListener(handleType, handle, bol);
        } else if (_ele.attachEvent) {
            _ele.detachEvent("on" + handleType, handle);
        } else {
            _ele["on" + handleType] = null;
        }
    }

    //绑定事件
    var addEvent = function (_ele, eType, handle, bol) {
        if (!_ele.editEvent) {
            _ele.editEvent = new Object;
        }
        var handleType = eType.split('.')[0];
        var handleName = eType.split('.')[1] || 'all';
        if (!handleType) return false;
        if (_ele.editEvent[handleName + handleType] != undefined) {
            removeEvent(_ele, eType);
        }
        _ele.editEvent[handleName + handleType] = handle;
        if (_ele.addEventListener) {
            bol = bol == undefined ? false : bol;
            _ele.addEventListener(handleType, handle, bol);
        } else if (_ele.attachEvent) {
            _ele.attachEvent("on" + handleType, handle);
        } else {
            _ele["on" + handleType] = handle;
        }
    }

    //添加class
    var addClass = function (_ele, className) {
        var oldClass = _ele.getAttribute('class');
        var classList = (_ele.getAttribute('class') || '').split(' ');
        classList.push(className);
        _ele.setAttribute('class', classList.join(' '));
    }

    //获取文档内容的位置情况
    var getRect = function (_ele) {
        var rect = _ele.getBoundingClientRect();
        var _left = document.documentElement.clientLeft;
        var _top = document.documentElement.clientTop;
        return {
            left: rect.left - _left,
            top: rect.top - _top,
            right: rect.right - _left,
            bottom: rect.bottom - _top,
            width: rect.right - rect.left,
            height: rect.bottom - rect.top
        }
    }

    //删除节点
    var removeElement = function (_ele) {
        var _parentElement = _ele.parentNode;
        if (_parentElement) {
            _parentElement.removeChild(_ele);
        }
    }

    var insertAfter = function(newEl, targetEl) {
        var parentEl = targetEl.parentNode;
        if (parentEl.lastChild == targetEl) {
            parentEl.appendChild(newEl);
        } else {
            parentEl.insertBefore(newEl, targetEl.nextSibling);
        }
    }

    //获取Selection对象
    var userSelection;
    if (window.getSelection) { //现代浏览器
        userSelection = window.getSelection();
    } else if (document.selection) { //IE浏览器 考虑到Opera，应该放在后面
        userSelection = document.selection.createRange();
    }

    //获取range对象
    var getRangeObject = function () {
        var rangeObject;
        rangeObject = userSelection;
        if (userSelection.getRangeAt) {
            rangeObject = userSelection.getRangeAt(0);
        }
        return rangeObject;
    }

    //恢复选区
    var setRange = function (range) {
        if (window.getSelection) {
            userSelection.removeAllRanges();
            userSelection.addRange(range);
        } else if (document.selection) {
            range.select();
        }
    }

    //过滤黏贴内容
    var filter = function () {
        var _ele = this.editbox;
        try {
            document.execCommand("AutoUrlDetect", false, false);
        } catch (e) { }
        addEvent(_ele, 'paste.filter', function (event) {
            var event = event || window.event;
            if (event.preventDefault) {
                event.preventDefault();
            } else {
                event.returnValue = false;
            }
            var textRange;
            var text = null;
            if (window.clipboardData && clipboardData.setData) {
                text = window.clipboardData.getData('text');
            } else {
                text = (event.originalEvent || event).clipboardData.getData('text/plain');
            }
            if (document.body.createTextRange) {
                if (document.selection) {
                    textRange = document.selection.createRange();
                } else if (window.getSelection) {
                    var sel = window.getSelection();
                    var range = sel.getRangeAt(0);
                    var tempEl = document.createElement("span");
                    tempEl.innerHTML = "";
                    range.deleteContents();
                    range.insertNode(tempEl);
                    textRange = document.body.createTextRange();
                    textRange.moveToElementText(tempEl);
                    tempEl.parentNode.removeChild(tempEl);
                }
                textRange.text = text;
                textRange.collapse(false);
                textRange.select();
            } else {
                document.execCommand("insertText", false, text);
            }
        });
    }

    //检测内容如果为空的话就添加<p></p>
    var restoreContent = function (editbox) {
        var html = editbox.innerHTML;
        if (html.length === 0 || html === '<br>') {
            editbox.innerHTML = defaultContent;
        }
    }

    //检查是否需要显示placeholder
    var checkPlaceholder = function () {
        var editbox = this.editbox;
        if (this.placeholderContent && this.placeholderText != '') {
            var html = editbox.innerHTML;
            if (html === defaultContent) {
                editbox.setAttribute('placeholder', this.placeholderText);
            } else {
                editbox.removeAttribute('placeholder');
            }
        }else if(!this.placeholderContent){
            editbox.removeAttribute('placeholder');
        }
    }

    //绑定各种事件
    var bindEvent = function () {
        var _this = this;
        addEvent(_this.editbox, 'click.edit', function () {
            _this.saveRange();
        });
        addEvent(_this.editbox, 'keypress.edit', function () {
            _this.saveRange();
        });
        addEvent(_this.editbox, 'keyup.edit', function (event) {
            _this.saveRange();
            var event = event || window.event;
            if (event.keyCode === 8) {
                restoreContent(_this.editbox);
            }
        });
        addEvent(_this.editbox, 'blur.edit', function () {
            checkPlaceholder.call(_this);
        })
        //不允许从外界拖东西进来，可以在里面拖动编辑器里面的内容
        _this.editbox.dragOnEdit = false;
        addEvent(_this.editbox, 'dragstart.edit', function (event) {
            _this.editbox.dragOnEdit = true;
        });
        addEvent(_this.editbox, 'dragend.edit', function (event) {
            _this.editbox.dragOnEdit = false;
        });
        addEvent(_this.editbox, 'drop.edit', function (event) {
            if (_this.editbox.dragOnEdit) {
                setTimeout(function () {
                    _this.saveRange();
                }, 1);
                _this.editbox.dragOnEdit = false;
            } else {
                var event = event || window.event;
                if (event.preventDefault) {
                    event.preventDefault();
                } else {
                    event.returnValue = false;
                }
            }
        });
        //在里面鼠标按下拖动到外面时，保存选区
        _this.editbox.mousedown = false;
        _this.editbox.isCanSave = false;
        addEvent(_this.editbox, 'mousedown.edit', function () {
            _this.editbox.mousedown = true;
        });
        addEvent(_this.editbox, 'mouseup.edit', function () {
            _this.editbox.mousedown = false;
        });
        addEvent(_this.editbox, 'mouseleave.edit', function () {
            if (_this.editbox.mousedown) {
                _this.editbox.isCanSave = true;
            } else {
                _this.editbox.isCanSave = false;
            }
        });
        addEvent(document, 'mouseup.edit', function () {
            if (_this.editbox.isCanSave) {
                _this.saveRange();
            }
            _this.editbox.mousedown = false;
            _this.editbox.isCanSave = false;
        });
    }

    //设置data
    var setData = function(_ele,data){
        if(_ele.dataset){
            for(var i in data){
                _ele.dataset[i] = data[i];
            }
        }else{
            _ele.dataset = data;
        }
    }

    //克隆节点
    var cloneNode = function (node) {
        var newNode = node.cloneNode(true);
        var newNodeEmoji = newNode.getElementsByTagName('img');
        var nodeEmoji = node.getElementsByTagName('img');
        var newNodeInput = newNode.getElementsByTagName('input');
        var nodeInput = node.getElementsByTagName('input');
        for (var i = 0; i < nodeEmoji.length; i++) {
            var dataset = JSON.parse(JSON.stringify(nodeEmoji[i].dataset));
            setData(newNodeEmoji[i],dataset);
        }
        for (var i = 0; i < nodeInput.length; i++) {
            var dataset = JSON.parse(JSON.stringify(nodeInput[i].dataset));
            setData(newNodeInput[i],dataset);
        }
        return newNode;
    }

    var EasyEditor = function (id) {
        this.editbox = document.getElementById(id);
        this.editbox.spellcheck = false; //关闭单词检查
        this.editbox.contentEditable = 'true'; //变成可编辑元素
        addClass(this.editbox, 'easyEditor'); //添加类名 

        filter.call(this); //添加过滤黏贴的内容
        bindEvent.call(this);//绑定事件
        restoreContent(this.editbox); //添加默认文本

        //聚焦
        this.focus = function () {
            this.editbox.focus();
            this.saveRange();
            return this;
        };
        //失去焦点
        this.blur = function () {
            this.editbox.blur();
            return this;
        };
        //光标定位
        this.setPosition = function (position) {
            if (position == 'start' || position == 'end') {
                var firstChild = this.editbox.firstChild;
                if (firstChild == null) {
                    this.blur().focus();
                } else {
                    var range = getRangeObject();
                    if (position == 'start') {
                        range.setStartBefore(firstChild);
                        range.setEndBefore(firstChild);
                    } else if (position == 'end') {
                        range.setStartAfter(this.editbox.lastChild);
                        range.setEndAfter(this.editbox.lastChild);
                    }
                    userSelection.removeAllRanges();
                    userSelection.addRange(range);
                    this.saveRange();
                }
            } else {
                console.error('[EasyEditor] position is not defined');
            }
            return this;
        };
        //选中所有内容
        this.selectAll = function () {
            var firstChild = this.editbox.firstChild;
            if (firstChild != null) {
                var range = getRangeObject();
                range.setStartBefore(firstChild);
                range.setEndAfter(this.editbox.lastChild);
                userSelection.removeAllRanges();
                userSelection.addRange(range);
                this.saveRange();
            } else {
                this.focus();
            }
            return this;
        };
        //删除所有内容
        this.clearAll = function () {
            this.selectAll().clearSelect();
            return this;
        };
        //删除选中内容
        this.clearSelect = function () {
            if (this.range != null) {
                this.range.deleteContents();
                this.restoreSaveRange();
                restoreContent(this.editbox);
            }
            return this;
        };
        //添加换行
        this.changeLine = function () {
            this.insertHTML('<br>');
            return this;
        };
        //添加placeholder
        this.placeholder = function (str) {
            this.placeholderContent = true;
            this.placeholderText = str || '';
            checkPlaceholder.call(this);
            return this;
        };
        //关闭placeholder
        this.closePlaceholder = function () {
            this.placeholderContent = false;
            this.placeholderText = '';
            checkPlaceholder.call(this);
            return this;
        };
        //插入表情
        this.insertEmoji = function (opts) {
            if (opts.src == undefined) {
                console.error('[EasyEditor] emoji src is not define');
                return false;
            }
            if (!opts.remark) opts.remark = '';

            this.insertHTML('<img id="easy-editor-save" src="' + opts.src + '" easy-remark="' + opts.remark + '" />');

            //存储节点信息
            var save = document.getElementById('easy-editor-save');
            if (save.dataset) {
                save.dataset.saveValue = opts.remark;
            } else {
                save.dataset = {
                    saveValue: opts.remark
                }
            }
            save.removeAttribute('id');

            if (opts.afterInsert) {
                opts.afterInsert.call(this);
            }
            return this;
        };
        //插入行块
        this.insertBlock = function (opts) {
            this.insertHTML('<br id="changeLinear"/><span id="easyEditorSaveWidth">' + opts.text + '</span>');
            var spanObj = document.getElementById('easyEditorSaveWidth');
            var width = getRect(spanObj).width;
            removeElement(spanObj);
            removeElement(document.getElementById('changeLinear'));
            opts.color = opts.color == undefined ? '' : 'color:' + opts.color + ';';

            this.insertHTML('<input id="easy-editor-save" type="text" disabled="disabled" value="' + opts.text + '" style="width:' + width + 'px;' + opts.color + '">');

            var save = document.getElementById('easy-editor-save');
            if (save.dataset) {
                save.dataset.saveValue = opts.text;
            } else {
                save.dataset = {
                    saveValue: opts.text
                }
            }
            save.removeAttribute('id');

            if (opts.afterInsert) {
                opts.afterInsert.call(this);
            }
            return this;
        };
        //获取内容
        this.getContent = function (opts) {
            var emojiSign = opts.emojiSign || '|';
			var blockSign = opts.blockSign || '|';
            var editbox = cloneNode(this.editbox);
            var emojiList = editbox.getElementsByTagName('img');
            var blockList = editbox.getElementsByTagName('input');
            var divList = editbox.getElementsByTagName('div');
            var pList = editbox.getElementsByTagName('p');
            for (var i = 0; i < emojiList.length; i++) {
                var oldNode = emojiList[i];
                var newNode = document.createTextNode(emojiSign + oldNode.dataset.saveValue + emojiSign);
                var parentNode = oldNode.parentNode;
                insertAfter(newNode, oldNode);
            }
            for (var i = 0; i < blockList.length; i++) {
                var oldNode = blockList[i];
                var newNode = document.createTextNode(blockSign + oldNode.dataset.saveValue + blockSign);
                var parentNode = oldNode.parentNode;
                insertAfter(newNode, oldNode);
            }
            for(var i=0;i<divList.length;i++){
                var oldNode = divList[i];
                var newNode = document.createElement('br');
                insertAfter(newNode, oldNode);
            }
            for(var i=0;i<pList.length;i++){
                var oldNode = pList[i];
                var newNode = document.createElement('br');
                insertAfter(newNode, oldNode);
            }
            var html = editbox.innerHTML;
            return html.replace(/<(?!\/?BR)[^<>]*>/gi,'');
        };
    }

    EasyEditor.prototype = {
        //显示的placeholder的内容
        placeholderText: '',
        //是否显示placeholder
        placeholderContent: false,
        //range对象
        range: null,
        //获取selection对象
        getSelection: function () {
            return userSelection;
        },
        //获取range对象
        getRangeObject: function () {
            return getRangeObject();
        },
        //把文档选区保存起来
        saveRange: function () {
            var range = getRangeObject();
            this.range = range;
            return this;
        },
        //插入HTML
        insertHTML: function (html) {
            if (this.range === null) {
                this.focus().saveRange();
            }
            var range = this.range;
            var oFragment = range.createContextualFragment(html);
            var oLastNode = oFragment.lastChild;
            range.deleteContents();
            range.insertNode(oFragment);
            range.setStartAfter(oLastNode);
            userSelection.removeAllRanges();
            userSelection.addRange(range);
            this.saveRange();
            return this;
        },
        //恢复保存的选区
        restoreSaveRange: function () {
            var range = this.range;
            if (range == null) {
                console.error('[EasyEditor] range is empty');
            } else {
                setRange(range);
            }
            return this;
        },
    }

    //每调用一次都实例化出一个editor对象
    window.easyEditor = function (id) {
        if (id == undefined || null) {
            console.error('[EasyEditor] editor id is not defined');
            return;
        }
        return new EasyEditor(id);
    }
})();