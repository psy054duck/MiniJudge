code = document.getElementById('code_area');

code.addEventListener('keydown', function(e) {
    if(e.keyCode===9){
        var position=this.selectionStart+4;//此处我用了两个空格表示缩进，其实无所谓几个，只要和下面保持一致就好了。
        this.value=this.value.substr(0,this.selectionStart)+'    '+this.value.substr(this.selectionStart);
        this.selectionStart=position;
        this.selectionEnd=position;
        this.focus();
        e.preventDefault();
      }
}, false);