import os,sys
import shutil
import math
import numpy as np

from util import mkdir,readtxt,writetxt

D0='../../data/'
Do='/var/www/html/donglai/jwr-syn/pf_syn_jwr_dh/'
numU=20 # user
# page per user (21): 1 instr + 20 test

class HtmlGenerator(object):
    def __init__(self, output_folder):
        self.output_folder = output_folder + '/'

    def setup(self):
        self.createFolder()
        self.copyWww()

    def createFolder(self):
        for i in range(self.num_user):
            # folder of saved results
            folder_save = self.output_folder + 'saved_%d/'%(i)
            mkdir(folder_save)
            # need to be writeable from browser
            os.chmod(folder_save, 0o777)
            # folder of test htmls
            folder_test = self.output_folder + 'test_%d/'%(i)
            mkdir(folder_test)

    def copyWww(self):
        if not os.path.exists(self.output_folder + 'save_ans.php'):
            shutil.copy('www/save_ans.php', self.output_folder + 'save_ans.php')
        if not os.path.exists(self.output_folder + 'js/jquery-1.7.1.min.js'):
            mkdir(self.output_folder + 'js/')
            shutil.copy('www/js/jquery-1.7.1.min.js', self.output_folder + 'js/jquery-1.7.1.min.js')

    elif opt=='0.1':# visualize all g/b result
        # no need for this 
        D1='/mnt/coxfs01/donglai/ppl/zudi/jwr/syn_test_0904_wdj/para/in300_pp50/50um_pf/'
        fn = readtxt(D1+'r2k_fn.txt')
        txt = np.loadtxt(D1+'r2k_gbr.txt').astype(int)

        numC=10
        out = '<html>'
        out +="""
            <style>
            .crop{position:relative;left:0;top:0;overflow:hidden;width:150px;height:150px;}
            </style>
        """
        out += '<script src="../js/jquery-1.7.1.min.js"></script>'
        nn=['good','bad']
        for k in range(2):
            ind = np.where(txt==k)[0]
            out += '<h1>Proofread %s (#=%d)</h1>\n'%(nn[k],len(ind))
            out += '<table>\n'
            for i in range(len(ind)):
                if i % numC ==0:
                    out+='<tr>\n'
                out += '<td><div class="crop">'
                out += '<img style="position:relative;top:-75px;left:-75px;opacity:0.5;"  src="'+D0+fn[ind[i]][:-1]+'_im.png">'
                out += '<img style="position:absolute;top:-75px;left:-75px;opacity:0.5;"  src="'+D0+fn[ind[i]][:-1]+'_syn.png">'
                out+='</div></td>\n'
                if (i+1) % numC ==0:
                    out+='</tr>\n'
            out+='</table>\n'
        out+='</html>'
        writetxt(Do+'test_all/all.htm',out)
    elif opt =='0.2': # generate index htm
        for i in range(numU):
            out="""<html>
                    <head>
                    <script src="js/jquery-1.7.1.min.js"></script>
                    <script src="js/util.js"></script>
                    </head>
                    <body>
                    <h1 id="tt"></h1>
                <script>
                var st=parseInt(getUrlParam('st'));if(isNaN(st)){st=0;}
                    var num=20;
                    function check_file(fileID){
                       if(fileID>=num){
                            $('#tt').text("Congratulations! Mission Completed!!"); 
                    }else{
                       $.get('saved_%d/s__'+fileID+'.save').done(function(){
                            check_file(fileID+1)
                         }).fail(function(){
                            window.location = 'test_%d/test_'+fileID+'.htm'
                         })
                    }
                    }
                    check_file(st)
                </script>
            </body></html>
            """%(i,i)
            writetxt(Do+'index_%d.htm'%(i),out)
    elif opt =='0.21': # generate cluster gt
        D1='/mnt/coxfs01/donglai/ppl/zudi/jwr/syn_test_0904_wdj/para/in300_pp50/50um_pf/'
        gbr = np.loadtxt(D1+'r2k_gbr.txt').astype(int)
        cid = np.loadtxt(D1+'r2k_cid.txt').astype(int)
        uid = np.unique(cid)
        ind = []
        for i in uid:
            ind += list(gbr[np.where(cid==i)[0]])
        np.savetxt('./r2k_gbr_clustered.txt',ind,fmt='%d')
 
    elif opt =='0.3': # generate test htm
        # random order 
        dopt=int(sys.argv[2]) # random or clustered
        bcolor='["green","red","white"]';
        D1='/mnt/coxfs01/donglai/ppl/zudi/jwr/syn_test_0904_wdj/para/in300_pp50/50um_pf/'
        if dopt == 0: # random good or bad
            ran=range(10)
            ind=range(2100)
        elif dopt == 1:
            ran=range(10,20)
            cid = np.loadtxt(D1+'r2k_cid.txt').astype(int)
            uid = np.unique(cid)
            ind = []
            for i in uid:
                ind += list(np.where(cid==i)[0])
        fn = readtxt(D1+'r2k_fn.txt')
        num=100;
        numC=10
        D0='../../data/'
        f1=''
        def getImName(im_id):
            return D0+f1+fn[im_id][:-1]+'_im.png'
        def getSynName(im_id):
            return D0+f1+fn[im_id][:-1]+'_syn.png'
        
        total = len(ind);
        numP = int(math.ceil(total/float(num)))
        print(dopt,numP)
        bcolor0=bcolor[bcolor.find('"')+1:bcolor.find(',')-1]
        for fid in ran:
            Doo =Do+'test_%d/'%(fid);
            for pid in range(numP):
                out='<html>'
                out+='<style>'
                out+="""
                .im0{position:absolute;top:-75px;left:-75px;}
                .im1{position:relative;top:-%spx;left:-%spx;opacity:0.7;}
                .im2{position:absolute;top:-75px;left:-75px;opacity:0.3;}
                .crop{position:relative;left:0;top:0;overflow:hidden;width:150px;height:150px;}
                """%(75,75)
                out+='</style>'
                out+='<script src="../../../js/jquery-1.7.1.min.js"></script>'
                out+='<h1> Synapse color coding</h1>'
                out+='<ul>'
                out+='<li>green=yes</li>'
                out+='<li>red=no</li>'
                out+='<li>white=not sure</li>'
                out+='</ul>'
                out+="<table cellpadding=8 border=2>"
                pid2 = min((pid+1)*num,total)
                for i in range(pid*num,pid2):
                    if i%numC == 0:
                        out+='<tr>'
                    out+='<td id="t'+str(i-pid*num)+'" class="cc" bgcolor="'+bcolor0+'">'
                    out+='<div class="crop">'
                    out+='<img class="im0" src="'+getImName(ind[i])+'">'
                    out+='</div><br>'
                    out+='<div class="crop" >'
                    out+='<img class="im1" src="'+getSynName(ind[i])+'">'
                    out+='<img class="im2" src="'+getImName(ind[i])+'">'
                    out+='</div>'
                    out+='</td>'
                    if (i+1)%numC == 0:
                        out+='</tr>'
                out+="</table>\n"
                out+="<table border=2>\n"
                out+='<tr><td colspan=2><button id="sub" style="width:100%;height=40">Done</button></td>\n'
                out+="</table>\n"
                out+="""
                      <form id="mturk_form" method="POST" style="display:none">
                         <input id="task" name="task" value="saved_"""+str(fid)+"""/s_">
                         <input id="ans" name="ans">
                         <input id="fileId" name="fileId" value="%d">
                     </form>
                    """%(pid)
                # js
                out+='<script>'
                out+="""
                  TOTAL_I="""+str(pid2-pid*num)+""";
                  colors="""+bcolor+""";
                  function get_answer() {
                    var out='';
                    for(var i=0;i<TOTAL_I;i++){
                        var cc=$("#t"+i)[0].style.backgroundColor
                        if(cc==""|| cc==colors[0]){
                            out+='0,';
                        }else if(cc==colors[1]){
                            out+='1,';
                        }else{
                            out+='2,';
                        }
                    }
                    return out
                  }
                  $(".cc").click(function(){
                        if($(this)[0].style.backgroundColor=="" || $(this)[0].style.backgroundColor==colors[0]){
                            $(this)[0].style.backgroundColor=colors[1];
                        }else if($(this)[0].style.backgroundColor==colors[1]){
                            $(this)[0].style.backgroundColor=colors[2];
                        }else{
                            $(this)[0].style.backgroundColor=colors[0];
                        }
                  });
                  $("#sub").click(function(){
                      ans_out=get_answer();
                      // local version
                      // $('#dw').attr("href","data:text;charset=utf-8,"+encodeURIComponent(ans_out));
                      // $('#dw').css("display", "block");
                      document.getElementById("ans").value = ans_out;
                      tmp = $.post("../save_ans.php", $("#mturk_form").serialize(),function(data) {
                         window.location='http://140.247.107.75/donglai/jwr-syn/pf_syn_jwr_dh/index_"""+str(fid)+""".htm?st="""+str(pid)+"""';
                       });

                  });
                """
                out+='</script>'
                out+='<html>'
                a=open(Doo+'test_%d.htm'%(pid),'w')
                a.write(out)
                a.close()
