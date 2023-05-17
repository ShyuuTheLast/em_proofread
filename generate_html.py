import os, sys
import shutil
import math
import numpy as np
from util import mkdir, read_text, write_text

class HtmlGenerator(object):
    def __init__(
        self, output_folder, host_address=None, num_user=1, num_per_page=100, num_column=10
    ):
        # files for storage
        self.output_folder = f"{output_folder}/"
        self.saved_folder = f"{self.output_folder}/saved_%d/"
        self.test_folder = f"{self.output_folder}/test_%d/"
        self.test_file = f"{self.test_folder}/test_%d.html"
        # files for display
        self.host_address = f'{host_address}/test_%d/' if host_address is not None else self.test_folder
        self.num_user = num_user
        self.num_per_page = num_per_page
        self.num_column = num_column

    def setup(self):
        self.create_folder()
        self.copy_www()

    def create_folder(self):
        for i in range(self.num_user):
            # folder of saved results
            folder_save = self.user_folder % i
            mkdir(folder_save)
            # need to be writeable from browser
            os.chmod(folder_save, 0o777)
            # folder of test htmls
            folder_test = self.test_folder % i
            mkdir(folder_test)

    def copy_www(self):
        if not os.path.exists(f"{self.output_folder}/save_ans.php"):
            shutil.copy(
                "www/save_ans.php", f"{self.output_folder}/save_ans.php"
            )
        if not os.path.exists(f"{self.output_folder}/js/jquery-1.7.1.min.js"):
            mkdir(f"{self.output_folder}/js/")
            shutil.copy(
                "www/js/jquery-1.7.1.min.js",
                f"{self.output_folder}/js/jquery-1.7.1.min.js",
            )

    def generate_html_visualization(self, labels, image_paths, output_file):
        # image_paths: list of image lists
        out = "<html>" + """
            <style>
            .crop{position:relative;left:0;top:0;overflow:hidden;width:150px;height:150px;}
            </style>
            """ + '<script src="../js/jquery-1.7.1.min.js"></script>'
        for label, image_path in zip(labels, image_paths):
            out += f"<h1>Visualize {label} (#={len(image_path)})</h1>\n"
            out += "<table>\n"
            for index, path_list in enumerate(image_path):
                if index % self.num_column == 0:
                    out += "<tr>\n"
                out += '<td><div class="crop">'
                for path in path_list:
                    out += (
                        "<img"
                        ' style="position:relative;top:-75px;left:-75px;opacity:0.5;"'
                        f'  src="{path}">'
                    )
                out += "</div></td>\n"
                if (index + 1) % self.num_column == 0:
                    out += "</tr>\n"
            out += "</table>\n"
        out += "</html>"
        write_text(output_file, out)

    def generate_html_main(self):
        for i in range(self.num_user):
            out = """<html>
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
            """ % (i, i)
            write_text(self.test_folder % i, out)

    def generate_html_proofreading(self, image_paths):
        # random order
        color_selection = '["green","red","white"]'
        num_per_user = int(math.ceil(len(image_paths) / self.num_user))
        num_last_user = len(image_paths) - self.num_user * num_per_user
        id_start = 0
        for uid in range(self.num_user):
            total = num_per_user if uid < self.num_user else num_last_user
            num_page = int(math.ceil(total / float(self.num_per_page)))
            color0 = color_selection[
                color_selection.find('"') + 1 : color_selection.find(",") - 1
            ]
            for fid in range(num_page):
                output_file = self.test_file % (uid, fid)
                out = "<html>" + "<style>"
                out += """
                .im0{position:absolute;top:-75px;left:-75px;}
                .im1{position:relative;top:-%spx;left:-%spx;opacity:0.7;}
                .im2{position:absolute;top:-75px;left:-75px;opacity:0.3;}
                .crop{position:relative;left:0;top:0;overflow:hidden;width:150px;height:150px;}
                """ % (75, 75)
                out += "</style>"
                out += (
                    '<script src="../../../js/jquery-1.7.1.min.js"></script>'
                )
                out += "<h1> Synapse color coding</h1>"
                out += "<ul>"
                out += f"<li>{color_selection[0]}=yes</li>"
                out += f"<li>{color_selection[1]}=no</li>"
                out += f"<li>{color_selection[2]}=not sure</li>"
                out += "</ul>"
                # display
                out += "<table cellpadding=8 border=2>"
                id_end = = min(start_id + self.num_per_page, total)
                for i in range(id_start, id_end):
                    i_rel = i - id_start
                    if (i_rel % self.num_column == 0:
                        out += "<tr>"
                    out += (
                        f'<td id="t{i_rel}" class="cc"'
                        f' bgcolor="{color0}">'
                    )
                    for image_path in image_paths[i]:
                        if isinstance(image_path, list):
                            # overlay display
                            out += '<div class="crop" >'
                            out += f'<img class="im1" src="{image_path[0]}">'
                            out += f'<img class="im2" src="{image_path[1]}">'
                            out += "</div>"
                        else:
                            out += '<div class="crop">'
                            out += f'<img class="im0" src="{image_path}">'
                            out += "</div>"
                    out += "</td>"
                    if (i_rel + 1) % self.num_column == 0:
                        out += "</tr>"
                out += "</table>\n"
                # submission
                out += "<table border=2>\n"
                out += (
                    '<tr><td colspan=2><button id="sub"'
                    ' style="width:100%;height=40">Done</button></td>\n'
                )
                out += "</table>\n"
                out += (
                    """
                    <form id="mturk_form" method="POST" style="display:none">
                        <input id="task" name="task" value="saved_"""
                    + str(uid)
                    + """/s_">
                        <input id="ans" name="ans">
                        <input id="fileId" name="fileId" value="%d">
                    </form>
                    """ % (fid)
                )
                # js
                out += "<script>"
                out += (
                    f"TOTAL_I={id_end - id_start};"
                    + f"colors={color_selection};"
                    + """;
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
                        window.location='
                    """
                    + f"{self.host_address % fid}?st={pid}';"
                    + """
                    });
                });
                """
                )
                out += "</script>"
                out += "</html>"
                write_txt(output_file, out)
