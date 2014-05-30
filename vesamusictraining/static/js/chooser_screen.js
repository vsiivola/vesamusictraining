/*jslint
  browser: true,
  continue: true
*/
/*globals Translator, lang, $*/

var ct = new Translator("chooserpage", lang),
    chooser_screen_context;

function ChooserScreen(mainWindow) {
    "use strict";
    this.mainWindow = mainWindow;
    this.course_list =  [];

    this.render_full = function () {
        $("#maintitle").html(ct.tp("Music Training | Choose your exercise"));

        var clist = this.course_list.lectures,
            tstring = '<div id="courses" class="row">',
            lclist,
            i,
            j,
            lecture,
            myDiv,
            obj;

        lclist = [];
        j = 0;
        for (i = 0; i < clist.length; i += 1) {
            lecture = clist[i];
            if (lecture.language !== lang) {
                continue;
            }
            lclist.push(lecture);
            tstring += '<div id="acc' + j + '" class="col-xs-4 col-lecture';
            if (lecture.complete) {
                tstring += ' inactive-lecture';
            }
            tstring += '"><h2 class="lecture-title">' + lecture.title + '</h2>';
            if (lecture.instructions) {
                tstring += '<H3>' + ct.tp("Hints") + '</H3><p>' + lecture.instructions + '</p>';
            }

            if (lecture.outside_info_name) {
                tstring += '<H3>' + ct.tp("More information") +
                    '</H3>' + '<a class="outside" href="' +
                    lecture.outside_info_link +
                    '"> ' + lecture.outside_info_name + "</a>";
            }

            tstring += '<H3>' + ct.tp("Exercise information") + '</H3>';
            tstring += '<ul class="lecture_info">';
            tstring += '<li> version ' +  lecture.version + '</li>';
            tstring += '<li> ' +  lecture.num_exercises + ' ' + ct.tp("exercises") + '</li>';
            if (lecture.complete) {
                tstring += '<li>' + ct.tp("completed") + '<ul>';
                tstring += '<li>' + ct.tp("version") + ' ' + lecture.version + '</li>';
                tstring += '<li>' + ct.tp("score") + ' ' + lecture.score + '</li>';
                tstring += '<li>' + ct.tp("on") + ' ' + lecture.complete_date + "</li></ul>";
            }
            tstring += '</ul>';
            tstring += '</div>';
            j += 1;
            if (j % 3 === 0) {
                tstring += '</div><div class="row">';
            }
        }
        tstring += "</div>";
        $("div#main").html(tstring);

        function set_obj_onclick() {
            chooser_screen_context.mainWindow.course_name = this.name;
            chooser_screen_context.mainWindow.exercise_index = 0;
            chooser_screen_context.mainWindow.show.apply(chooser_screen_context.mainWindow);
        }

        for (i = 0; i < lclist.length; i += 1) {
            myDiv = document.getElementById("acc" + i);
            obj = document.createElement("input");
            obj.type = "button";
            obj.id = "btn" + i;
            obj.name = lclist[i].title;
            obj.value = ct.tp("Enter") + $('<div/>').html(" &raquo;").text();
            obj.className = "btn btn-lg btn-primary btn-block";
            obj.onclick = set_obj_onclick;
            myDiv.appendChild(obj);
        }

        $("#courses").accordion();
    };

    this.res = function (response) {
        this.course_list = JSON.parse(response);
        this.render_full();
    };

    this.get_server_info = function (foo, bar) {
        chooser_screen_context = this; //preserve context for callback
        $.get(
            '/exercise/list_lectures/',
            null,
            function (response) {
                chooser_screen_context.res.apply(chooser_screen_context, arguments);
            }
        );
    };
}
