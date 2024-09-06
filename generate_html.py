import os, sys
import shutil
import math
import numpy as np
from util import mkdir, read_txt, write_txt

COLORS = [
    "red",
    "green",
    "black",
    "white",
    "yellow",
    "gray",
    "maroon",
    "purple",
    "fushsia",
    "lime",
    "olive",
    "silver",
    "navy",
    "blue",
    "teal",
    "aqua",
]


class HtmlGenerator(object):
    def __init__(
        self,
        output_folder,
        host_address=None,
        num_user=1,
        num_per_page=100,
        num_column=10,
    ):
        # files for storage
        self.output_folder = output_folder
        self.saved_folder = os.path.join(output_folder, "saved_%d")
        self.test_folder = os.path.join(output_folder, "test_%d")
        self.test_file = os.path.join(self.test_folder, "test_%d.html")
        self.js_folder = os.path.join(output_folder, "js")

        # files for display
        self.use_php = host_address is not None
        self.host_address = (
            os.path.join(host_address, "test_%d")
            if host_address is not None
            else self.test_folder
        )
        self.num_user = num_user
        self.num_per_page = num_per_page
        self.num_column = num_column

        # will be computed by the input
        self.num_per_user = 0
        self.num_last_user = 0

        self.setup_www()
        self.setup_users()

    def setup_www(self):
        if self.use_php:
            php_file = os.path.join(self.output_folder, "save_ans.php")
            if not os.path.exists(php_file):
                shutil.copy(os.path.join("www", "save_ans.php"), php_file)

        mkdir(self.js_folder)
        for fn in ["jquery-1.7.1.min.js", "util.js"]:
            js_file = os.path.join(self.js_folder, fn)
            if not os.path.exists(js_file):
                shutil.copy(
                    os.path.join("www", "js", fn),
                    js_file,
                )

    def setup_users(self):
        for i in range(self.num_user):
            # folder of saved results
            folder_save = self.saved_folder % i
            mkdir(folder_save)
            # need to be writeable from browser
            os.chmod(folder_save, 0o777)
            # folder of test htmls
            folder_test = self.test_folder % i
            mkdir(folder_test)

    def create_html(self, image_paths, image_labels, color_labels):
        self.num_per_user = int(math.ceil(len(image_paths) / self.num_user))
        self.num_last_user = len(image_paths) - (self.num_user - 1) * self.num_per_user
        self.create_html_index()
        self.create_html_proofreading(
            image_paths, image_labels, color_labels, self.use_php
        )

    def create_html_index(self):
        # if on server, index.html can automatically present the tasks to work on
        # if on client, js can't check file existence
        if self.use_php:
            save_pref = "saved_%d/s_" if self.use_php else "saved_%d_"
            for i in range(self.num_user):
                num_images = (
                    self.num_per_user if i != self.num_user - 1 else self.num_last_user
                )
                num_pages = (num_images + self.num_per_page - 1) // self.num_per_page
                out = """
                <html>
                    <head>
                        <script src="js/jquery-1.7.1.min.js"></script>
                        <script src="js/util.js"></script>
                    </head>
                    <body>
                        <h1 id="tt"></h1>
                        <script>
                        var st=parseInt(getUrlParam('st'));if(isNaN(st)){st=0;}
                            var num = %d;
                            function check_file(fileID){
                                if(fileID >= num){
                                    $('#tt').text("Congratulations! Mission Completed!!"); 
                                }else{
                                    $.get('saved_%d/%s'+fileID+'.txt').done(function(){
                                            check_file(fileID+1)
                                        }).fail(function(){
                                            window.location = 'test_%d/test_'+fileID+'.html'
                                        })
                                    }
                            }
                            check_file(st)
                        </script>
                    </body>
                </html>
                """ % (
                    num_pages,
                    i,
                    save_pref % i,
                    i,
                )
                write_txt(os.path.join(self.output_folder, f"index_{i}.html"), out)

    def create_html_proofreading(
        self, image_paths, image_labels=None, color_labels=None, use_php=False
    ):
        if image_labels is None:
            image_labels = np.zeros(len(image_paths))
        if color_labels is None:
            color_labels = ["undefined"]

        colors = COLORS[: len(color_labels)]
        color_js = '["' + '","'.join(colors) + '"]'

        for uid in range(self.num_user):
            num_images = (
                self.num_per_user if uid != self.num_user - 1 else self.num_last_user
            )
            id_start = self.num_per_user * uid
            id_end = id_start + num_images
            num_pages = (num_images + self.num_per_page - 1) // self.num_per_page
            for fid in range(num_pages):
                output_file = self.test_file % (uid, fid)
                out = "<html>"
                out += """
                <style>
                .im0{position:absolute;top:0px;left:0px;height:100%;}
                .im1{position:relative;top:-75px;left:-75px;opacity:0.7;}
                .im2{position:absolute;top:-75px;left:-75px;opacity:0.3;}
                .crop{position:relative;left:0;top:0;overflow:hidden;width:150px;height:150px;}
                </style>
                """
                # color scheme
                out += f"""
                <script src="../js/jquery-1.7.1.min.js"></script>
                <h1> User {uid}, page {fid}/{num_pages}</h1>
                <h3> color coding</h3>
                <ul>"""
                for i, color_name in enumerate(color_labels):
                    out += f"<li>{colors[i]}: {color_name}</li>\n"
                out += "</ul>\n"
                # display
                out += "<table cellpadding=8 border=2>\n"
                id_start_f = id_start + fid * self.num_per_page
                id_end_f = min(id_start_f + self.num_per_page, id_end)
                for i in range(id_start_f, id_end_f):
                    i_rel = i - id_start_f
                    if (i_rel % self.num_column) == 0:
                        out += "\t <tr>\n"
                    out += (
                        f'\t\t<td id="t{i_rel}" class="cc"'
                        f' bgcolor="{colors[image_labels[i]]}">\n'
                    )
                    for image_path in image_paths[i]:
                        if isinstance(image_path, list):
                            # overlay display
                            out += f"""
                                <div class="crop" >
                                    <img class="im1" src="{image_path[0]}">
                                    <img class="im2" src="{image_path[1]}">
                                </div>
                                """
                        else:
                            out += f"""
                                <div class="crop">
                                    <img class="im0" src="{image_path}">
                                </div>
                                """
                    out += "</td>\n"
                    if (i_rel + 1) % self.num_column == 0:
                        out += "</tr>\n"
                out += "</table>\n"
                # submission
                out += """<table border=2>
                    <tr>
                        <td>
                            <button id="sub" style="width:100%;height=40">Done</button>
                        </td>
                        <td>
                            <button id="next" style="width:100%;height=40">Next</button>
                        </td>
                    </tr>
                    </table>
                    """
                if use_php:
                    out += f"""
                    <form id="mturk_form" method="POST" style="display:none">
                        <input id="task" name="task" value="saved_{uid}/s_">
                        <input id="ans" name="ans">
                        <input id="fileId" name="fileId" value="{fid}">
                    </form>
                    """

                # js
                out += f"""
                    <script>
                        TOTAL_I={id_end_f - id_start_f};
                        colors={color_js};
                    """
                out += """
                function get_answer() {
                    var out='';
                    var cc='';
                    for(var i=0;i<TOTAL_I;i++){
                        cc = $("#t"+i)[0].style.backgroundColor
                        out += Math.max(0, colors.indexOf(cc))
                        if(i < TOTAL_I-1){
                            out += ',';                        
                        }
                    }
                    return out
                }
                $(".cc").click(function(){
                    // next color
                    if($(this)[0].style.backgroundColor == ""){
                        $(this)[0].style.backgroundColor = colors[1 % colors.length]; 
                    } else {
                        $(this)[0].style.backgroundColor = colors[(colors.indexOf($(this)[0].style.backgroundColor) + 1) % colors.length]
                    }
                });
                """
                out += """
                $("#next").click(function(){
                    window.location = 'test_%d/test_%d.html'
                });
                """ % (
                    uid,
                    fid + 1,
                )
                if use_php:
                    # write files on the server
                    out += """
                    $("#sub").click(function(){
                        ans_out=get_answer();
                        document.getElementById("ans").value = ans_out;
                        tmp = $.post("../save_ans.php", $("#mturk_form").serialize(),function(data) {
                            window.location='%s?st=%d';                    
                        });
                    });
                    """ % (
                        self.host_address % uid,
                        fid,
                    )
                else:
                    # write files with browser
                    out += """
                    $("#sub").click(function(){                        
                        const link = document.createElement("a");
                        const content = get_answer();
                        const file = new Blob([content], { type: 'text/plain' });
                        link.href = URL.createObjectURL(file);
                        link.download = "saved_%d_%d.txt";
                        link.click();
                        URL.revokeObjectURL(link.href);
                    });
                    """ % (
                        uid,
                        fid,
                    )

                out += "</script>\n</html>"
                write_txt(output_file, out)

    def create_html_summary(self, labels, image_paths, output_file):
        # image_paths: list of image lists
        out = (
            "<html>"
            + """
            <style>
            .crop{position:relative;left:0;top:0;overflow:hidden;width:150px;height:150px;}
            </style>
            """
            + '<script src="../js/jquery-1.7.1.min.js"></script>'
        )
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
        write_txt(output_file, out)
