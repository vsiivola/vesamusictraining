/*globals Translator, lang, document, $*/

var rt = new Translator("resultpage", lang),
    result_context;


function ResultScreen(mainWindow) {
    "use strict";
    this.mainWindow = mainWindow;
    result_context = this;

    this.get_server_info = function () {
        result_context = this;
        $("span").removeClass("ui-icon-circle-check");
        $("span").removeClass("ui-icon-circle-close");
        $("span.checkremove").css("opacity", "0.0");

        $("div#main").slideUp("slow", function () {
            result_context.get_server_info2.apply(result_context);
        });
    };

    this.get_server_info2 = function (foo, bar) { // not really getting any info nowsen
        $("#maintitle").html(rt.tp("Music Training | Results"));
        var mdiv = $("div#main");
        mdiv.html('<div class="results ui-corner-all">' +
                  result_context.mainWindow.correct_clicks +
                  " / " + result_context.mainWindow.num_exercises + "</div>");

        $.get(result_context.mainWindow.course_name + '/complete/', {
            'num_correct': JSON.stringify(result_context.mainWindow.correct_clicks)
        },
              function () {
                var obj = document.createElement("input");
                obj.type = "button";
                obj.value = rt.tp("Continue");
                obj.className = "ui-button-text";
                obj.onclick = function () {
                    result_context.mainWindow.course_name = null;
                    result_context.mainWindow.exercise_index = 0;
                    result_context.mainWindow.show.apply(result_context.mainWindow);
                };
                mdiv.append(obj);
                $("div#main").slideDown("slow");
            });
    };
}
